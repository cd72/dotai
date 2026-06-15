# Formatting and file-writing details

Read this for HTML escaping, the colour span, source-quote markup, and the TSV-writing script. The everyday essentials (em dash ban, emoji, bold, HTML-not-Markdown, no labels) are in SKILL.md; this file is the full detail and the parts that matter most for code/maths cards.

## HTML formatting

Anki renders HTML natively and strips Markdown, so always use HTML:

- `<b>` for key terms (bold the key term on each side so the eye lands on it fast).
- `<i>` for emphasis or for quoted phrases from the source.
- `<br>` for line breaks within a card.
- `<span style="color:#0066cc">…</span>` sparingly, to highlight a single critical word.
- For a direct source quote, put it on the back as `<br><br><i>"…quote here…"</i>`.

## Escaping literal `<`, `>` and `&` (the silent-break trap)

Because the files set `#html:true`, Anki parses every `<…>` as a tag. Literal angle brackets in your *content* - `vector<int>`, `List<String>`, `template<T>`, or an inequality like `x < y` - will be swallowed and vanish on the rendered card. Write these as `&lt;` and `&gt;`. Write a literal ampersand (`R&D`, `AT&T`, the `&&` operator) as `&amp;`.

Do **not** blanket-escape the whole field - that would destroy your intentional `<b>`, `<br>`, `<ul>` tags. Escape only the literal source characters, leaving the formatting tags as real HTML. This is the most common way a code or maths card silently breaks, so check every card whose content contains `<`, `>` or `&` before output. `validate.py` will catch a stray unescaped bracket, but get it right while drafting.

## TSV escaping rules

TSV breaks easily. Per field:

- **No literal tabs.** Use a space or `<br>`.
- **No literal newlines.** Each card is exactly one line; use `<br>` for any visible break.
- **Literal `<`, `>`, `&` already escaped** to `&lt;`, `&gt;`, `&amp;` as above - a content decision made while drafting, because the `sanitise()` helper deliberately does not touch angle brackets (it cannot tell a real `<b>` from a literal `vector<int>`).
- **Quotes are fine** - TSV does not need to escape `"` the way CSV does.
- **UTF-8 encoding.**

## Writing the file

Generate the file with a small Python script. **Do not use Python's `csv` module** - `csv.QUOTE_NONE` with an `escapechar` mangles quote characters (you get `\"` in Anki). Manually `\t`-join the fields; the "no tabs/newlines inside fields" rule makes proper CSV escaping unnecessary, and this keeps `"` and `'` intact, which matters because backs often hold direct source quotes.

```python
def sanitise(cell: str) -> str:
    # Defensively strip anything that would break the row.
    # Note: deliberately does NOT touch <, >, & - escape those while drafting.
    return cell.replace('\t', ' ').replace('\r', '').replace('\n', '<br>')

with open('/mnt/user-data/outputs/deck_basic.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('#separator:tab\n')
    f.write('#html:true\n')
    f.write('#notetype:Basic\n')
    f.write(f'#deck:{deck_display_name}\n')  # readable name; pre-selects a deck, user can override
    f.write('#tags column:3\n')
    for front, back, tags in cards:
        f.write('\t'.join(sanitise(c) for c in (front, back, tags)) + '\n')

# Cloze file: three columns - text, Back Extra (may be ''), tags
with open('/mnt/user-data/outputs/deck_cloze.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('#separator:tab\n')
    f.write('#html:true\n')
    f.write('#notetype:Cloze\n')
    f.write(f'#deck:{deck_display_name}\n')
    f.write('#tags column:3\n')
    for text, back_extra, tags in cloze_cards:
        f.write('\t'.join(sanitise(c) for c in (text, back_extra, tags)) + '\n')
```

After writing, run `python evals/validate.py /mnt/user-data/outputs/` to confirm the deck imports cleanly. Remember this is the *mechanical* gate only - it says nothing about whether the cards are worth learning (see the audit section in SKILL.md).

## Emoji nuance

Start each side with an emoji, varied across the deck, loosely tied to the topic (🧬 biology, ⚖️ law, 🏛️ history, 💡 definitions, ⚙️ processes, 📐 maths, 🔁 cycles). Keep it *loosely* topical, never a giveaway - an emoji that uniquely identifies the answer becomes an incidental retrieval cue, so the learner recognises the picture instead of recalling the fact. If the user prefers plain cards, drop emojis entirely.

## Re-importing and duplicates

Anki detects duplicate notes by the **first field** (the front, or the cloze text). So keep fronts unique - near-identical fronts both trip the duplicate check *and* interfere in review. If the user re-runs this skill on the same source and re-imports, Anki's import dialog has an "Existing notes" setting (Update / Preserve / Duplicate) that decides whether matching notes are updated or added again; mention this when the user is iterating on a deck they have already imported.

## Forcing exact spelling (type-in answers)

When exact spelling or form is the point (vocabulary, terminology, formulae written out), Anki can make the user *type* the answer and highlight mistakes. The front field ends with `<br>{{type:Back}}` referencing the answer field. Mention this option when spelling is the point - but don't apply it by default, since for most conceptual cards "recall the gist" is the goal and forced typing just adds friction.
