"""
DeepCodeX Accuracy Test Suite
Tests language detection and complexity analysis accuracy
Target: 90%+ accuracy
"""

import requests
import json

API_URL = "http://127.0.0.1:5000/analyze"

# ============================================================
# TEST CASES: (code, expected_language, expected_time, expected_space)
# ============================================================

TEST_CASES = [
    # ==================== PYTHON ====================
    {
        "name": "Python - O(1) Constant",
        "lang": "Python",
        "time": "O(1)",
        "space": "O(1)",
        "code": """
def check_parity(n):
    is_even = n % 2 == 0
    val1 = n * 10
    val2 = n + 500
    return {"parity": "Even" if is_even else "Odd", "value": val1}
"""
    },
    {
        "name": "Python - O(n) Linear",
        "lang": "Python",
        "time": "O(n)",
        "space": "O(1)",
        "code": """
def find_max(arr):
    max_val = arr[0]
    for num in arr:
        if num > max_val:
            max_val = num
    return max_val
"""
    },
    {
        "name": "Python - O(log n) Binary Search",
        "lang": "Python",
        "time": "O(log n)",
        "space": "O(1)",
        "code": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
    },
    {
        "name": "Python - O(n²) Bubble Sort",
        "lang": "Python",
        "time": "O(n²)",
        "space": "O(1)",
        "code": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
"""
    },
    {
        "name": "Python - O(n log n) Merge Sort",
        "lang": "Python",
        "time": "O(n log n)",
        "space": "O(n)",
        "code": """
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
"""
    },
    {
        "name": "Python - O(2^n) Subset Sum",
        "lang": "Python",
        "time": "O(2ⁿ)",
        "space": "O(n)",
        "code": """
def subset_sum(arr, n, target):
    if target == 0:
        return True
    if n == 0:
        return False
    if arr[n-1] > target:
        return subset_sum(arr, n-1, target)
    return subset_sum(arr, n-1, target) or subset_sum(arr, n-1, target - arr[n-1])
"""
    },
    {
        "name": "Python - O(n) Kadane's Algorithm",
        "lang": "Python",
        "time": "O(n)",
        "space": "O(1)",
        "code": """
def kadane(arr):
    max_so_far = arr[0]
    current_max = arr[0]
    for i in range(1, len(arr)):
        current_max = max(arr[i], current_max + arr[i])
        max_so_far = max(max_so_far, current_max)
    return max_so_far
"""
    },
    {
        "name": "Python - O(E log V) Dijkstra",
        "lang": "Python",
        "time": "O(E log V)",
        "space": "O(V + E)",
        "code": """
import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        dist, node = heapq.heappop(pq)
        if dist > distances[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    return distances
"""
    },
    
    # ==================== JAVA ====================
    {
        "name": "Java - O(n²) Bubble Sort",
        "lang": "Java",
        "time": "O(n²)",
        "space": "O(1)",
        "code": """
public class BubbleSort {
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
    
    public static void main(String[] args) {
        int[] arr = {5, 3, 8, 4, 2};
        bubbleSort(arr);
        for (int num : arr) {
            System.out.print(num + " ");
        }
    }
}
"""
    },
    {
        "name": "Java - O(log n) Binary Search",
        "lang": "Java",
        "time": "O(log n)",
        "space": "O(1)",
        "code": """
public class BinarySearch {
    public static int search(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                return mid;
            }
            if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }
}
"""
    },
    {
        "name": "Java - O(n log n) Heap Sort",
        "lang": "Java",
        "time": "O(n log n)",
        "space": "O(log n)",
        "code": """
public class HeapSort {
    public void sort(int arr[]) {
        int n = arr.length;
        for (int i = n / 2 - 1; i >= 0; i--)
            heapify(arr, n, i);
        for (int i = n - 1; i > 0; i--) {
            int temp = arr[0];
            arr[0] = arr[i];
            arr[i] = temp;
            heapify(arr, i, 0);
        }
    }

    void heapify(int arr[], int n, int i) {
        int largest = i;
        int l = 2 * i + 1;
        int r = 2 * i + 2;
        if (l < n && arr[l] > arr[largest]) largest = l;
        if (r < n && arr[r] > arr[largest]) largest = r;
        if (largest != i) {
            int swap = arr[i];
            arr[i] = arr[largest];
            arr[largest] = swap;
            heapify(arr, n, largest);
        }
    }
}
"""
    },
    {
        "name": "Java - O(n!) Permutations",
        "lang": "Java",
        "time": "O(n!)",
        "space": "O(n)",
        "code": """
public class Permutations {
    public static void generate(String str, String ans) {
        if (str.length() == 0) {
            System.out.println(ans);
            return;
        }
        for (int i = 0; i < str.length(); i++) {
            char ch = str.charAt(i);
            String ros = str.substring(0, i) + str.substring(i + 1);
            generate(ros, ans + ch);
        }
    }
    
    public static void main(String[] args) {
        generate("ABC", "");
    }
}
"""
    },
    
    # ==================== C++ ====================
    {
        "name": "C++ - O(√n) Prime Check",
        "lang": "C++",
        "time": "O(√n)",
        "space": "O(1)",
        "code": """
#include <iostream>
#include <cmath>

bool isPrime(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    int limit = static_cast<int>(std::sqrt(n));
    for (int i = 5; i <= limit; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0)
            return false;
    }
    return true;
}
"""
    },
    {
        "name": "C++ - O(n²) Selection Sort",
        "lang": "C++",
        "time": "O(n²)",
        "space": "O(1)",
        "code": """
#include <iostream>
#include <vector>

void selectionSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        int temp = arr[min_idx];
        arr[min_idx] = arr[i];
        arr[i] = temp;
    }
}
"""
    },
    {
        "name": "C++ - O(V + E) BFS",
        "lang": "C++",
        "time": "O(V + E)",
        "space": "O(V)",
        "code": """
#include <iostream>
#include <vector>
#include <queue>

void BFS(int start, const std::vector<std::vector<int>>& adj) {
    int V = adj.size();
    std::vector<bool> visited(V, false);
    std::queue<int> q;
    
    visited[start] = true;
    q.push(start);
    
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        std::cout << u << " ";
        
        for (int v : adj[u]) {
            if (!visited[v]) {
                visited[v] = true;
                q.push(v);
            }
        }
    }
}
"""
    },
    
    # ==================== C ====================
    {
        "name": "C - O(n) Kadane's Algorithm",
        "lang": "C",
        "time": "O(n)",
        "space": "O(1)",
        "code": """
#include <stdio.h>
#include <limits.h>

int kadane(int arr[], int n) {
    int max_so_far = INT_MIN;
    int current_max = 0;
    
    for (int i = 0; i < n; i++) {
        current_max = current_max + arr[i];
        if (max_so_far < current_max)
            max_so_far = current_max;
        if (current_max < 0)
            current_max = 0;
    }
    return max_so_far;
}
"""
    },
    {
        "name": "C - O(n³) Matrix Multiplication",
        "lang": "C",
        "time": "O(n³)",
        "space": "O(n²)",
        "code": """
#include <stdio.h>

void multiplyMatrices(int first[10][10], int second[10][10], int result[10][10], int r1, int c1, int r2, int c2) {
    for (int i = 0; i < r1; ++i) {
        for (int j = 0; j < c2; ++j) {
            result[i][j] = 0;
            for (int k = 0; k < c1; ++k) {
                result[i][j] += first[i][k] * second[k][j];
            }
        }
    }
}

int main() {
    int a[10][10] = {{1, 2}, {3, 4}};
    int b[10][10] = {{5, 6}, {7, 8}};
    int res[10][10];
    multiplyMatrices(a, b, res, 2, 2, 2, 2);
    return 0;
}
"""
    },
    {
        "name": "C - O(V³) Floyd-Warshall",
        "lang": "C",
        "time": "O(V³)",
        "space": "O(V²)",
        "code": """
#include <stdio.h>
#define INF 99999

void floydWarshall(int graph[4][4], int V) {
    int dist[4][4];
    
    for (int i = 0; i < V; i++)
        for (int j = 0; j < V; j++)
            dist[i][j] = graph[i][j];
    
    for (int k = 0; k < V; k++) {
        for (int i = 0; i < V; i++) {
            for (int j = 0; j < V; j++) {
                if (dist[i][k] + dist[k][j] < dist[i][j])
                    dist[i][j] = dist[i][k] + dist[k][j];
            }
        }
    }
}
"""
    },
    
    # ==================== JAVASCRIPT ====================
    {
        "name": "JavaScript - O(n) Find Max",
        "lang": "JavaScript",
        "time": "O(n)",
        "space": "O(1)",
        "code": """
function findMaxElement(nums) {
    if (!nums || nums.length === 0) return null;
    
    let maxVal = nums[0];
    for (let i = 1; i < nums.length; i++) {
        if (nums[i] > maxVal) {
            maxVal = nums[i];
        }
    }
    
    console.log("Max:", maxVal);
    return maxVal;
}

const data = [12, 45, 2, 89, 34];
findMaxElement(data);
"""
    },
    {
        "name": "JavaScript - O(n²) Bubble Sort",
        "lang": "JavaScript",
        "time": "O(n²)",
        "space": "O(1)",
        "code": """
function bubbleSort(arr) {
    let n = arr.length;
    let swapped;
    
    for (let i = 0; i < n - 1; i++) {
        swapped = false;
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                let temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = true;
            }
        }
        if (!swapped) break;
    }
    return arr;
}
"""
    },
    {
        "name": "JavaScript - O(V + E) DFS",
        "lang": "JavaScript",
        "time": "O(V + E)",
        "space": "O(V)",
        "code": """
function DFS(u, adj, visited) {
    visited[u] = true;
    console.log("Visited:", u);
    
    for (let v of adj[u]) {
        if (!visited[v]) {
            DFS(v, adj, visited);
        }
    }
}

const graph = [[1, 2], [0, 3], [0, 4], [1], [2]];
const visited = Array(5).fill(false);
DFS(0, graph, visited);
"""
    },
    {
        "name": "JavaScript - O(n) Frequency Count",
        "lang": "JavaScript",
        "time": "O(n)",
        "space": "O(n)",
        "code": """
function countFrequencies(str) {
    const map = new Map();
    
    for (let char of str) {
        map.set(char, (map.get(char) || 0) + 1);
    }
    
    console.log("Frequencies:", map);
    return map;
}

countFrequencies("complexityanalysis");
"""
    },
]


def normalize_complexity(complexity):
    """Normalize complexity strings for comparison."""
    if not complexity:
        return ""
    # Map equivalent representations
    mappings = {
        "O(2^n)": "O(2ⁿ)",
        "O(n^2)": "O(n²)",
        "O(n^3)": "O(n³)",
        "O(V^3)": "O(V³)",
        "O(V^2)": "O(V²)",
        "O((V + E) log V)": "O(E log V)",  # Alternate Dijkstra notation
        "O(V*E)": "O(V × E)",
        "O(V * E)": "O(V × E)",
        "O(n^2 * 2^n)": "O(n² × 2ⁿ)",
        "O(n * 2^n)": "O(n × 2ⁿ)",
    }
    normalized = complexity.strip()
    return mappings.get(normalized, normalized)


def test_analysis():
    """Run all test cases and calculate accuracy."""
    print("=" * 70)
    print("DeepCodeX Accuracy Test Suite")
    print("=" * 70)
    print()
    
    results = {
        "lang_correct": 0,
        "lang_total": 0,
        "time_correct": 0,
        "time_total": 0,
        "space_correct": 0,
        "space_total": 0,
    }
    
    failed_tests = []
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: {test['name']}")
        
        try:
            response = requests.post(
                API_URL,
                json={"code": test["code"]},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  ❌ API Error: {response.status_code}")
                failed_tests.append((test["name"], "API Error"))
                continue
            
            data = response.json()
            
            # Check language (from API response)
            detected_lang = data.get("language", "Unknown")
            expected_lang = test["lang"]
            
            # Normalize language comparison
            lang_match = expected_lang.lower() in detected_lang.lower() or detected_lang.lower() in expected_lang.lower()
            
            results["lang_total"] += 1
            if lang_match:
                results["lang_correct"] += 1
                print(f"  ✅ Language: {detected_lang} (expected: {expected_lang})")
            else:
                print(f"  ❌ Language: {detected_lang} (expected: {expected_lang})")
                failed_tests.append((test["name"], f"Language: got {detected_lang}, expected {expected_lang}"))
            
            # Check time complexity
            actual_time = normalize_complexity(data.get("timeComplexity", ""))
            expected_time = normalize_complexity(test["time"])
            
            results["time_total"] += 1
            if actual_time == expected_time:
                results["time_correct"] += 1
                print(f"  ✅ Time: {actual_time}")
            else:
                print(f"  ❌ Time: {actual_time} (expected: {expected_time})")
                failed_tests.append((test["name"], f"Time: got {actual_time}, expected {expected_time}"))
            
            # Check space complexity
            actual_space = normalize_complexity(data.get("spaceComplexity", ""))
            expected_space = normalize_complexity(test["space"])
            
            results["space_total"] += 1
            if actual_space == expected_space:
                results["space_correct"] += 1
                print(f"  ✅ Space: {actual_space}")
            else:
                print(f"  ❌ Space: {actual_space} (expected: {expected_space})")
                failed_tests.append((test["name"], f"Space: got {actual_space}, expected {expected_space}"))
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            failed_tests.append((test["name"], str(e)))
        
        print()
    
    # Calculate and print accuracy
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    lang_accuracy = (results["lang_correct"] / results["lang_total"] * 100) if results["lang_total"] > 0 else 0
    time_accuracy = (results["time_correct"] / results["time_total"] * 100) if results["time_total"] > 0 else 0
    space_accuracy = (results["space_correct"] / results["space_total"] * 100) if results["space_total"] > 0 else 0
    
    total_correct = results["lang_correct"] + results["time_correct"] + results["space_correct"]
    total_tests = results["lang_total"] + results["time_total"] + results["space_total"]
    overall_accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 Language Detection: {results['lang_correct']}/{results['lang_total']} ({lang_accuracy:.1f}%)")
    print(f"⏱️  Time Complexity:    {results['time_correct']}/{results['time_total']} ({time_accuracy:.1f}%)")
    print(f"💾 Space Complexity:   {results['space_correct']}/{results['space_total']} ({space_accuracy:.1f}%)")
    print(f"\n🎯 OVERALL ACCURACY:   {total_correct}/{total_tests} ({overall_accuracy:.1f}%)")
    
    if overall_accuracy >= 90:
        print("\n✅ TARGET MET: 90%+ accuracy achieved!")
    else:
        print(f"\n⚠️  TARGET NOT MET: Need {90 - overall_accuracy:.1f}% more accuracy")
    
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for name, reason in failed_tests:
            print(f"   - {name}: {reason}")
    
    return overall_accuracy >= 90


if __name__ == "__main__":
    success = test_analysis()
    exit(0 if success else 1)
