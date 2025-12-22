"""Test large code samples for accuracy"""
import requests

API = 'http://127.0.0.1:5000/analyze'

# Large Java code sample (100+ lines)
large_java_code = """
public class ComplexSystem {
    private int[] data;
    private int size;
    private static final int MAX_SIZE = 1000;
    
    public ComplexSystem(int capacity) {
        this.data = new int[capacity];
        this.size = 0;
    }
    
    // O(n^2) - Bubble Sort implementation
    public void bubbleSort() {
        int n = data.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (data[j] > data[j + 1]) {
                    int temp = data[j];
                    data[j] = data[j + 1];
                    data[j + 1] = temp;
                }
            }
        }
    }
    
    // O(log n) - Binary Search
    public int binarySearch(int target) {
        int left = 0;
        int right = size - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (data[mid] == target) {
                return mid;
            }
            
            if (data[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return -1;
    }
    
    // O(n) - Linear search  
    public int linearSearch(int target) {
        for (int i = 0; i < size; i++) {
            if (data[i] == target) {
                return i;
            }
        }
        return -1;
    }
    
    // O(n^3) - Matrix multiplication helper
    public int[][] multiplyMatrices(int[][] a, int[][] b) {
        int n = a.length;
        int[][] result = new int[n][n];
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                result[i][j] = 0;
                for (int k = 0; k < n; k++) {
                    result[i][j] += a[i][k] * b[k][j];
                }
            }
        }
        
        return result;
    }
    
    public void add(int value) {
        if (size < data.length) {
            data[size++] = value;
        }
    }
    
    public int get(int index) {
        if (index >= 0 && index < size) {
            return data[index];
        }
        throw new IndexOutOfBoundsException();
    }
    
    public int getSize() {
        return size;
    }
    
    public static void main(String[] args) {
        ComplexSystem system = new ComplexSystem(100);
        
        for (int i = 0; i < 50; i++) {
            system.add(i * 2);
        }
        
        system.bubbleSort();
        
        int result = system.binarySearch(20);
        System.out.println("Found at: " + result);
    }
}
"""

# Large Python code sample
large_python_code = """
class DataProcessor:
    def __init__(self, data):
        self.data = data
        self.processed = []
        self.cache = {}
    
    def bubble_sort(self):
        '''O(n^2) time, O(1) space'''
        arr = self.data.copy()
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
    
    def binary_search(self, target):
        '''O(log n) time, O(1) space'''
        arr = sorted(self.data)
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
    
    def find_duplicates(self):
        '''O(n) time, O(n) space'''
        seen = set()
        duplicates = []
        for item in self.data:
            if item in seen:
                duplicates.append(item)
            seen.add(item)
        return duplicates
    
    def matrix_multiply(self, matrix_a, matrix_b):
        '''O(n^3) time, O(n^2) space'''
        n = len(matrix_a)
        result = [[0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]
        
        return result
    
    def merge_sort(self, arr=None):
        '''O(n log n) time, O(n) space'''
        if arr is None:
            arr = self.data.copy()
        
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid])
        right = self.merge_sort(arr[mid:])
        
        return self._merge(left, right)
    
    def _merge(self, left, right):
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def process_all(self):
        sorted_data = self.bubble_sort()
        duplicates = self.find_duplicates()
        return {
            'sorted': sorted_data,
            'duplicates': duplicates,
            'size': len(self.data)
        }


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90, 45, 33, 21]
    processor = DataProcessor(data)
    result = processor.process_all()
    print(result)
"""

# Large C++ code
large_cpp_code = """
#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>

class GraphProcessor {
private:
    int vertices;
    std::vector<std::vector<int>> adj;
    
public:
    GraphProcessor(int v) : vertices(v), adj(v) {}
    
    void addEdge(int u, int v) {
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    
    // O(V + E) - BFS traversal
    std::vector<int> bfs(int start) {
        std::vector<int> result;
        std::vector<bool> visited(vertices, false);
        std::queue<int> q;
        
        visited[start] = true;
        q.push(start);
        
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            result.push_back(u);
            
            for (int v : adj[u]) {
                if (!visited[v]) {
                    visited[v] = true;
                    q.push(v);
                }
            }
        }
        
        return result;
    }
    
    // O(V + E) - DFS traversal
    void dfs(int u, std::vector<bool>& visited, std::vector<int>& result) {
        visited[u] = true;
        result.push_back(u);
        
        for (int v : adj[u]) {
            if (!visited[v]) {
                dfs(v, visited, result);
            }
        }
    }
    
    std::vector<int> dfsTraversal(int start) {
        std::vector<int> result;
        std::vector<bool> visited(vertices, false);
        dfs(start, visited, result);
        return result;
    }
    
    // O(V^2) - Check all pairs connectivity
    bool allPairsConnected() {
        for (int i = 0; i < vertices; i++) {
            for (int j = i + 1; j < vertices; j++) {
                std::vector<int> path = bfs(i);
                bool found = std::find(path.begin(), path.end(), j) != path.end();
                if (!found) return false;
            }
        }
        return true;
    }
};

// O(n^2) - Selection Sort
void selectionSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[minIdx]) {
                minIdx = j;
            }
        }
        std::swap(arr[i], arr[minIdx]);
    }
}

int main() {
    GraphProcessor graph(6);
    graph.addEdge(0, 1);
    graph.addEdge(0, 2);
    graph.addEdge(1, 3);
    graph.addEdge(2, 4);
    graph.addEdge(3, 5);
    
    std::vector<int> bfsResult = graph.bfs(0);
    std::cout << "BFS: ";
    for (int v : bfsResult) {
        std::cout << v << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
"""

def test_large_code(name, code, expected_lang, expected_time):
    try:
        r = requests.post(API, json={'code': code}, timeout=60)
        result = r.json()
        
        lang = result.get('language', 'Unknown')
        time_c = result.get('timeComplexity', 'Unknown')
        space_c = result.get('spaceComplexity', 'Unknown')
        engine = result.get('engine', 'Unknown')
        
        print(f"\n=== {name} ===")
        print(f"Lines: {len(code.strip().split(chr(10)))}")
        print(f"Language: {lang} (expected: {expected_lang})")
        print(f"Time: {time_c} (expected: {expected_time})")
        print(f"Space: {space_c}")
        print(f"Engine: {engine}")
        
        lang_ok = expected_lang.lower() in lang.lower()
        print(f"Language OK: {lang_ok}")
        
        return lang_ok
    except Exception as e:
        print(f"\n=== {name} === ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing Large Code Samples...")
    
    # Test 1: Large Java
    test_large_code("Large Java (100+ lines)", large_java_code, "Java", "O(n³)")
    
    # Test 2: Large Python  
    test_large_code("Large Python (100+ lines)", large_python_code, "Python", "O(n³)")
    
    # Test 3: Large C++
    test_large_code("Large C++ (100+ lines)", large_cpp_code, "C++", "O(V²)")
