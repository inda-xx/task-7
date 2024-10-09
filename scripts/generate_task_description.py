import os
import sys
import subprocess
from datetime import datetime
import pytz
from pytz import timezone

# Import the OpenAI client
from openai import OpenAI

def main(api_key):
    if not api_key:
        print("Error: OpenAI API key is missing.")
        sys.exit(1)

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    # Extract theme and language from environment variables
    theme = os.getenv("TASK_THEME", "Create a basic Java application with the following requirements.")
    language = os.getenv("TASK_LANGUAGE", "English")

    # Extract learning goals
    learning_goals = """
    * Understanding the Java `Random` object
    * Understanding the [ternary operator]
    * Know the difference between a deep and a shallow copy
    * Finding and fixing bugs
    * Using an Iterator to modify a collection during iteration
    * **Optional**: Using inheritance to avoid code duplication 
    """

    # Read the original task from file
    original_task_path = os.path.join("tasks", "original_task.md")
    if not os.path.exists(original_task_path):
        print(f"Error: Original task file not found at {original_task_path}")
        sys.exit(1)
    with open(original_task_path, "r") as f:
        original_task_content = f.read()

    # Split the original task into chunks per exercise
    exercise_chunks = split_task_into_exercises(original_task_content)

    # Build the messages for the OpenAI API
    messages = [
        {
            "role": "system",
            "content": (
                "You are an experienced programming instructor creating detailed tasks for university-level students. "
                "The tasks should be challenging, pedagogically valuable, and should include detailed descriptions with code snippets where necessary."
            )
        },
        {
            "role": "user",
            "content": (
                f"Create a new programming task in {language} with the following theme:\n\n"
                f"**Theme**: {theme}\n\n"
                f"The task must include and integrate the following learning goals:\n{learning_goals}\n\n"
                "The task should include at least six exercises that gradually increase in difficulty. Each exercise should be well-detailed and include code snippets where necessary.\n\n"
                "- **Exercises 1 & 2**: Focus on theoretical aspects of the learning goals. Challenge students' understanding through conceptual questions and explanations without requiring coding.\n\n"
                "- **Exercises 3 & 4**: Focus on combining and integrating the concepts into coding. Require students to write code that applies the concepts in practical scenarios.\n\n"
                "- **Exercises 5 & 6**: Are challenging coding tasks that require significant learning and coding effort to complete. These should be step-by-step tasks that build upon previous exercises.\n\n"
                "Use the following exercises from the original task as inspiration for each exercise in the new task. Adapt them to fit the new theme and ensure they cover the learning goals.\n\n"
            )
        }
    ]

    # Add each exercise chunk as a separate message
    for i, chunk in enumerate(exercise_chunks):
        messages.append({
            "role": "assistant",
            "content": (
                f"Here is exercise {i+1} from the original task for inspiration:\n\n{chunk}\n\n"
                "Please adapt this exercise to fit the new theme and include it in the new task."
            )
        })

    messages.append({
        "role": "user",
        "content": (
            "Please provide the complete new task description, including all exercises, instructions, and any necessary details. "
            "Include titles, subtitles, and emojis for aesthetics to make the description detailed, well-structured, and engaging. "
            "Ensure the task is challenging and pedagogically valuable, following the structure specified."
        )
    })

    # Call OpenAI API to generate the task description
    response_content = generate_with_retries(client, messages, max_retries=3)
    if response_content is None:
        print("Error: Failed to generate task description after multiple retries.")
        sys.exit(1)

    # Create a new branch with a unique name
    stockholm_tz = timezone('Europe/Stockholm')
    branch_name = f"task-{datetime.now(stockholm_tz).strftime('%Y%m%d%H%M')}"
    create_branch(branch_name)

    # Write the response content to a markdown file
    task_file_path = os.path.join("tasks", "new_task.md")
    with open(task_file_path, "w") as file:
        file.write(response_content)

    # Commit and push changes
    commit_and_push_changes(branch_name, task_file_path)

    # Output the branch name for the next job
    print(f"::set-output name=branch_name::{branch_name}")

def split_task_into_exercises(task_content):
    # This function splits the task content into separate exercises
    # For simplicity, let's assume that each exercise starts with '#### Exercise'
    exercises = []
    lines = task_content.split('\n')
    current_exercise = []
    in_exercise = False
    for line in lines:
        if line.strip().startswith('#### Exercise'):
            if current_exercise:
                exercises.append('\n'.join(current_exercise))
                current_exercise = []
            in_exercise = True
        if in_exercise:
            current_exercise.append(line)
    if current_exercise:
        exercises.append('\n'.join(current_exercise))
    return exercises

def generate_with_retries(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating task description: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
    return None

def create_branch(branch_name):
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            check=True,
            env=dict(os.environ, GIT_ASKPASS='echo', GIT_USERNAME='x-access-token', GIT_PASSWORD=os.getenv('GITHUB_TOKEN'))
        )
    except subprocess.CalledProcessError as e:
        print(f"Error creating branch: {e}")
        sys.exit(1)

def commit_and_push_changes(branch_name, task_file_path):
    try:
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)

        subprocess.run(["git", "add", task_file_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Add new task description: {branch_name}"], check=True)
        subprocess.run(
            ["git", "push", "--set-upstream", "origin", branch_name],
            check=True,
            env=dict(os.environ, GIT_ASKPASS='echo', GIT_USERNAME='x-access-token', GIT_PASSWORD=os.getenv('GITHUB_TOKEN'))
        )
    except subprocess.CalledProcessError as e:
        print(f"Error committing and pushing changes: {e}")
        sys.exit(1)

if len(sys.argv) != 2:
    print("Error: Missing required command line argument 'api_key'")
    sys.exit(1)

api_key = sys.argv[1]

main(api_key)
