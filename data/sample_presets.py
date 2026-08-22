"""
Sample buggy code presets across Python, C++, and Java for instant demo and testing.
"""

SAMPLE_PRESETS = {
    "Python": {
        "IndexError & Mutable Default Arg": {
            "title": "Student Task: Calculate Grade Averages & Store Results",
            "code": """def calculate_student_averages(grades_list, history=[]):
    \"\"\"Calculates average and appends to student history.\"\"\"
    total = 0
    # Bug 1: Loop goes out of bounds (<= len)
    for i in range(0, len(grades_list) + 1):
        total += grades_list[i]
    
    avg = total / len(grades_list)
    # Bug 2: Mutable default argument accumulates state across function calls
    history.append(avg)
    return avg, history

# Test run
scores = [85, 90, 78, 92]
avg, hist = calculate_student_averages(scores)
print(f"Average: {avg}, History: {hist}")
""",
            "error_log": """Traceback (most recent call last):
  File "grade_calculator.py", line 15, in <module>
    avg, hist = calculate_student_averages(scores)
  File "grade_calculator.py", line 6, in calculate_student_averages
    total += grades_list[i]
IndexError: list index out of range"""
        },
        "Infinite Recursion (Fibonacci)": {
            "title": "Student Task: Recursive Fibonacci Sequence",
            "code": """def fibonacci(n):
    # Bug: Missing base case for n == 0 or n <= 1, wrong boundary check
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

print("Fibonacci(0):", fibonacci(0))
""",
            "error_log": """Traceback (most recent call last):
  File "fibonacci.py", line 7, in <module>
    print("Fibonacci(0):", fibonacci(0))
  File "fibonacci.py", line 5, in fibonacci
    return fibonacci(n - 1) + fibonacci(n - 2)
  ... [Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded in comparison"""
        },
        "KeyError & Type Mismatch in Dictionary": {
            "title": "Student Task: Inventory Price Aggregator",
            "code": """def get_total_inventory_value(inventory):
    total = 0.0
    for item in inventory:
        # Bug 1: Price is string, requires float cast
        # Bug 2: Accessing 'qty' which might be missing or keyed as 'quantity'
        total += item["price"] * item["qty"]
    return total

items = [
    {"name": "Notebook", "price": "4.50", "qty": 10},
    {"name": "Pen", "price": "1.25", "quantity": 25}
]
print("Total Value:", get_total_inventory_value(items))
""",
            "error_log": """Traceback (most recent call last):
  File "inventory.py", line 12, in <module>
    print("Total Value:", get_total_inventory_value(items))
  File "inventory.py", line 6, in get_total_inventory_value
    total += item["price"] * item["qty"]
TypeError: can't multiply sequence by non-int of type 'int'"""
        }
    },
    "C++": {
        "Segmentation Fault (Dangling Pointer)": {
            "title": "Student Task: Dynamic Integer Array Sum",
            "code": """#include <iostream>
#include <vector>

int* createBuffer(int size) {
    int localArray[size]; // Bug 1: Stack allocated VLA
    for (int i = 0; i < size; ++i) {
        localArray[i] = (i + 1) * 10;
    }
    return localArray; // Bug 2: Returning pointer to local stack variable!
}

int main() {
    int size = 5;
    int* ptr = createBuffer(size);
    
    std::cout << "Buffer contents: ";
    for (int i = 0; i <= size; ++i) { // Bug 3: Out-of-bounds loop (<= size)
        std::cout << ptr[i] << " ";
    }
    std::cout << std::endl;
    return 0;
}
""",
            "error_log": """Segmentation fault (core dumped)
AddressSanitizer:DEADLYSIGNAL
=================================================================
==12849==ERROR: AddressSanitizer: stack-use-after-return on address 0x7ffe2319f020
READ of size 4 at 0x7ffe2319f020 thread T0
    #0 0x55dc98a213e8 in main buffer.cpp:16
    #1 0x7f48e3629d8f in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x29d8f)"""
        },
        "Vector Out-of-Bounds & Memory Leak": {
            "title": "Student Task: Dynamic Student Record Manager",
            "code": """#include <iostream>
#include <vector>
#include <string>

class StudentManager {
private:
    std::vector<std::string> students;
    int* auditCounter;

public:
    StudentManager() {
        auditCounter = new int(0);
    }
    
    // Bug 1: Missing Destructor -> Memory leak of auditCounter

    void addStudent(const std::string& name) {
        students.push_back(name);
        (*auditCounter)++;
    }

    std::string getTopStudent() {
        // Bug 2: No check if vector is empty before indexing
        return students.at(students.size()); // Bug 3: Out of bounds (size vs size - 1)
    }
};

int main() {
    StudentManager sm;
    std::cout << sm.getTopStudent() << std::endl;
    return 0;
}
""",
            "error_log": """terminate called after throwing an instance of 'std::out_of_range'
  what():  vector::_M_range_check: __n (which is 0) >= this->size() (which is 0)
Aborted (core dumped)"""
        }
    },
    "Java": {
        "NullPointerException & Off-by-One": {
            "title": "Student Task: Course Roster & Score Computation",
            "code": """import java.util.ArrayList;
import java.util.List;

public class Main {
    private List<String> studentNames;
    private int[] examScores;

    public Main() {
        // Bug 1: studentNames is left null (not instantiated)
        examScores = new int[5];
    }

    public void enroll(String name) {
        studentNames.add(name); // Throws NullPointerException
    }

    public int getHighestScore() {
        int max = 0;
        // Bug 2: Off-by-one error with <= examScores.length
        for (int i = 0; i <= examScores.length; i++) {
            if (examScores[i] > max) {
                max = examScores[i];
            }
        }
        return max;
    }

    public static void main(String[] args) {
        Main roster = new Main();
        roster.enroll("Alex Johnson");
        System.out.println("Top score: " + roster.getHighestScore());
    }
}
""",
            "error_log": """Exception in thread "main" java.lang.NullPointerException: Cannot invoke "java.util.List.add(Object)" because "this.studentNames" is null
	at Main.enroll(Main.java:13)
	at Main.main(Main.java:27)"""
        },
        "String Equality & Concurrent Modification": {
            "title": "Student Task: Filter Inactive Users",
            "code": """import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void removeInactive(List<String> statuses) {
        // Bug 1: Modifying list during enhanced for-loop iteration
        for (String status : statuses) {
            // Bug 2: Using == instead of .equals() for String comparison
            if (status == "inactive") {
                statuses.remove(status);
            }
        }
    }

    public static void main(String[] args) {
        List<String> list = new ArrayList<>();
        list.add("active");
        list.add(new String("inactive"));
        list.add("active");
        
        removeInactive(list);
        System.out.println("Remaining: " + list);
    }
}
""",
            "error_log": """Exception in thread "main" java.util.ConcurrentModificationException
	at java.base/java.util.ArrayList$Itr.checkForComodification(ArrayList.java:1013)
	at java.base/java.util.ArrayList$Itr.next(ArrayList.java:967)
	at Main.removeInactive(Main.java:6)
	at Main.main(Main.java:19)"""
        }
    }
}
