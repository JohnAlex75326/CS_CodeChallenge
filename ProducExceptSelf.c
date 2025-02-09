#include <stdio.h>

void productExceptSelf(int arr[], int n, int result[]) {
    int left[n], right[n];

    // Compute left product array
    left[0] = 1;
    for (int i = 1; i < n; i++) {
        left[i] = left[i - 1] * arr[i - 1];
    }

    // Compute right product array
    right[n - 1] = 1;
    for (int i = n - 2; i >= 0; i--) {
        right[i] = right[i + 1] * arr[i + 1];
    }

    // Compute the result array
    for (int i = 0; i < n; i++) {
        result[i] = left[i] * right[i];
    }
}

// Utility function to print an array
void printArray(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int n = sizeof(arr) / sizeof(arr[0]);
    int result[n];

    productExceptSelf(arr, n, result);
    printArray(result, n);  // Output: 120 60 40 30 24

    return 0;
}
