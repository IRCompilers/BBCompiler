import pytest

from src.Project.Pipeline import run_pipeline

# Simple test cases

test_case_1 = "print(\"Hello, World!\")"
test_case_2 = "?print(\"Hello, World!\")"
test_case_3 = "function add(x: Number, y: Number) { \n\t return x+y; }\n let a=3, y=-5 in print(add(a, y));"
test_case_4 = "function addCosTan(x: Number, y: Number) { \n\t return cos(x) *tan(y); }\n let a=3, y=-5 in print(addCosTan(a, y));"
test_case_5 = "type Person(name, age){ \n name = name, age = age; }\n let p = Person(\"John\", 25) in print(p.name);"
test_case_6 = "if (20 > 10) { print(\"x is greater than 10\"); } else { print(\"x is not greater than 10\"); }"
test_case_7 = "if (x > 10) { print(\"x is greater than 10\"); } else { print(\"x is not greater than 10\"); }"
test_case_8 = "for (x in range(0, 10)) print(x);"

# Complex test cases
test_case_9 = """
let a = 10 in while (a >= 0) {
    print(a);
    a := a - 1;
}
"""

test_case_10 = """
let iterable = range(0, 10) in
    while (iterable.next())
        let x = iterable.current() in
            print(x);
"""

test_case_11 = """
function gcd(a, b) => while (a > 0)
    let m = a % b in {
        b := a;
        a := m;
    };

let a = 12, b = 5 in
    print(gcd(a, b));
"""

test_case_12 = """
let a = 5, b = 10, c = 20 in {
    print(a+b);
    print(b*c);
    print(c/a);
}
"""

test_case_13 = """
let a = 12.5, b = 5 in {
    print(a+b);
    print(b*a);
    print(a/b);
}
"""

test_case_14 = "let a = 10 in while (a >= 0 { print(a); a := a - 1; }"
test_case_15 = "let a = [x for x in range(0,10)] in for (x in a) print(x);"
test_case_16 = "let a = 10 in while (b >= 0) { print(a); a := a - 1; }"  # b is not defined
test_case_17 = "function add(x, y) { return x+y; } print(add(a, b));"  # a and b are not defined

test_case_18 = """
type Person(){
    name = "John";
    age = 25;
    
    function printName(){
        print(name);
    }
}

let x = new Person() in x.printName()
"""

test_case_19 = """
let x = new Person() in x.printName()
"""

test_case_20 = """
type Person(){
    name = "John";
    age = 25;
    
    function printName(){
        print(name);
    }
}

let x = new Person() in if x.name == "Jane" print("Jane") else print("John")
"""

test_case_21 = """
if (x > 10) {
    print("x is greater than 10");
}
"""


# Use the @pytest.mark.parametrize decorator to specify different sets of data
@pytest.mark.parametrize("input_, expected", [
    (test_case_1, "Hello, World!\n"),
    (test_case_2, "LEXER ERROR: Invalid token \"?\" at position: (0, 0)\n"),
    (test_case_3, "-2\n"),
    (test_case_4, "-0.9899924966004454\n"),
    (test_case_5, "John\n"),
    (test_case_6, "x is greater than 10\n"),
    (test_case_7, "SEMANTIC ERROR: The x variable doesn't exist in the current context\n"),
    (test_case_8, "0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n"),
    (test_case_9, "10\n9\n8\n7\n6\n5\n4\n3\n2\n1\n0\n"),
    (test_case_10, "0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n"),
    (test_case_11, "1\n"),
    (test_case_12, "15\n200\n4\n"),
    (test_case_13, "17.5\n62.5\n2.5\n"),
    (test_case_14, "PARSER ERROR: Expected tokens { ) }\n"),
    (test_case_15, "0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n"),
    (test_case_16, "SEMANTIC ERROR: The b variable doesn't exist in the current context\n"),
    (test_case_17, "SEMANTIC ERROR: The a variable doesn't exist in the current context\n"
                   "SEMANTIC ERROR: The b variable doesn't exist in the current context\n"),
    (test_case_18, "John\n"),
    (test_case_19, "SEMANTIC ERROR: The Person type doesn't exist in the current context\n"),
    (test_case_20, "SEMANTIC ERROR: Parent doesn't have a definition for name"),
    (test_case_21, "PARSER ERROR: Expected tokens { else }\n")
])
def test_print_message(capsys, input_, expected):
    # Call the function with the input parameter
    run_pipeline(input_, "../models")
    # Capture the output
    captured = capsys.readouterr()
    # Assert that the captured output matches the expected output
    assert captured.out == expected
