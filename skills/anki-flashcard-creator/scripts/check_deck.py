#!/usr/bin/env python3
"""
check_deck.py - Structural smoke-test for Anki TSV decks.

This is the *mechanical* audit gate. It checks that a deck will IMPORT CLEANLY.
It does NOT judge card quality (atomicity, cloze-vs-Q&A choice, interference,
answer-telegraphing) - that needs per-card reasoning by the model or a human.
A green result here means "the file is well-formed", NOT "the cards are good".

This lives in scripts/ (which the packager ships) so it is runnable at output
time by an installed skill, not just by a maintainer testing offline.

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
  - basic/reversed files: WARNS (never fails) when a front looks like a yes/no
    question or a binary "A or B?" choice - both are 50%-guess fronts. This is a
    conservative safety net for the per-card audit, not a replacement: the defects
    that actually need reading the card (telegraphing, interference, smuggled
    context) cannot be detected here.
"""
import os
import re
import sys

ALLOWED_TAGS = {"b", "i", "u", "br", "code", "pre", "span", "ul", "ol", "li", "sub", "sup", "em", "strong"}
TAG_RE = re.compile(r"</?([a-zA-Z]+)(\s[^>]*)?>")
ENTITY_RE = re.compile(r"&(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);")
CLOZE_RE = re.compile(r"\{\{c\d+::")
INLINE_CLOZE_RUN_RE = re.compile(r"\{\{c\d+::[^}]*\}\}\s*,\s*\{\{c\d+::")

# --- Heuristic front-quality warnings (judgment gates that happen to be lexically detectable) ---
# These are conservative and WARN ONLY - they never fail the build. They are a safety net for
# when the per-card audit misses them; they do not replace it. Most quality defects
# (telegraphing, interference, smuggled context) need reading the card and cannot be scripted.

# Yes/no front: starts with an interrogative auxiliary and ends in a question mark.
# A 50% guess rate tests nothing -> recast as an open "which/what/why" front.
YES_NO_FRONT_RE = re.compile(
    r"^(is|are|was|were|do|does|did|can|could|should|would|will|has|have|had)\b.*\?\s*$",
    re.IGNORECASE,
)
# Binary "A or B?" front: a two-option forced choice baked into the question (".. X or Y?").
# Same 50% guess, and it lets the learner memorise the position instead of the fact.
# Requires the " or " to sit near the end (before the final '?') to avoid matching answers
# that merely list alternatives mid-sentence.
A_OR_B_FRONT_RE = re.compile(r"\bor\b[^?]{0,40}\?\s*$", re.IGNORECASE)


def strip_for_prose(text):
    """Remove HTML tags and a leading emoji/symbol so front heuristics see plain words."""
    prose = TAG_RE.sub("", text)
    # drop leading non-letter clutter (category emoji, spaces) so ^ anchors hit the first word
    return re.sub(r"^[^A-Za-z]+", "", prose).strip()


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
        else:
            # Front-quality heuristics: the front is the first column on basic/reversed notes.
            front_prose = strip_for_prose(cols[0]) if cols else ""
            if YES_NO_FRONT_RE.match(front_prose):
                warnings.append(
                    f"card {i}: front looks like a yes/no question (50% guess) - "
                    f"recast as an open 'which/what/why' front"
                )
            elif A_OR_B_FRONT_RE.search(front_prose):
                warnings.append(
                    f"card {i}: front looks like a binary 'A or B?' choice (50% guess) - "
                    f"recast as an open front or test the property directly"
                )

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
    print("Reminder: structural pass != good cards. Any 'warn:' lines above are heuristic")
    print("flags to revisit; absence of warnings still does not mean the cards are well-made -")
    print("telegraphing, interference, and smuggled-context defects are invisible to this script.")
    sys.exit(1 if any_problem else 0)


if __name__ == "__main__":
    main()
