"""Quick accuracy test for DeepCodeX"""
import requests

API = 'http://127.0.0.1:5000/analyze'

tests = [
    # (name, code, expected_lang, expected_time, expected_space)
    ("Python-O1", "def f(n): return n*2", "Python", "O(1)", "O(1)"),
    ("Python-On", "def f(arr):\n    for x in arr:\n        print(x)", "Python", "O(n)", "O(1)"),
    ("Python-LogN", """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""", "Python", "O(log n)", "O(1)"),
    
    ("Java-O1", "public class Test { public static void main(String[] args) { int x = 5; } }", "Java", "O(1)", "O(1)"),
    ("Java-N2", """public class BubbleSort {
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
}""", "Java", "O(n²)", "O(1)"),
    
    ("Cpp-O1", "#include <iostream>\nint main() { std::cout << 5; return 0; }", "C++", "O(1)", "O(1)"),
    ("Cpp-BFS", """#include <iostream>
#include <queue>
#include <vector>
void BFS(int start, std::vector<std::vector<int>>& adj) {
    std::vector<bool> visited(adj.size(), false);
    std::queue<int> q;
    visited[start] = true;
    q.push(start);
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (int v : adj[u]) {
            if (!visited[v]) {
                visited[v] = true;
                q.push(v);
            }
        }
    }
}""", "C++", "O(V + E)", "O(V)"),
    
    ("C-O1", "#include <stdio.h>\nint main() { printf(\"Hi\"); return 0; }", "C", "O(1)", "O(1)"),
    ("C-On", """#include <stdio.h>
int kadane(int arr[], int n) {
    int max_so_far = arr[0];
    int current_max = arr[0];
    for (int i = 1; i < n; i++) {
        current_max = current_max + arr[i];
        if (max_so_far < current_max)
            max_so_far = current_max;
        if (current_max < 0)
            current_max = 0;
    }
    return max_so_far;
}""", "C", "O(n)", "O(1)"),
    
    ("JS-O1", "function test() { console.log(5); }", "JavaScript", "O(1)", "O(1)"),
    ("JS-On", """function findMax(nums) {
    let maxVal = nums[0];
    for (let i = 1; i < nums.length; i++) {
        if (nums[i] > maxVal) {
            maxVal = nums[i];
        }
    }
    return maxVal;
}""", "JavaScript", "O(n)", "O(1)"),
]

def run_tests():
    results = {"lang": [0, 0], "time": [0, 0], "space": [0, 0]}
    
    for name, code, exp_lang, exp_time, exp_space in tests:
        try:
            r = requests.post(API, json={"code": code}, timeout=30)
            d = r.json()
            
            got_lang = d.get("language", "Unknown")
            got_time = d.get("timeComplexity", "Unknown")
            got_space = d.get("spaceComplexity", "Unknown")
            
            # Check language
            lang_ok = exp_lang.lower() in got_lang.lower()
            time_ok = got_time == exp_time
            space_ok = got_space == exp_space
            
            results["lang"][0] += 1 if lang_ok else 0
            results["lang"][1] += 1
            results["time"][0] += 1 if time_ok else 0
            results["time"][1] += 1
            results["space"][0] += 1 if space_ok else 0
            results["space"][1] += 1
            
            status = "PASS" if (lang_ok and time_ok and space_ok) else "FAIL"
            print(f"{name}: {status}")
            if not lang_ok:
                print(f"  Lang: {got_lang} (expected: {exp_lang})")
            if not time_ok:
                print(f"  Time: {got_time} (expected: {exp_time})")
            if not space_ok:
                print(f"  Space: {got_space} (expected: {exp_space})")
                
        except Exception as e:
            print(f"{name}: ERROR - {e}")
            for k in results:
                results[k][1] += 1
    
    print()
    print("=" * 50)
    print("ACCURACY SUMMARY")
    print("=" * 50)
    for k, (c, t) in results.items():
        pct = c / t * 100 if t > 0 else 0
        print(f"{k.upper():8}: {c}/{t} = {pct:.1f}%")
    
    total_c = sum(v[0] for v in results.values())
    total_t = sum(v[1] for v in results.values())
    overall = total_c / total_t * 100 if total_t > 0 else 0
    print(f"{'OVERALL':8}: {total_c}/{total_t} = {overall:.1f}%")
    
    if overall >= 90:
        print("\n[OK] TARGET MET: 90%+ accuracy!")
    else:
        print(f"\n[!!] Need {90 - overall:.1f}% more accuracy")
    
    return overall >= 90

if __name__ == "__main__":
    run_tests()
