"""Command-line interface for commit-sleuth."""
import argparse
import json
import sys

from . import __version__, scoring


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="commit-sleuth",
        description="Detect AI-agent fingerprints in a repository's git history.")
    parser.add_argument("path", help="Path to a local git repository")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        report = scoring.score_repository(args.path)
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        print(f"error: not a readable git repository ({args.path})", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print("error: git executable not found on PATH", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"commit-sleuth v{__version__}")
        print(f"Repo: {report['repo']}  ({report['commits_analyzed']} commits analyzed)")
        print(f"Average AI-likelihood score: {report['average_score']}/100")
        print(f"Verdict: {report['verdict']}")
        if report["flagged"]:
            print("\nFlagged commits:")
            for f in report["flagged"]:
                print(f"  [{f['score']:3d}] {f['hash'][:9]}  {f['subject'][:60]}")
                for r in f["reasons"]:
                    print(f"         - {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
