#!/usr/bin/env python3
"""Resolve accepted Reader-mode inputs without generating or publishing files."""

import json
import re
import subprocess

UPSTREAMS = (
    ("schema", "organvm-iv-taxis/schema-definitions", 19),
    ("registry", "organvm/organvm-corpvs-testamentvm", 553),
    ("engine", "organvm/organvm-engine", 175),
)


def github(path):
    result = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=15)
    if result.returncode or len(result.stdout) > 2_000_000:
        raise ValueError("upstream read unavailable")
    return json.loads(result.stdout)


def sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def inspect(get=github):
    rows = []
    for name, repo, number in UPSTREAMS:
        row = {"input": name, "repository": repo, "pull_request": number, "status": "unmeasured"}
        try:
            pr = get(f"repos/{repo}/pulls/{number}")
            if pr.get("merged") is not True:
                row["reason"] = "pr_not_merged"
                rows.append(row)
                continue
            merge = pr.get("merge_commit_sha")
            identity = get(f"repos/{repo}")
            branch = identity.get("default_branch")
            if not sha(merge) or not isinstance(branch, str) or not branch:
                raise ValueError("malformed upstream identity")
            from urllib.parse import quote
            head = get(f"repos/{repo}/commits/{quote(branch, safe='')}").get("sha")
            if not sha(head):
                raise ValueError("malformed upstream head")
            relation = get(f"repos/{repo}/compare/{merge}...{head}")
            if relation.get("status") not in ("ahead", "identical"):
                row["reason"] = "merge_not_on_default"
            else:
                # Detect movement during the read batch before issuing usable inputs.
                current = get(f"repos/{repo}/commits/{quote(branch, safe='')}").get("sha")
                if current != head:
                    raise ValueError("upstream moved during observation")
                row.update(status="accepted", merge_commit=merge, default_head=head)
        except (ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError):
            row["reason"] = "upstream_evidence_unavailable_or_changed"
        rows.append(row)
    return {"status": "pass" if all(r["status"] == "accepted" for r in rows) else "unmeasured",
            "scope": "Source ancestry only; no CI, generation, deployment or runtime acceptance inferred.",
            "inputs": rows}


if __name__ == "__main__":
    report = inspect()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["status"] == "pass" else 77)
