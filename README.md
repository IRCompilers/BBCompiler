# BBCompiler
A compiler for the HULK language

## Summary

The goal of this project is an interpreter for the HULK language described [here](https://matcom.in/hulk/guide/expressions/)
The project is divided into four main parts:
- Lexer
- Parser
- Semantic Checker
- Interpreter

The lexer is responsible for tokenizing the input file, the parser is responsible for building the AST, the semantic checker is responsible for checking the semantic rules of the language and the interpreter is responsible for executing the code.

## Prerequisites

- Dill
- Pytest
- Click

## Running Tests

To run the tests, run the following command:

```bash
# Tests for the semantic checker
python -m unittest test/SemanticCheckTesting.py

# Tests for lexer
python -m unittest test/LexerTesting.py

# Tests for parser
python -m unittest test/ParserTesting.py
```

## How to use

The package is itself a python click application that can be run from the command line. So you can build the app and run it with:
```bash
hulk <filename>
```

Otherwise you can run it with:
```bash
python setup.py run test_file.hlk
```

## Authors

- Hector Miguel Rodriguez Sosa C411
- Sebastian Suarez Gomez C411
- Javier Rodriguez Sanchez C411

