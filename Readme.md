# SI2002 Formal Languages - Assignment 2
## Subset Construction (Kozen, Lecture 6)

**name:** Mateo Cadavid Ramirez

## Environment

- **Operating System:** Windows (tested on Windows 10/11, PowerShell)
- **Programming language:** Python 3.14.8
- **Tools / libraries:** Standard Python interpreter (`python3`), plus the standard library module `re` (regular expressions, included with Python — no installation needed). Optionally, the `matplotlib` package is used to automatically draw the resulting DFA as a diagram when the program runs (see "About the diagrams" below). Install it once with:

```bash
pip install matplotlib
```

No other external tools or libraries are required.

## How to run

The program reads all input from standard input (stdin) and writes the resulting DFA table to standard output (stdout), following the format described in the assignment. Every time it runs, it also automatically pops up a window with a diagram of the resulting DFA for each case — no extra steps or flags needed (see "About the diagrams" below).

**On Windows (PowerShell):**

```powershell
Get-Content test1.txt | python3 taller2.py
```

**On Linux / macOS (or Windows using cmd.exe):**

```bash
python3 taller2.py < test1.txt
```

Where `test1.txt` is a text file containing the input cases in the format specified by the assignment: number of cases, then for each case, in order: number of states `n`, the set of initial states `S`, the alphabet `Σ`, the set of final states `F`, and `n` lines with the transition table (each cell a set, written as `{1 5}`, or `0` for the empty set `∅`).

## Explanation of the algorithm

The implementation follows the **Subset Construction** presented in Kozen (1997), *Automata and Computability*, Lecture 6 ("The Subset Construction").

Given an NFA `N = (Q_N, Σ, Δ, S, F_N)`, the algorithm builds an equivalent DFA `M = (Q_M, Σ, δ_M, s_M, F_M)` where, in principle:

- `Q_M = 2^(Q_N)` — every state of `M` is a **subset** of the states of `N`.
- `δ_M(A, a) = Δ̂(A, a) = ⋃_{q ∈ A} Δ(q, a)` for `A ⊆ Q_N` — from a "state" `A` (a set of `N`-states), reading symbol `a`, `M` moves to the **union** of what every individual state in `A` can reach under `a`.
- `s_M = S` — the start state of `M` is the set of start states of `N`.
- `F_M = { A ⊆ Q_N | A ∩ F_N ≠ ∅ }` — a subset `A` is accepting in `M` if it contains **at least one** accepting state of `N`.

Theorem 6.4 in Kozen proves `L(M) = L(N)`, i.e., this construction always produces an equivalent DFA.

### Avoiding the full powerset (lazy / on-the-fly construction)

Building all `2^n` subsets up front is wasteful, since most are usually unreachable from `s_M`. Instead, the implementation explores **only the reachable subsets**, using a breadth-first search (BFS) starting from `s_M = S`:

1. Start with the initial subset `S` as the only known state of `M`.
2. For each symbol `a` of the alphabet, compute `δ_M(A, a)` as the union of `Δ(q, a)` over every `q ∈ A`.
3. If the resulting subset has not been seen before, add it to the queue to be processed the same way.
4. Repeat until the queue is empty (i.e., a fixed point is reached: no new reachable subsets appear).

This is exactly the example worked out informally in Kozen Lecture 13 for an NFA accepting strings containing `aba`: out of `2^4 = 16` possible subsets, only 6 were reachable and therefore relevant.

### Implementation details

- Each NFA transition `Δ(q, a)` is stored as a Python dictionary `Delta[(q, a)] = frozenset(...)`. `frozenset` (an immutable set) is used instead of a regular `set` because the states of the DFA `M` are themselves **sets of `N`-states**, and only immutable, hashable objects can be stored in a Python `set`/used as dictionary keys — which is required to detect when a newly computed subset has already been seen before.
- Parsing each row of the transition table requires separating tokens that may contain embedded spaces inside curly braces (e.g. `1 {1 5} 0`), so a regular expression is used: `re.findall(r'\{[^}]*\}|\S+', line)`, which matches either a full `{...}` group (keeping its contents together) or a plain space-free token (a number). This correctly splits `"1 {1 5} 0"` into `['1', '{1 5}', '0']`.
- The empty set `∅`, written as `0` in the input, is parsed as `frozenset()`.
- States of the resulting DFA `M` are renamed to simple consecutive integers (`0, 1, 2, ...`) in the order they are discovered by the BFS, as explicitly allowed by the assignment ("you may rename the states of M for the sake of readability"). The output also shows, for traceability, which subset of `N`-states each renamed state corresponds to.

### Output format

For each test case, the program prints a table of the resulting DFA `M`: one row per state, with the row's transitions under each symbol of the alphabet (in the same order as the alphabet was given). The initial state is marked with `->` and every accepting state is marked with `(F)` (both marks appear together when the initial state is also accepting). Each row ends with a comment showing which subset of original `N`-states that renamed state represents, e.g.:

```
   a b
->     0   1 2        ; 0 = {3,5}
   (F) 1   3 4        ; 1 = {1,2,4,5}
   (F) 2   5 6        ; 2 = {4}
```

## Optional feature: printing automata as diagrams

As an additional feature (Section 4 of the assignment, optional), the program **automatically draws a diagram** of the resulting DFA `M` for every test case, each time it runs — right after printing the required table, a window pops up showing all the diagrams side by side.

Each diagram is drawn with `matplotlib` (circles for states, double circles for accepting states, an arrow for the initial state, and curved arrows with labels for transitions), directly in a pop-up window — nothing is saved to disk, and there is nothing to paste anywhere.

This never interferes with the required output: the diagram window only opens **after** the required table has already been printed to stdout, so the automatic grader — which only reads stdout — is unaffected either way. If `matplotlib` is not installed, the program prints a short warning to stderr and simply skips the diagram, without changing the required output.

## Files included

- `taller2.py` — main implementation.
- `README.md` — this file.
- `Test1.TXT` - the dataset.