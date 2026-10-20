"""Unit tests for commit-sleuth. Builds throwaway git repos as fixtures."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commit_sleuth import scanners, scoring, __version__  # noqa: E402


def make_repo(commits):
    """Create a temp git repo and commit (subject, body) tuples sequentially."""
    repo = tempfile.mkdtemp(prefix="sleuth_test_")
    def git(*a, env=None):
        subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True,
                       env={**os.environ, **(env or {})})
    git("init", "-q")
    git("config", "user.name", "Test User")
    git("config", "user.email", "test@example.com")
    for i, (subject, body) in enumerate(commits):
        with open(os.path.join(repo, f"f{i}.txt"), "w") as fh:
            fh.write(f"content {i}\n")
        git("add", ".")
        git("commit", "-q", "--allow-empty", "-m", subject, "-m", body)
    return repo


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo([
            ("Initial commit", "boilerplate"),
            ("Add login flow", "This change adds proper error handling \u2014 carefully."),
            ("Fix bug",
             "Co-Authored-By: Claude <noreply@anthropic.com>"),
            ("docs: update readme", "regular work"),
        ])

    def test_git_log_reads_all_commits(self):
        commits = scanners.git_log(self.repo)
        self.assertEqual(len(commits), 4)

    def test_trailer_detection_finds_agent(self):
        found = [c for c in scanners.git_log(self.repo) if scanners.trailer_hits(c)]
        self.assertEqual(len(found), 1)
        self.assertIn("co-authored-by: claude", (found[0]["subject"] + found[0]["body"]).lower())

    def test_em_dash_counted(self):
        em = [scanners.em_dash_count(c) for c in scanners.git_log(self.repo)]
        self.assertEqual(sum(em), 1)

    def test_conventional_commit_alone_scores_low(self):
        commit = {"hash": "x", "author": "a", "email": "e",
                 "subject": "docs: update readme", "body": ""}
        score, _ = scoring.score_commit(commit)
        self.assertLess(score, 20)


class ScoringTests(unittest.TestCase):
    def test_trailer_commit_flags_max_reason(self):
        commit = {"hash": "x", "author": "a", "email": "e", "subject": "Fix",
                  "body": "Co-Authored-By: Claude <noreply@anthropic.com>"}
        score, reasons = scoring.score_commit(commit)
        self.assertGreaterEqual(score, 40)
        self.assertTrue(any("trailer" in r for r in reasons))

    def test_verdict_explicit_when_trailer(self):
        v = scoring.verdict(0, [{"score": 40}])
        self.assertEqual(v, "AI-assisted commits are explicitly labeled in this history.")

    def test_verdict_clean_history(self):
        self.assertIn("human", scoring.verdict(0, []).lower())

    def test_full_report_structure(self):
        repo = make_repo([("Initial commit", "first"), ("Tweak", "Co-Authored-By: Claude <noreply@anthropic.com>")])
        report = scoring.score_repository(repo)
        self.assertEqual(report["commits_analyzed"], 2)
        self.assertEqual(len(report["flagged"]), 1)
        self.assertIn("explicitly labeled", report["verdict"])


class CliTests(unittest.TestCase):
    def test_json_output_runnable(self):
        repo = make_repo([("Initial commit", "hello"), ("Fix", "Co-Authored-By: Claude <noreply@anthropic.com>")])
        out = subprocess.run(
            [sys.executable, "-m", "commit_sleuth", repo, "--json"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..", "src")},
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        data = json.loads(out.stdout)
        self.assertEqual(data["commits_analyzed"], 2)
        self.assertIn("verdict", data)

    def test_text_output_contains_verdict(self):
        repo = make_repo([("Initial commit", "hello")])
        out = subprocess.run(
            [sys.executable, "-m", "commit_sleuth", repo],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..", "src")},
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("Verdict", out.stdout)

    def test_version_flag(self):
        out = subprocess.run(
            [sys.executable, "-m", "commit_sleuth", "--version"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..", "src")},
        )
        self.assertIn(__version__, out.stdout)


if __name__ == "__main__":
    unittest.main()
