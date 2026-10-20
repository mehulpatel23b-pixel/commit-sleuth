<div align="center">

# ⚖️ commit-sleuth

**Detect AI-agent fingerprints in a repository's git history.**

*Co-Authored-By trailers, LLM style tells, and em-dash habits — quantified.*

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Tests](https://img.shields.io/badge/tests-11%20passing-brightgreen.svg)](./tests)
[![Dependencies](https://img.shields.io/badge/dependencies-none-success.svg)](./requirements.txt)

</div>

---

## 🤔 Why?

AI coding agents now author a big share of commits on GitHub. Most teams have
**no visibility** into which commits were agent-assisted, because trailers get
stripped, message styles blur, and nobody audits the log by hand.

`commit-sleuth` reads the git history of any local repository and scores each
commit for AI-agent likelihood, using two classes of evidence:

| Evidence class | Examples | Weight |
|---|---|---|
| **Hard** | `Co-Authored-By: Claude`, Copilot/Gemini/Codex trailers | 40 pts |
| **Soft (style)** | "This change adds...", uniform conventional-commit formatting, [em dash density — the classic LLM tell](https://arxiv.org) | 4–12 pts |

It is a **transparency tool, not a judge**: a high score means "worth a look",
not a verdict about authorship.

## 🚀 Install

```bash
git clone https://github.com/mehulpatel23b-pixel/commit-sleuth.git
cd commit-sleuth
```

Zero dependencies — pure Python standard library (Python 3.9+). No pip install needed.

## 🛠️ Usage

```bash
# Human-readable report (default)
python3 -m commit_sleuth /path/to/any/git/repo

# Machine-readable output for CI
python3 -m commit_sleuth /path/to/repo --json

# Version
python3 -m commit_sleuth --version
```

### Sample output

```
commit-sleuth v1.0.0
Repo: /src/my-project  (214 commits analyzed)
Average AI-likelihood score: 18.4/100
Verdict: A few commits look AI-assisted; overall history looks mostly human.

Flagged commits:
  [ 46] a1b2c3d4e  Refactor retry logic for edge cases
         - explicit agent trailer: co-authored-by: claude
         - style tell: llm correctness idiom
```

## 🧩 How it works

1. **Read** the last 500 commits via `git log` (no network access, no tokens).
2. **Scan** each commit message for explicit agent trailers and stylistic tells.
3. **Score** each commit 0-100 (hard evidence dominates soft style signals).
4. **Report** the average, the flagged commits, and a plain-English verdict.

## 📁 Project structure

```
commit-sleuth/
├── src/commit_sleuth/
│   ├── scanners.py    # git reading + pattern detection
│   ├── scoring.py     # evidence → likelihood score
│   ├── cli.py         # argument parsing, text/JSON output
│   ├── __main__.py    # python3 -m commit_sleuth entry
│   └── __init__.py    # version metadata
├── tests/
│   └── test_commit_sleuth.py   # 11 unit tests, temp-repo fixtures
├── requirements.txt   # (empty: stdlib only)
├── LICENSE
└── README.md
```

Run the test suite:

```bash
python3 -m unittest discover -s tests
```

## 🔒 Security & privacy

- Runs **entirely locally** — never sends commits, diffs, or any data anywhere.
- Reads commit **messages only**; it does not inspect file contents of your code.
- Perfect for auditing a clone before you interview a candidate, review a vendor
  submission, or check what your own agents have been quietly committing.

## 📄 License

MIT © Mehul Patel — see [LICENSE](./LICENSE)
