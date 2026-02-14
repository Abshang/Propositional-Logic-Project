# Propositional Logic Tools Suite

A comprehensive Python implementation of propositional logic tools including formula parsing, CNF conversion, Horn satisfiability checking, natural deduction rule application, and complete proof verification.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Phase 1: Formula Parser and Binary Tree Builder](#phase-1-formula-parser-and-binary-tree-builder)
- [Phase 2: CNF Converter](#phase-2-cnf-converter)
- [Phase 3: Horn Formula Satisfiability Checker](#phase-3-horn-formula-satisfiability-checker)
- [Phase 4: Natural Deduction Rule Applier](#phase-4-natural-deduction-rule-applier)
- [Phase 5: Natural Deduction Proof Checker](#phase-5-natural-deduction-proof-checker)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Technical Details](#technical-details)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project provides a complete toolkit for working with propositional logic formulas. It implements fundamental algorithms from logic and automated reasoning, suitable for educational purposes, logic programming, and automated theorem proving.

### Key Features

- **Formula Parsing**: Convert logical formulas into binary parse trees
- **CNF Conversion**: Transform formulas into Conjunctive Normal Form
- **Satisfiability Checking**: Determine if Horn formulas are satisfiable
- **Rule Application**: Apply natural deduction inference rules
- **Proof Verification**: Validate complete natural deduction proofs with scope management

## Project Structure

```
propositional-logic-tools/
├── phase1_parser.py           # Formula parser and tree builder
├── phase2_cnf.py              # CNF converter
├── phase3_horn_sat.py         # Horn satisfiability checker
├── phase4_rule_applier.py     # Natural deduction rule applier
├── phase5_proof_checker.py    # Complete proof checker
├── docs/
│   ├── phase1_documentation.pdf
│   ├── phase2_documentation.pdf
│   ├── phase3_documentation.pdf
│   ├── phase4_documentation.pdf
│   └── phase5_documentation.pdf
├── examples/
│   ├── formulas/
│   ├── cnf_examples/
│   ├── horn_formulas/
│   ├── rules/
│   └── proofs/
└── README.md
```

---

## Phase 1: Formula Parser and Binary Tree Builder

### Description

Parses propositional logic formulas and constructs binary parse trees based on operator precedence. Validates well-formed formulas (WFF) and provides tree visualization.

### Features

- Parse formulas from text files
- Build binary parse trees with correct operator precedence
- Validate well-formed formulas
- Visual tree output

### Input Format

```
((p ∧ q) → r)
```

### Output

```
Valid formula!
→
  ∧
    p
    q
  r
```

### Operator Precedence

1. Implication (→) - lowest precedence
2. Disjunction (∨)
3. Conjunction (∧)
4. Negation (¬) - highest precedence

### Usage

```bash
python phase1_parser.py
# Enter filename when prompted
```

### Key Algorithms

- **Binary tree construction**: O(n²) time complexity
- **Parentheses validation**: O(n) time complexity
- **WFF validation**: O(n) tree traversal

---

## Phase 2: CNF Converter

### Description

Converts propositional logic formulas into Conjunctive Normal Form (CNF) through systematic transformations: implication elimination, negation normalization, and distribution.

### Features

- Eliminate implication operators
- Apply De Morgan's laws
- Remove double negations
- Distribute disjunction over conjunction
- Iterative transformation until fixed point

### Transformation Steps

1. **Implication Elimination**: `A → B` ≡ `¬A ∨ B`
2. **Move Negations Inward**: Apply De Morgan's laws
   - `¬(A ∧ B)` ≡ `¬A ∨ ¬B`
   - `¬(A ∨ B)` ≡ `¬A ∧ ¬B`
3. **Remove Double Negations**: `¬¬A` ≡ `A`
4. **Distribute OR over AND**: `A ∨ (B ∧ C)` ≡ `(A ∨ B) ∧ (A ∨ C)`

### Example

**Input:**

```
((p → q) → r)
```

**Output:**

```
===================
(p ∨ r) ∧ (¬q ∨ r)
===================
```

### Usage

```bash
python phase2_cnf.py
# Enter filename when prompted
```

### Complexity

- **Time**: O(2^n) worst case (exponential due to distribution)
- **Space**: O(2^n) worst case
- **Typical cases**: Much better performance

---

## Phase 3: Horn Formula Satisfiability Checker

### Description

Determines satisfiability of Horn formulas using the unit propagation algorithm. Horn formulas are a restricted form of CNF with at most one positive literal per clause, enabling polynomial-time satisfiability checking.

### Features

- Parse Horn formulas in CNF with implications
- Validate Horn clause structure
- Apply unit propagation algorithm
- Determine satisfiability in polynomial time
- Output satisfying assignment

### Horn Clause Format

```
(p₁ ∧ p₂ ∧ ... ∧ pₙ) → q
```

Where p₁, p₂, ..., pₙ are positive literals (antecedents) and q is a positive literal or ⊥ (consequent).

### Example

**Input:**

```
(p → q) ∧ (q → r) ∧ (⊤ → p)
```

**Output:**

```
Satisfiable
p
q
r
```

### Usage

```bash
python phase3_horn_sat.py
# Enter filename when prompted
```

### Complexity

- **Time**: O(n·v) - polynomial time (n = clauses, v = variables)
- **Space**: O(n)
- **Comparison**: General SAT is NP-complete, Horn SAT is in P

### Applications

- Logic programming (Prolog)
- Datalog query languages
- Expert systems
- Type inference systems

---

## Phase 4: Natural Deduction Rule Applier

### Description

Applies natural deduction inference rules to formulas. Takes a set of formulas with line numbers and a rule specification, validates the rule application, and outputs the resulting formula.

### Supported Rules

| Rule                    | Notation | Description              |
| ----------------------- | -------- | ------------------------ |
| AND Introduction        | ∧i       | Combine two formulas     |
| AND Elimination 1       | ∧e1      | Extract left conjunct    |
| AND Elimination 2       | ∧e2      | Extract right conjunct   |
| Implication Elimination | →e       | Modus Ponens             |
| Negation Elimination    | ¬e       | Derive ⊥ from A and ¬A   |
| Double Negation Elim.   | ¬¬e      | Remove ¬¬                |
| Double Negation Intro.  | ¬¬i      | Add ¬¬                   |
| Modus Tollens           | MT       | Contrapositive reasoning |

### Input Format

```
[line_number]    [formula]
[line_number]    [formula]
[rule_name], [line1], [line2], ...
```

### Example

**Input file:**

```
1    p ∧ q
2    q → r
∧e1, 1
```

**Output:**

```
p
```

### Usage

```bash
python phase4_rule_applier.py
# Enter filename when prompted
```

### Key Features

- Tree-based formula comparison
- Rule validation
- Error detection and reporting
- Formula output with proper parenthesization

---

## Phase 5: Natural Deduction Proof Checker

### Description

Complete proof checker for natural deduction with full scope management. Validates entire proofs by checking each line against natural deduction rules, managing nested scopes for assumption-based reasoning.

### Supported Rules (15 Total)

**Elimination Rules:**

- ∧e1, ∧e2: AND elimination
- ∨e: OR elimination (with two scopes)
- →e: Implication elimination (Modus Ponens)
- ¬e: Negation elimination
- ¬¬e: Double negation elimination
- ⊥e: False elimination (ex falso quodlibet)

**Introduction Rules:**

- ∧i: AND introduction
- ∨i1, ∨i2: OR introduction
- →i: Implication introduction (requires scope)
- ¬i: Negation introduction (requires scope)
- ¬¬i: Double negation introduction

**Derived and Classical Rules:**

- MT: Modus Tollens
- PBC: Proof by Contradiction
- LEM: Law of Excluded Middle
- Copy: Copy rule

### Scope Management

Proofs can contain nested scopes for temporary assumptions:

```
BeginScope
    [assumption]
    [derivations...]
EndScope
```

### Input Format

```
[line_num]    [formula]    [rule], [refs]
BeginScope
[line_num]    [formula]    [rule], [refs]
...
EndScope
[line_num]    [formula]    [rule], [refs]
```

### Example Proof

**Input:**

```
1    p ∧ q        Premise
2    p            ∧e1, 1
BeginScope
3    r            Assumption
4    p ∧ r        ∧i, 2, 3
EndScope
5    r → (p ∧ r)  →i, 3-4
```

**Output:**

```
Valid Deduction
```

### Usage

```bash
python phase5_proof_checker.py
# Enter filename when prompted
```

### Key Features

- **Scope tracking**: Nested assumption contexts
- **Accessibility checking**: Ensures proper variable scoping
- **Complete validation**: All 15 natural deduction rules
- **Clear error reporting**: Line-by-line validation with error messages

### Complexity

- **Time**: O(n·(m + d + k)) where n = lines, m = formula length, d = scope depth, k = validation cost
- **Space**: O(n·m + s) where s = number of scopes

---

## Installation

### Requirements

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

### Setup

# Run any phase

python phase1_parser.py
python phase2_cnf.py
python phase3_horn_sat.py
python phase4_rule_applier.py
python phase5_proof_checker.py

```

---

## Usage Examples

### Phase 1: Parse a Formula

**formula.txt:**
```

((p ∧ q) → (r ∨ s))

````

**Command:**
```bash
python phase1_parser.py
# Enter: formula.txt
````

**Output:**

```
Valid formula!
→
  ∧
    p
    q
  ∨
    r
    s
```

---

### Phase 2: Convert to CNF

**formula.txt:**

```
(p → (q ∧ r))
```

**Command:**

```bash
python phase2_cnf.py
# Enter: formula.txt
```

**Output:**

```
===================
(¬p ∨ q) ∧ (¬p ∨ r)
===================
```

---

### Phase 3: Check Horn Satisfiability

**horn.txt:**

```
(p → q) ∧ (q → r) ∧ (⊤ → p)
```

**Command:**

```bash
python phase3_horn_sat.py
# Enter: horn.txt
```

**Output:**

```
Satisfiable
p
q
r
```

---

### Phase 4: Apply a Rule

**rule.txt:**

```
1    p ∧ q
2    q → r
∧e2, 1
```

**Command:**

```bash
python phase4_rule_applier.py
# Enter: rule.txt
```

**Output:**

```
q
```

---

### Phase 5: Check a Proof

**proof.txt:**

```
1    p → q        Premise
2    q → r        Premise
3    p            Premise
4    q            →e, 1, 3
5    r            →e, 2, 4
```

**Command:**

```bash
python phase5_proof_checker.py
# Enter: proof.txt
```

**Output:**

```
Valid Deduction
```

---

## Technical Details

### Design Principles

1. **Modularity**: Each phase is self-contained
2. **Tree-based representation**: Formulas stored as binary trees
3. **Recursive algorithms**: Natural for tree structures
4. **Clear separation**: Parsing, validation, and execution separated

### Data Structures

**Node Class** (used in all phases):

```python
class Node:
    def __init__(self, key, left=None, right=None):
        self.data = key           # Operator or variable
        self.left: Node | None = left   # Left child
        self.right: Node | None = right  # Right child
```

### Algorithm Complexities

| Phase   | Time Complexity | Space Complexity | Problem Class |
| ------- | --------------- | ---------------- | ------------- |
| Phase 1 | O(n²)           | O(n)             | P             |
| Phase 2 | O(2^n) worst    | O(2^n) worst     | EXPTIME       |
| Phase 3 | O(n·v)          | O(n)             | P             |
| Phase 4 | O(n·m)          | O(n·k)           | P             |
| Phase 5 | O(n·(m+d+k))    | O(n·m+s)         | P             |

---

## Educational Value

This project demonstrates:

- **Parsing techniques**: Recursive descent parsing with operator precedence
- **Tree algorithms**: Construction, traversal, and transformation
- **Logic fundamentals**: WFF validation, CNF conversion, satisfiability
- **Proof theory**: Natural deduction, inference rules, scope management
- **Algorithm analysis**: Time/space complexity, problem classification

### Learning Path

1. **Phase 1**: Understand formula structure and tree representation
2. **Phase 2**: Learn logical equivalences and transformations
3. **Phase 3**: Study satisfiability and efficient algorithms
4. **Phase 4**: Explore inference rules and proof steps
5. **Phase 5**: Master complete proof systems and scope management

---

## Comparison with Related Tools

| Feature           | This Project | Prover9    | Coq        | Z3         |
| ----------------- | ------------ | ---------- | ---------- | ---------- |
| Natural Deduction | ✅ Full      | ❌ No      | ✅ Yes     | ❌ No      |
| CNF Conversion    | ✅ Yes       | ✅ Yes     | ✅ Yes     | ✅ Yes     |
| Horn SAT          | ✅ Yes       | ✅ Yes     | ❌ No      | ✅ Yes     |
| Educational Focus | ✅ Yes       | ❌ No      | ⚠️ Partial | ❌ No      |
| Standalone        | ✅ Yes       | ✅ Yes     | ❌ No      | ✅ Yes     |
| Interactive       | ❌ No        | ⚠️ Limited | ✅ Yes     | ⚠️ Limited |

---

## Future Enhancements

### Planned Features

- [ ] **GUI Interface**: Visual proof construction
- [ ] **Proof Search**: Automatic theorem proving
- [ ] **LaTeX Export**: Generate formatted proofs
- [ ] **DIMACS Support**: Integration with SAT solvers
- [ ] **Tseitin Transformation**: Avoid exponential blowup in CNF
- [ ] **First-Order Logic**: Extend beyond propositional logic
- [ ] **Proof Tactics**: Higher-level proof strategies

### Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes
- New features
- Documentation improvements
- Additional examples
- Test cases

---

## Documentation

Complete documentation for each phase is available in the `docs/` directory:

- **Phase 1**: Formula Parser and Binary Tree Builder (20 pages)
- **Phase 2**: CNF Converter (25 pages)
- **Phase 3**: Horn Formula Satisfiability Checker (15 pages)
- **Phase 4**: Natural Deduction Rule Applier (18 pages)
- **Phase 5**: Natural Deduction Proof Checker (20 pages)

Each document includes:

- Detailed algorithm explanations
- Complexity analysis
- Complete examples
- Full source code
- References

---

## References

### Books

1. **Mendelson, E.** (2015). _Introduction to Mathematical Logic_ (6th ed.). CRC Press.
2. **Enderton, H. B.** (2001). _A Mathematical Introduction to Logic_ (2nd ed.). Academic Press.
3. **Huth, M., & Ryan, M.** (2004). _Logic in Computer Science_ (2nd ed.). Cambridge University Press.
4. **Harrison, J.** (2009). _Handbook of Practical Logic and Automated Reasoning_. Cambridge University Press.

### Papers

1. **Gentzen, G.** (1935). Untersuchungen über das logische Schließen. _Mathematische Zeitschrift_, 39(2), 176-210.
2. **Dowling, W. F., & Gallier, J. H.** (1984). Linear-time algorithms for testing the satisfiability of propositional Horn formulae. _The Journal of Logic Programming_, 1(3), 267-284.

---

## Author

**Fatemeh Abshang**  
Spring 2024-2025

---

## Acknowledgments

Special thanks to:

- The logic and automated reasoning community
- Open source contributors
- Educational institutions supporting logic education

---
