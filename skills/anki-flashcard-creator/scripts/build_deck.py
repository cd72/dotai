#!/usr/bin/env python3
"""
build_deck.py - Serialise a deck JSON into Anki-importable TSV files.

This is the *mechanical* half of card production. The model decides what the
cards say (the judgment work) and writes a deck JSON; this script guarantees
the cards are written to disk in the correct format every time - correct
headers, answer-first backs, safe TSV escaping - so none of that has to be
re-derived by hand on each run.

It does NOT judge card quality (atomicity, cloze-vs-Q&A, interference). That is
the model's job and cannot be scripted. Keep this a dumb serialiser.

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
    print("\nNext: run  python scripts/check_deck.py " + output_dir)


if __name__ == "__main__":
    main()
