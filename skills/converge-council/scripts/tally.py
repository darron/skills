"""Validate coordinator-owned ballots and tally family-balanced Borda votes."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path


def unique_strings(value, name, minimum=0):
    if (not isinstance(value, list) or len(value) < minimum
            or any(not isinstance(x, str) or not x.strip() for x in value)
            or len(set(value)) != len(value)):
        raise ValueError(f"{name} must contain unique nonempty strings")
    return value


def tally(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    labels = unique_strings(data.get("candidates"), "candidates", minimum=2)
    roster = data.get("reviewers")
    ballots = data.get("ballots")
    if not isinstance(roster, list) or not isinstance(ballots, list):
        raise ValueError("reviewers and ballots must be arrays")
    reviewers = {}
    for r in roster:
        if not isinstance(r, dict):
            raise ValueError("reviewer must be an object")
        rid, family = r.get("id"), r.get("family")
        if not isinstance(rid, str) or not rid.strip() or rid in reviewers:
            raise ValueError("reviewer IDs must be unique nonempty strings")
        if not isinstance(family, str) or not family.strip():
            raise ValueError("reviewer family is required")
        if r.get("context") not in ("fresh", "reused-author"):
            raise ValueError("reviewer context must be fresh or reused-author")
        reviewers[rid] = r
    counts = Counter(b.get("reviewer") for b in ballots
                     if isinstance(b, dict) and isinstance(b.get("reviewer"), str))
    rejected, valid = [], []
    families = defaultdict(list)
    for index, b in enumerate(ballots):
        rid = b.get("reviewer") if isinstance(b, dict) else None
        reason = None
        if not isinstance(rid, str) or rid not in reviewers:
            reason = "unknown_reviewer"
        elif counts[rid] != 1:
            reason = "duplicate_reviewer"
        elif reviewers[rid]["context"] != "fresh":
            reason = "reused_author_context"
        else:
            rank = b.get("ranking")
            if (not isinstance(rank, list) or len(rank) != len(labels)
                    or any(not isinstance(x, str) for x in rank)
                    or set(rank) != set(labels)):
                reason = "ranking_must_include_every_candidate_once"
        if reason:
            rejected.append({"index": index, "reviewer": rid, "reason": reason})
            continue
        score = {label: Fraction(len(labels) - 1 - i, len(labels) - 1)
                 for i, label in enumerate(b["ranking"])}
        families[reviewers[rid]["family"]].append(score)
        valid.append({"reviewer": rid, "family": reviewers[rid]["family"],
                      "ranking": b["ranking"]})
    means = {f: {label: sum(s[label] for s in scores) / len(scores)
                 for label in labels} for f, scores in families.items()}
    combined = {label: sum(m[label] for m in means.values()) / len(means)
                for label in labels} if means else {}
    # Use exact fractions for leaders, rounding only for display.
    leaders = [label for label in labels
               if combined and combined[label] == max(combined.values())]
    coverage = ("insufficient_reviewers" if len(valid) < 2 else
                "single_family" if len(means) < 2 else "cross_family")
    return {
        "method": "normalized_borda_equal_family_weight",
        "coverage": coverage,
        "valid_ballots": valid,
        "rejected_ballots": rejected,
        "missing_reviewers": [rid for rid in reviewers if rid not in counts],
        "family_scores": {f: {k: float(v) for k, v in m.items()}
                          for f, m in means.items()},
        "scores": {k: float(v) for k, v in combined.items()},
        "preference_leaders": leaders,
        "tie": len(leaders) > 1,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("votes", type=Path)
    args = parser.parse_args()
    try:
        result = tally(json.loads(args.votes.read_text()))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Invalid tally input: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
