# Formatting and file-writing details

Read this for HTML escaping, the colour span, source-quote markup, and the deck JSON schema build_deck.py consumes. The everyday essentials (em dash ban, emoji, bold, HTML-not-Markdown, no labels) are in SKILL.md; this file is the full detail and the parts that matter most for code/maths cards.

## HTML formatting

Anki renders HTML natively and strips Markdown, so always use HTML:

- `<b>` for key terms (bold the key term on each side so the eye lands on it fast).
- `<i>` for emphasis or for quoted phrases from the source.
- `<br>` for line breaks within a card.
- `<span style="color:#0066cc">…</span>` sparingly, to highlight a single critical word.
- For a direct source quote, put it on the back as `<br><br><i>"…quote here…"</i>`.

## Escaping literal `<`, `>` and `&` (the silent-break trap)

Because the files set `#html:true`, Anki parses every `<…>` as a tag. Literal angle brackets in your *content* - `vector<int>`, `List<String>`, `template<T>`, or an inequality like `x < y` - will be swallowed and vanish on the rendered card. Write these as `&lt;` and `&gt;`. Write a literal ampersand (`R&D`, `AT&T`, the `&&` operator) as `&amp;`.

Do **not** blanket-escape the whole field - that would destroy your intentional `<b>`, `<br>`, `<ul>` tags. Escape only the literal source characters, leaving the formatting tags as real HTML. This is the most common way a code or maths card silently breaks, so check every card whose content contains `<`, `>` or `&` before output. `check_deck.py` will catch a stray unescaped bracket, but get it right while drafting.

## TSV escaping rules

TSV breaks easily. Per field:

- **No literal tabs.** Use a space or `<br>`.
- **No literal newlines.** Each card is exactly one line; use `<br>` for any visible break.
- **Literal `<`, `>`, `&` already escaped** to `&lt;`, `&gt;`, `&amp;` as above - a content decision made while drafting, because the `sanitise()` helper deliberately does not touch angle brackets (it cannot tell a real `<b>` from a literal `vector<int>`).
- **Quotes are fine** - TSV does not need to escape `"` the way CSV does.
- **UTF-8 encoding.**

## Writing the files: the deck JSON

You do not hand-write TSV files. You produce a **deck JSON** and run `scripts/build_deck.py`, which serialises it into the correct TSVs. This guarantees correct headers and escaping every run, and it assembles each basic back as answer-first (answer, blank line, context) so that formatting rule is enforced by the tool rather than left to memory. Under the hood it `\t`-joins manually (never Python's `csv` module, which mangles quotes) and applies a `sanitise()` that strips literal tabs/newlines/CR but deliberately leaves `<`, `>`, `&` untouched - those are your escaping decisions, made while drafting.

Schema (one object per card; include only the card types you actually made):

```json
{
  "deck_name": "Biology::Cell Structure",
  "slug": "biology_cell_structure",
  "cards": [
    {"type": "basic",
     "front": "🧬 Which organelle is the <b>powerhouse of the cell</b>?",
     "answer": "⚡ The <b>mitochondrion</b>.",
     "context": "It generates most of the cell's ATP through aerobic respiration.",
     "tags": ["biology::cell_structure::organelles"]},

    {"type": "cloze",
     "text": "The three primary colours are:<ul><li>{{c1::red}}</li><li>{{c2::blue}}</li><li>{{c3::yellow}}</li></ul>",
     "back_extra": "",
     "tags": ["art::colour_theory"]},

    {"type": "reversed",
     "front": "🇪🇸 gato",
     "back": "🐱 cat",
     "tags": ["spanish::animals"]}
  ]
}
```

Field notes:
- `deck_name` is required; `slug` is optional (derived from `deck_name` if omitted).
- **basic**: `front`, `answer` (required - the single retrievable thing), `context` (optional - explanation or quote; goes below the answer), `tags`.
- **cloze**: `text` (must contain `{{cN::…}}`, laid out as an HTML list), `back_extra` (may be `""`), `tags`.
- **reversed**: `front`, `back`, `tags` - generates a card each direction.
- Put emojis and any HTML/escaping inside the field values; the script passes them through.
- `build_deck.py` prints a REVIEW warning if a basic `answer` looks multi-fact (over ~14 words, or containing a mid-string sentence break). It does not fail the build - treat each warning as a prompt to split the card.

Run it, then validate:

```
python scripts/build_deck.py deck.json /mnt/user-data/outputs/
python scripts/check_deck.py /mnt/user-data/outputs/
```

`check_deck.py` is the *mechanical* gate only - it confirms the deck imports cleanly and says nothing about whether the cards are worth learning (see the audit section in SKILL.md).

## Emoji nuance

Start each side with an emoji, varied across the deck, loosely tied to the topic (🧬 biology, ⚖️ law, 🏛️ history, 💡 definitions, ⚙️ processes, 📐 maths, 🔁 cycles). Keep it *loosely* topical, never a giveaway - an emoji that uniquely identifies the answer becomes an incidental retrieval cue, so the learner recognises the picture instead of recalling the fact. If the user prefers plain cards, drop emojis entirely.

## Re-importing and duplicates

Anki detects duplicate notes by the **first field** (the front, or the cloze text). So keep fronts unique - near-identical fronts both trip the duplicate check *and* interfere in review. If the user re-runs this skill on the same source and re-imports, Anki's import dialog has an "Existing notes" setting (Update / Preserve / Duplicate) that decides whether matching notes are updated or added again; mention this when the user is iterating on a deck they have already imported.

## Forcing exact spelling (type-in answers)

When exact spelling or form is the point (vocabulary, terminology, formulae written out), Anki can make the user *type* the answer and highlight mistakes. The front field ends with `<br>{{type:Back}}` referencing the answer field. Mention this option when spelling is the point - but don't apply it by default, since for most conceptual cards "recall the gist" is the goal and forced typing just adds friction.
