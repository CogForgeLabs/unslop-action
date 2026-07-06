#!/usr/bin/env python3
"""Upload the merged SARIF + run metadata to the Unslop GitHub App backend.

Invoked by action.yml's "Upload to Unslop App" step when app-upload is enabled.
Best-effort by design: the App decides gating / PR comments / SARIF upload
server-side by plan, so any failure here is logged and the job continues (the
local `--fail-on` gate still applies independently). Reads configuration from the
environment set by the step; uses only the Python standard library.
"""
import json
import os
import time
import urllib.error
import urllib.request


def main() -> None:
    engines = [e.strip() for e in os.environ.get("UNSLOP_ENGINES", "").split(",") if e.strip()]

    # Merge each engine's SARIF runs into one document for the App.
    merged = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [],
    }
    for engine in engines:
        try:
            with open(f"{engine}.sarif", encoding="utf-8") as fh:
                doc = json.load(fh)
            merged["runs"].extend(doc.get("runs", []))
        except Exception:
            pass  # a missing/invalid engine report just contributes no runs

    # PR number + head sha from the event payload (fall back to the push sha).
    pr = None
    sha = os.environ.get("GITHUB_SHA")
    try:
        with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as fh:
            event = json.load(fh)
        if event.get("pull_request"):
            pr = event["pull_request"].get("number")
            sha = event["pull_request"].get("head", {}).get("sha", sha)
    except Exception:
        pass

    payload = {
        "repo": os.environ.get("GITHUB_REPOSITORY", ""),
        "ref": os.environ.get("GITHUB_REF", ""),
        "sha": sha,
        "pr": pr,
        "fail_on": os.environ.get("UNSLOP_FAIL_ON", "none"),
        "engines": engines,
        "run": {"ts": int(time.time())},
        "sarif": merged,
    }

    endpoint = os.environ["UNSLOP_APP_ENDPOINT"].rstrip("/") + "/api/results"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["UNSLOP_UPLOAD_TOKEN"],
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            print(f"unslop app: {resp.status} {resp.read(200).decode('utf-8', 'replace')}")
    except urllib.error.HTTPError as ex:
        print(f"unslop app: HTTP {ex.code} — reporting skipped (job continues).")
    except Exception as ex:  # noqa: BLE001 — never fail the job on a reporting error
        print(f"unslop app: upload failed ({ex}) — reporting skipped (job continues).")


if __name__ == "__main__":
    main()
