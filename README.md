# PyTrace — Python Execution Tracer

PyTrace is a Python execution tracer that explains what changes during execution and where it happens in the program structure.

It combines:
- runtime tracing using 'sys.settrace'
- static structure analysis using Python’s 'ast' module

The goal is to make Python execution flow explicit, without guessing or interpretation.

---

## What PyTrace Does

- Traces line-by-line execution of a Python program
- Detects variable creation inside loops, functions, and conditionals
- Tracks call stack depth and iteration counts
- Explains events using fixed, rule-based logic (no AI, no heuristics)

Example explanation:
Iteration 3 of loop: variable i created.

---

## How It Works 

1. The source file is parsed once using the ast module to understand structure.
2. The program is executed under sys.settrace.
3. For every runtime event, PyTrace:
   - captures frame state
   - matches it with static context
   - generates a deterministic explanation

---

## Installation (Windows)

Requirements:
- Python 3.8+

Steps:
git clone https://github.com/NayanAgarwal7/pytrace
cd pytrace


No external dependencies are required.
---

## Usage

Basic execution trace:
python -m pytrace examples/loop.py


With explanations enabled:
python -m pytrace examples/loop.py --explain


---

## Project Structure

pytrace/
│
├── pytrace/
│ ├── main.py    # Entry point
│ ├── tracer.py    # sys.settrace logic
│ ├── state.py     # Runtime state tracking
│ ├── ast_parser.py    # Static AST analysis
│ └── explainer.py     # Rule-based explanations
├── examples/     # Test programs
├── design.md   # Design decisions
└── README.md


---

## Limitations

- Tracks **variable creation only**, not value mutation
- No support for classes or object methods
- No async / threading support
- Designed for analysis and learning, not production debugging

---

## Why PyTrace

Most debuggers show *where* execution is.
PyTrace explains *what changed* and *why*, using program structure.
