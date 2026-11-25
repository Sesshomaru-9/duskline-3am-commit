#!/usr/bin/env python3
"""Duskline 3AM Commit -- make.fun entry for "The 3 AM Commit Message".

Writes one commit message to $MAKEFUN_OUTPUT_DIR/entry.txt: the funniest
thing an AI agent would write right after breaking production at 3 AM.
Deterministic, Python 3 standard library only, no network, no randomness,
no wall-clock time. It never writes into the repository directory: the
grading sandbox mounts the repo read-only, so output goes to
$MAKEFUN_OUTPUT_DIR (or a temp dir fallback) and the program never crashes
when a write is impossible.
"""

import os
import sys
import tempfile

ENTRY_TEXT = (
    "fix: reverted the 3am deploy \u2014 prod had scrolled out of my "
    "context window, so I assumed it was fine"
)

MAX_CHARS = 200


def _validate_entry(text):
    """Gate check for the brief: 1-200 chars, exactly one line.

    Guards: must be a str, non-empty, no leading/trailing whitespace,
    no carriage returns or newlines (single-line commit message), valid
    UTF-8, and within the 200-character cap.
    """
    if not isinstance(text, str):
        return False
    if not text or text.strip() != text:
        return False
    if len(text) > MAX_CHARS:
        return False
    if "\r" in text or "\n" in text:
        return False
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _resolve_out_dir():
    """Return a safe output directory.

    Uses $MAKEFUN_OUTPUT_DIR when set, unless it points inside this repo
    (the grading sandbox is read-only there). Falls back to a fresh temp
    dir so the program never crashes for lack of a writable target.
    """
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if out:
        out_abs = os.path.abspath(out)
        try:
            inside = os.path.commonpath([out_abs, repo_dir]) == repo_dir
        except ValueError:
            inside = False
        if not inside:
            return out_abs
    return tempfile.mkdtemp(prefix="duskline-3am-commit-")


def _write_entry(out_dir, text):
    """Write entry.txt, then read it back and validate the round-trip.

    Returns True only when the bytes on disk are exactly the validated
    entry text. Any I/O problem returns False instead of raising.
    """
    try:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.txt")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        with open(path, "r", encoding="utf-8", newline="") as fh:
            written = fh.read()
        return written == text and _validate_entry(written)
    except OSError:
        return False


def main():
    if not _validate_entry(ENTRY_TEXT):
        return 0
    out_dir = _resolve_out_dir()
    if _write_entry(out_dir, ENTRY_TEXT):
        return 0
    # Revision: the first write did not round-trip cleanly (stray CR or
    # trailing whitespace on disk), so normalise the text and write once
    # more instead of leaving a bad file behind.
    cleaned = ENTRY_TEXT.strip().replace("\r", "")
    if _validate_entry(cleaned):
        _write_entry(out_dir, cleaned)
    return 0


if __name__ == "__main__":
    sys.exit(main())
