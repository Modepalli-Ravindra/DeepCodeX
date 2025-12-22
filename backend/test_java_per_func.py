import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from analyzer.per_function_analyzer import analyze_per_function

java_code = """
public class StressTest {
    public static void bubbleSort(int[] a) {
        for(int i=0; i<a.length; i++)
            for(int j=0; j<a.length-i-1; j++)
                if(a[j] > a[j+1]) { int t=a[j]; a[j]=a[j+1]; a[j+1]=t; }
    }
    
    public static int fib(int n) {
        if(n<=1) return n;
        return fib(n-1) + fib(n-2);
    }
    
    public static void main(String[] args) {
        int[] x = {3,1,2};
        bubbleSort(x);
        System.out.println(fib(5));
    }
}
"""

result = analyze_per_function(java_code)

print(f"Total Functions: {len(result['functions'])}")
for f in result['functions']:
    print(f"Function: {f['name']} -> Time: {f['timeComplexity']}")

print(f"Worst Time Func: {result['worstTimeFunction']}")
print(f"Summary: {result['summary']}")
