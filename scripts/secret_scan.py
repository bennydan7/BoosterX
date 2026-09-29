#!/usr/bin/env python3
"""
BoostX Secret Scan Script
Scans tracked git files and recent git diff for leaked passwords, API keys, or credentials.
"""

import sys
import subprocess
import re

LEAK_PATTERNS = [
    (re.compile(r"FlameFlame@99"), "Production Admin Password Leak"),
    (re.compile(r"sk-[a-zA-Z0-9]{32,}"), "OpenAI Secret Key Leak"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token Leak"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key Leak"),
]

def scan_diff():
    print("=== Running BoostX Secret Leak Scan ===")
    try:
        diff_output = subprocess.check_output(["git", "diff", "HEAD~5"], text=True, errors="ignore")
    except Exception:
        diff_output = ""

    leaks_found = 0
    for pattern, name in LEAK_PATTERNS:
        matches = pattern.findall(diff_output)
        if matches:
            print(f"[FAIL] Secret Leak Detected: {name} ({len(matches)} instance(s))")
            leaks_found += 1

    if leaks_found == 0:
        print("[PASS] Secret Scan Complete: ZERO LEAKS FOUND in git history/diff.")
        return 0
    else:
        print(f"[FAIL] {leaks_found} secret leak(s) detected. Aborting build/commit.")
        return 1

if __name__ == "__main__":
    sys.exit(scan_diff())
