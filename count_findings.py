#!/usr/bin/env python3
"""Count findings in an unslop report. Best effort, format-aware.

Usage: count_findings.py <report-path> <format>  (format: sarif|json|text)
Prints the finding count to stdout, or 0 on any problem, so the caller can
sum engines without special-casing failures.
"""
import json
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print(0)
        return 0
    path, fmt = sys.argv[1], sys.argv[2]
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        print(0)
        return 0

    try:
        if fmt == "sarif":
            print(sum(len(run.get("results", [])) for run in data.get("runs", [])))
            return 0
        # json: engines use different top-level keys for their finding list.
        for key in ("detections", "findings", "smells", "issues"):
            value = data.get(key)
            if isinstance(value, list):
                print(len(value))
                return 0
        print(0)
    except Exception:
        print(0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
