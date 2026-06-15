#!/usr/bin/env python3
"""
check_deck.py - Structural smoke-test for Anki TSV decks.

This is the *mechanical* audit gate. It checks that a deck will IMPORT CLEANLY.
It does NOT judge card quality (atomicity, cloze-vs-Q&A choice, interference,
answer-telegraphing) - that needs per-card reasoning by the model or a human.
A green result here means "the file is well-formed", NOT "the cards are good".

This lives in scripts/ (not evals/) on purpose: the packager ships scripts/ but
excludes evals/, so putting it here makes it runnable at runtime by an installed
skill, not just by a maintainer testing offline.

Usage:
    python scripts/check_deck.py <file-or-directory> [more files...]
    python scripts/check_deck.py /mnt/user-data/outputs/

Exit code is 0 if everything passes, 1 if any file has problems.

Checks per file:
  - required headers present (#separator:tab, #html:true, #notetype:...)
  - data-column count matches the `#tags column:N` header
  - every card row has exactly that many tab-separated columns
  - no em dash (-) anywhere in card content (house style)
  - no literal <, > left unescaped (only known formatting tags allowed)
  - no raw & that isn't a proper HTML entity
  - cloze files: every note has >=1 {{cN::...}}; warns on inline comma-separated
    cloze runs (should be an HTML list instead)
"""
import os
import re
import sys

ALLOWED_TAGS = {"b", "i", "u", "br", "code", "pre", "span", "ul", "ol", "li", "sub", "sup", "em", "strong"}
TAG_RE = re.compile(r"</?([a-zA-Z]+)(\s[^>]*)?>")
ENTITY_RE = re.compile(r"&(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);")
CLOZE_RE = re.compile(r"\{\{c\d+::")
INLINE_CLOZE_RUN_RE = re.compile(r"\{\{c\d+::[^}]*\}\}\s*,\s*\{\{c\d+::")


def check_file(path):
    problems = []
    warnings = []
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    headers = [l for l in lines if l.startswith("#")]
    cards = [l for l in lines if l and not l.startswith("#")]
    header_blob = "\n".join(headers)

    for needed in ["#separator:tab", "#html:true", "#notetype:"]:
        if needed not in header_blob:
            problems.append(f"missing header {needed}")

    is_cloze = "#notetype:Cloze" in header_blob

    m = re.search(r"#tags column:(\d+)", header_blob)
    expected_cols = int(m.group(1)) if m else None
    if expected_cols is None:
        warnings.append("no '#tags column:N' header - can't verify column count")

    for i, line in enumerate(cards, 1):
        cols = line.split("\t")
        if expected_cols is not None and len(cols) != expected_cols:
            problems.append(f"card {i}: {len(cols)} columns, header says {expected_cols}")
        if "\u2014" in line:
            problems.append(f"card {i}: contains em dash")
        for mt in TAG_RE.finditer(line):
            if mt.group(1).lower() not in ALLOWED_TAGS:
                problems.append(f"card {i}: literal/unknown tag <{mt.group(1)}> (escape as &lt;{mt.group(1)}&gt;)")
        stripped = TAG_RE.sub("", line)
        if "<" in stripped or ">" in stripped:
            problems.append(f"card {i}: stray < or > after removing valid tags -> {stripped.replace(chr(9),' ')[:80]!r}")
        if "&" in ENTITY_RE.sub("", line):
            problems.append(f"card {i}: raw '&' not written as an entity (&amp;)")
        if is_cloze:
            text = cols[0]
            if not CLOZE_RE.search(text):
                problems.append(f"card {i}: cloze note has no {{{{cN::...}}}} deletion")
            if INLINE_CLOZE_RUN_RE.search(text):
                warnings.append(f"card {i}: inline comma-separated clozes - prefer an HTML list (<ul>/<ol>)")

    return problems, warnings, len(cards)


def gather(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files.extend(sorted(os.path.join(p, f) for f in os.listdir(p) if f.endswith(".tsv")))
        elif p.endswith(".tsv"):
            files.append(p)
        else:
            print(f"  (skipping non-tsv: {p})")
    return files


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    files = gather(sys.argv[1:])
    if not files:
        print("No .tsv files found to validate.")
        sys.exit(2)

    any_problem = False
    for path in files:
        problems, warnings, n = check_file(path)
        print(f"\n{path}\n  cards: {n}")
        for w in warnings:
            print("  warn: ", w)
        if problems:
            any_problem = True
            print("  PROBLEMS:")
            for p in problems:
                print("   -", p)
        else:
            print("  structural checks passed")

    print("\n" + ("Some files have problems." if any_problem else "All files passed structural checks."))
    print("Reminder: this is the mechanical gate only - it says nothing about whether the cards are worth learning.")
    sys.exit(1 if any_problem else 0)


if __name__ == "__main__":
    main()
