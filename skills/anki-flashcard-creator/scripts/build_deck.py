#!/usr/bin/env python3
"""
build_deck.py - Serialise a deck JSON into Anki-importable TSV files.

This is the *mechanical* half of card production. The model decides what the
cards say (the judgment work) and writes a deck JSON; this script guarantees
the cards are written to disk in the correct format every time - correct
headers, answer-first backs, safe TSV escaping - so none of that has to be
re-derived by hand on each run.

It does NOT judge semantic card quality (atomicity, interference, whether a
fact is worth learning). That is the model's job and cannot be scripted.

It DOES hard-fail on one narrow, mechanical defect: a basic answer that
*literally encodes a list* - an HTML list (<ol>/<ul>/<li>) or a multi-item
dash-join. These have near-zero false positives and are never a legitimate
basic card (a list belongs in a cloze or in separate cards), so the build is
blocked rather than warned. Fuzzier enumeration signals (commas, conjunctions,
length) stay as soft REVIEW warnings, because prose answers contain commas too.

Usage:
    python scripts/build_deck.py <deck.json> [output_dir]

    output_dir defaults to /mnt/user-data/outputs

Deck JSON schema:
{
  "deck_name": "Biology::Cell Structure",   # readable; used for #deck: and the filename slug
  "slug": "biology_cell_structure",          # optional; derived from deck_name if omitted
  "cards": [
    # basic Q&A - the back is assembled as: answer, then a blank line, then context
    {"type": "basic",
     "front": "🧬 Which organelle is the <b>powerhouse of the cell</b>?",
     "answer": "⚡ The <b>mitochondrion</b>.",
     "context": "It generates most of the cell's ATP through aerobic respiration.",  # optional
     "tags": ["biology::cell_structure::organelles"]},

    # cloze - text already contains {{c1::...}} markup (use an <ol>/<ul> list)
    {"type": "cloze",
     "text": "The three primary colours are:<ul><li>{{c1::red}}</li><li>{{c2::blue}}</li><li>{{c3::yellow}}</li></ul>",
     "back_extra": "",                      # optional; shows under the answer
     "tags": ["art::colour_theory"]},

    # reversed - generates a card in each direction (vocabulary, term<->symbol)
    {"type": "reversed",
     "front": "🇪🇸 gato",
     "back": "🐱 cat",
     "tags": ["spanish::animals"]}
  ]
}

Notes:
  - Emojis, <b>/<i> formatting, and any HTML escaping (&lt; &gt; &amp;) are the
    model's responsibility inside the field values - this script passes them
    through untouched. It only strips characters that would break a TSV row
    (literal tabs/newlines/CR), exactly like the old inline sanitise().
  - Only the files needed are written: a deck with no cloze cards gets no
    _cloze.tsv, etc.
  - After running this, run scripts/check_deck.py on the output to confirm the
    files will import cleanly.
"""
import json
import os
import re
import sys

DEFAULT_OUTPUT_DIR = "/mnt/user-data/outputs"

HEADERS = {
    "basic":    "#notetype:Basic",
    "cloze":    "#notetype:Cloze",
    "reversed": "#notetype:Basic (and reversed card)",
}
SUFFIX = {"basic": "_basic.tsv", "cloze": "_cloze.tsv", "reversed": "_reversed.tsv"}


def sanitise(cell: str) -> str:
    """Strip only what would break a TSV row. Deliberately does NOT touch
    <, >, & - those are content decisions made while drafting the card."""
    if cell is None:
        cell = ""
    return str(cell).replace("\t", " ").replace("\r", "").replace("\n", "<br>")


def slugify(name: str) -> str:
    slug = name.lower()
    slug = slug.replace("::", "_")
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_") or "deck"


def assemble_back(card: dict) -> str:
    """Answer first on its own line, then context after a blank line. This is
    what makes answer-first formatting structural rather than a thing the model
    has to remember."""
    answer = (card.get("answer") or "").strip()
    context = (card.get("context") or "").strip()
    if not answer:
        raise ValueError(f"basic card missing 'answer': {card.get('front', '?')!r}")
    return answer + (f"<br><br>{context}" if context else "")


# Word count above which an answer is "probably more than one fact". A crisp
# retrievable answer is usually a word or short phrase; long answers are the
# signature of a multi-fact back that should have been split at draft time.
ANSWER_WORD_LIMIT = 14


def list_answer_errors(card: dict) -> list:
    """HARD errors: the card *literally encodes a list*. Unlike the soft
    heuristics below, these have near-zero false positives - a basic answer or
    front never legitimately contains an HTML list or a 3+ item dash-join,
    because that content belongs in a cloze (one {{cN::item}} per <li>) or in
    separate cards. When this fires the build is BLOCKED: a list smuggled into a
    single Q&A back is the deck's most common and most memory-damaging defect
    (SuperMemo's minimum-information principle), and it is exactly the case a
    one-line 'recalled as a unit' rationalisation slips past a human audit.
    Returns a list of error strings (empty if clean)."""
    front = card.get("front", "?")
    errs = []
    for field in ("front", "answer"):
        val = card.get(field) or ""
        if re.search(r"<\s*(?:ol|ul|li)\b", val, re.I):
            errs.append(
                f"basic card {field} contains an HTML list (<ol>/<ul>/<li>) - a list is "
                f"never a basic card. Make it a cloze (one {{{{cN::item}}}} per <li>) or "
                f"split into one card per item. Front: {front!r}")
    ans_plain = re.sub(r"<[^>]+>", " ", card.get("answer") or "")
    ans_plain = re.sub(r"[.!?]+$", "", ans_plain).strip()
    dash_parts = [p.strip() for p in re.split(r"\s+-\s+", ans_plain) if p.strip()]
    if len(dash_parts) >= 3:
        errs.append(
            f"answer enumerates {len(dash_parts)} dash-separated items "
            f"({' / '.join(dash_parts)}) - a 3+ item list is never a basic card. Convert "
            f"to a cloze with <ol>/<ul>, or split into one card per distinguishing "
            f"feature. Front: {front!r}")
    return errs


def answer_warnings(card: dict) -> list:
    """Soft, heuristic flags for a basic card's answer field. These are NOT
    quality judgements - the script cannot decide atomicity - they just surface
    answers worth a second look so the model splits them before shipping. Unlike
    list_answer_errors() these do NOT block the build, because commas and
    conjunctions occur in legitimate single-fact prose answers too."""
    ans = card.get("answer") or ""
    front = card.get("front", "?")
    inner = re.sub(r"<[^>]+>", "", ans).strip()        # drop HTML tags for analysis
    inner_no_final = re.sub(r"[.!?]+$", "", inner)      # ignore a single trailing period
    warns = []
    n_words = len(inner.split())
    if n_words > ANSWER_WORD_LIMIT:
        warns.append(f"answer is {n_words} words (> {ANSWER_WORD_LIMIT}) - is it really one fact? consider splitting: {front!r}")
    if re.search(r"[.;!?]\s+[A-Za-z]", inner_no_final):
        warns.append(f"answer contains a mid-string sentence break - may be two facts: {front!r}")
    # Enumeration heuristic: 3+ comma/semicolon items that are ALL short looks
    # like a peer list ("Plan, Use tools, Reflect"); a single long clause among
    # them is usually prose (adjective pairs, appositives) so we don't warn.
    norm = re.sub(r",\s+(?:and|or)\s+", ", ", inner_no_final)   # "A, B and C" -> "A, B, C"
    comma_items = [p.strip() for p in re.split(r"[;,]", norm) if p.strip()]
    if len(comma_items) >= 3 and all(len(it.split()) <= 5 for it in comma_items):
        warns.append(f"answer may enumerate {len(comma_items)} peer items - if so, split or make a cloze: {front!r}")
    return warns


def rows_for(card_type: str, cards: list) -> list:
    rows = []
    for c in cards:
        tags = " ".join(c.get("tags", []))
        if card_type == "basic":
            rows.append((c.get("front", ""), assemble_back(c), tags))
        elif card_type == "cloze":
            text = c.get("text", "")
            if "{{c" not in text:
                raise ValueError(f"cloze card has no {{{{cN::...}}}} deletion: {text[:60]!r}")
            rows.append((text, c.get("back_extra", ""), tags))
        elif card_type == "reversed":
            rows.append((c.get("front", ""), c.get("back", ""), tags))
    return rows


def write_tsv(path: str, notetype_header: str, deck_name: str, rows: list):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("#separator:tab\n")
        f.write("#html:true\n")
        f.write(f"{notetype_header}\n")
        f.write(f"#deck:{deck_name}\n")
        f.write("#tags column:3\n")
        for cells in rows:
            f.write("\t".join(sanitise(x) for x in cells) + "\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    deck_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    with open(deck_path, encoding="utf-8") as f:
        deck = json.load(f)

    deck_name = deck.get("deck_name") or "Flashcards"
    slug = deck.get("slug") or slugify(deck_name)
    cards = deck.get("cards", [])

    by_type = {"basic": [], "cloze": [], "reversed": []}
    for c in cards:
        t = c.get("type", "basic")
        if t not in by_type:
            raise ValueError(f"unknown card type {t!r} (expected basic/cloze/reversed)")
        by_type[t].append(c)

    # HARD GATE - validate before writing anything, so a deck that encodes a list
    # in a basic answer never lands in the output directory. Only basic cards are
    # checked: a cloze legitimately contains <ol>/<ul>/<li>, that is the point.
    hard_errors = []
    for c in by_type["basic"]:
        hard_errors.extend(list_answer_errors(c))
    if hard_errors:
        print("BUILD BLOCKED - basic cards that encode a list (must be a cloze or split):")
        for e in hard_errors:
            print("  \u2717", e)
        print("\nNo files written. A 3+ item list is never one basic card - there is no")
        print("'recalled as a unit' exception. Convert each to a cloze (<ol>/<ul>) or")
        print("split into one card per distinguishing feature, then re-run.")
        sys.exit(1)

    written = []
    for card_type, group in by_type.items():
        if not group:
            continue
        rows = rows_for(card_type, group)
        path = os.path.join(output_dir, f"{slug}{SUFFIX[card_type]}")
        write_tsv(path, HEADERS[card_type], deck_name, rows)
        written.append((path, len(rows)))

    if not written:
        print("No cards found in deck JSON - nothing written.")
        sys.exit(1)

    print(f"Deck: {deck_name}")
    for path, n in written:
        print(f"  wrote {n} cards -> {path}")

    # Soft backstop: surface basic answers that look like they smuggle in a
    # second fact. Does not fail the build - splitting is the model's call.
    review = []
    for c in by_type["basic"]:
        review.extend(answer_warnings(c))
    if review:
        print("\nREVIEW - these answers look multi-fact (split unless you're sure they're one fact):")
        for w in review:
            print("  -", w)

    print("\nNext: run  python scripts/check_deck.py " + output_dir)


if __name__ == "__main__":
    main()