public class Arrays {
  public static int average(int[] array) {
    int sum = 0;

    for (int i : array) {
      sum += i;
    }

    return sum / array.length;
  }

  public static double average(double[] array) {
    double sum = 0;

    for (double i : array) {
      sum += i;
    }

    return sum / array.length;
  }

  public static int smallestElement(int[] array) {
    if (array.length == 0) {
      return Integer.MAX_VALUE;
    }

    int smallestEl = array[0];

    for (int i = 1; i < array.length; i++) {
      if (array[i] < smallestEl) {
        smallestEl = array[i];
      }
    }

    return smallestEl;
  }

  public static int[] reverse(int[] array) {
    int[] reverseArray = new int[array.length];
    int j = 0;

    for (int i = array.length - 1; i >= 0; i--) {
      reverseArray[j] = array[i];
      j++;
    }

    return reverseArray;
  }

  public static void main(String[] args) {
    int[] intArray = { 1, 2, 3, 4 };
    double[] doubleArray = { 1.0, 2.0, 3.0, 4.0 };
    int[] array = { 31, 6, 8, 12, 20, 25, 23, 10 };
    int[] emptyArray = {};
    int[] reversed = Arrays.reverse(intArray);

    System.out.println("---------------avgInt-------------");
    System.out.println(Arrays.average(intArray));

    System.out.println("---------------avgDouble-------------");
    System.out.println(Arrays.average(doubleArray));

    System.out.println("---------------smallestElement-------------");
    System.out.println(Arrays.smallestElement(array));
    System.out.println(Arrays.smallestElement(emptyArray));

    System.out.println("---------------reverse-------------");
    for (int i : reversed) {
      System.out.println(i);
    }
  }
}
