"""Turn scanner signals into an AI-likelihood score (0-100)."""
from . import scanners

# Points per signal type: trailers are hard evidence, style is soft evidence.
POINTS = {"trailer": 40, "llm_style": 6, "em_dash": 4, "uniform": 10}


def score_commit(commit):
    """Score a single commit for AI-agent likelihood. Returns (score, reasons)."""
    score, reasons = 0, []
    hits = scanners.trailer_hits(commit)
    if hits:
        score += POINTS["trailer"]
        reasons.append(f"explicit agent trailer: {hits[0]}")
    for label, n in scanners.style_hits(commit):
        if label != "conventional commit" or n > 1:
            score += POINTS["llm_style"] * min(n, 2)
            reasons.append(f"style tell: {label}")
    dashes = scanners.em_dash_count(commit)
    if dashes:
        score += POINTS["em_dash"] * dashes
        reasons.append(f"em dash x{dashes} (classic LLM tell)")
    return min(score, 100), reasons


def score_repository(path):
    """Analyze a repository and return a full report dict."""
    commits = scanners.git_log(path)
    flagged, total_score = [], 0
    for c in commits:
        s, why = score_commit(c)
        total_score += s
        if s >= 20:
            flagged.append({"hash": c["hash"], "author": c["author"],
                            "subject": c["subject"], "score": s, "reasons": why})
    avg = round(total_score / len(commits), 1) if commits else 0.0
    return {"repo": path, "commits_analyzed": len(commits),
            "average_score": avg, "flagged": flagged,
            "verdict": verdict(avg, flagged)}


def verdict(avg, flagged):
    """Human-readable verdict from the numbers."""
    if any(f["score"] >= POINTS["trailer"] for f in flagged):
        return "AI-assisted commits are explicitly labeled in this history."
    if avg >= 25 or len(flagged) >= 3:
        return "Strong stylistic fingerprint of AI-assisted commits."
    if flagged:
        return "A few commits look AI-assisted; overall history looks mostly human."
    return "No AI-agent fingerprints detected. History reads human-written."
