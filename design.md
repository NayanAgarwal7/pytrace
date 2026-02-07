# PyTrace — Design Notes

This document explains the technical decisions behind PyTrace and the trade-offs involved.

---

## Core Design Goal

Make Python execution **observable and deterministic**.

Every explanation must be:
- reproducible
- rule-based
- directly derived from interpreter behavior

---

## Static + Dynamic Analysis

### Static (AST)
- The source file is parsed once using 'ast'
- Loops, functions, and conditionals are recorded by line number
- This provides structural context that runtime events alone do not expose

### Dynamic (Runtime)
- 'sys.settrace' captures line, call, and return events
- Frame objects provide access to local scope and execution state

Combining both answers:
- *what executed* (runtime)
- *where in structure* (static)

---

## Why 'sys.settrace'

Chosen because:
- Built into CPython
- Captures all execution events
- Exposes frame-level information

Trade-off:
- Significant slowdown (~10x)
- Acceptable for analysis and education

---

## State Tracking Strategy

Tracked data:
- variable names (strings only)
- frame identity
- line number
- iteration count

Not tracked:
- object values
- equality comparisons
- object representations

Reason:
Calling 'repr()' or comparing objects can be unsafe or expensive.

---

## Iteration Counting

Each '(frame_id, line_number)' pair maintains its own counter.

This avoids ambiguity in cases like recursion or nested loops where the same line executes in different frames.

---

## Explanation Rules

Explanations are:
- technical
- passive voice
- descriptive only

Examples:
- “Variable x created.”
- “Iteration 2 of loop: variable i created.”

No intent, no interpretation.

---

## Known Limitations

- Function parameters are not detected as “created”
- Class-based code is not analyzed
- Imports are not traced across files

These are deliberate scope limits.

---

## Summary

PyTrace prioritizes:
- correctness over completeness
- transparency over intelligence
- systems understanding over surface-level output

It is an educational systems project focused on Python’s execution model.

