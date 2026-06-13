---
name: anki-flashcard-creator
description: Generate high-quality Anki flashcards from source material — articles, syllabi, textbook chapters, lecture notes, documentation, transcripts, or any study material. Use this skill whenever the user wants to make flashcards, study cards, revision cards, spaced-repetition cards, or Anki cards from content they share, even if they don't say the word "Anki". Also trigger when the user asks to "memorise", "revise", "study", or "learn" a piece of source material in a structured way, or asks to turn notes/a chapter/a paper/a syllabus into something they can revise from. Produces both an inline preview of the cards and tab-separated files ready to import directly into Anki.
---

# Anki Flashcard Creator

Turn any source material into a deck of well-crafted Anki flashcards that follow established spaced-repetition principles, then deliver them both as an inline preview and as Anki-importable TSV files.

## Workflow

Follow these steps in order.

1. **Read the source material in full.** If a file was uploaded, read it. If the user pasted text, work from that. If they referenced a URL, fetch it. Don't skim — card quality depends on understanding what's actually important versus what's incidental.
2. **Confirm scope briefly if the source is very long.** For sources over ~5,000 words or with clearly distinct sections, ask the user whether they want cards on the whole thing or specific chapters/topics. For shorter sources, just proceed.
3. **Plan the cards mentally before writing them.** Identify the important concepts, definitions, processes, relationships, causes-and-effects, and key facts. Skip trivia, examples that exist only to illustrate the concept, and anything the user is unlikely to need to recall. Aim for **comprehensive coverage of important content** — one card per atomic fact — not exhaustive coverage of every sentence.
4. **Draft the cards** following the rules in the next section.
5. **Review every drafted card for atomicity before writing any output.** For each card ask two questions: (a) *Does the front have exactly one correct answer?* (b) *If I deleted one sentence from the back, would the card still be a complete, valid card?* If the answer to (a) is no, narrow the front. If the answer to (b) is yes, that sentence belongs on a separate card. This step is not optional — failure to split is the single most common quality problem in generated decks.
6. **Display a preview in chat** — show the cards in a readable format so the user can sanity-check before importing.
6. **Generate the TSV files** in `/mnt/user-data/outputs/`, then present them with the `present_files` tool.

## Card-writing rules

These rules are the heart of the skill. Follow them carefully — they're based on established spaced-repetition principles (Wozniak's 20 rules, SuperMemo guidance) and produce cards that are actually retainable.

### Atomicity and minimum information

Each card tests **one specific piece of information**. If a concept has multiple aspects (e.g., a function has a name, a return type, and a side effect), make a separate card for each aspect. If the answer to a question contains multiple distinct facts, split it into multiple cards. The "minimum information principle" is the single most important rule — cards that try to test too much at once are the main reason flashcards fail.

**Red flags on the front:** these question patterns almost always produce multi-fact backs — treat them as a signal to split before you write:
- "What is X?" for any concept with multiple defining properties → split into "What does X do?", "Where does X run?", "What does X return?", etc.
- "What are the [plural noun]…?" → each item in the answer is its own card.
- Fronts containing "and" or "or" joining two distinct concepts → split into two fronts.
- "How does X compare to Y?" → usually hides 3+ independent facts; ask one specific dimension per card instead.

**Red flags on the back:** before finalising, scan the back for:
- A list of 3+ comma-separated items that are independent facts (not a fixed sequence) → split into separate Q&A cards or a cloze.
- Two or more full sentences each asserting a different fact → split; the second sentence is a new card.
- The word "and" joining two independent clauses → often a split point.

**Bad (too much at once):**
- Front: What is photosynthesis?
- Back: The process by which plants convert light energy into chemical energy, using carbon dioxide and water to produce glucose and oxygen, taking place in the chloroplasts.

**Good (split into atomic cards):**
- Card 1 — Front: What is the purpose of photosynthesis? Back: To convert light energy into chemical energy.
- Card 2 — Front: What two raw materials do plants need for photosynthesis? Back: Carbon dioxide and water.
- Card 3 — Front: What two products does photosynthesis produce? Back: Glucose and oxygen.
- Card 4 — Front: Where in the plant cell does photosynthesis occur? Back: In the chloroplasts.

### Question style

- **Default to Q&A format.** Rephrase facts as a clear question with a definitive answer. Use Q&A for conceptual understanding, processes, and "why" / "how" questions.
- **Use cloze when a single card's answer contains 3 or more independent items** — a list, sequence, enumeration, or set of named steps where the items themselves are what needs memorising. When you do, lay the items out as an HTML list (one cloze per `<li>`) rather than as a comma-separated sentence — see "Cloze formatting" below for the required markup. For example, the five Great Lakes become:
  ```html
  The five Great Lakes are:
  <ul>
    <li>{{c1::Superior}}</li>
    <li>{{c2::Michigan}}</li>
    <li>{{c3::Huron}}</li>
    <li>{{c4::Erie}}</li>
    <li>{{c5::Ontario}}</li>
  </ul>
  ```
  If you can write a clean Q&A card instead, do that. Don't reach for cloze just because the source sentence is convenient to gut.
- **When cloze cards exist, the cloze TSV file is required** — generate it automatically alongside the basic TSV. Do not wait to be asked.
- **Write unambiguous prompts.** A good prompt has exactly one correct answer. If the question could reasonably have several answers, narrow it: "What was the **immediate** cause of WWI?" rather than "What caused WWI?"
- **Avoid yes/no questions.** They give a 50% chance of being right by guessing and don't test real understanding. Reframe: instead of "Is the mitochondrion the powerhouse of the cell?" ask "Which organelle is known as the powerhouse of the cell?"
- **Add enough context that the card makes sense in isolation.** When the user reviews this card in 6 months, they won't remember it came from chapter 3 of a specific book. "What does the second argument do?" is unreviewable; "In Python's `range()` function, what does the second argument specify?" is fine.

### Answer / back-of-card style

- The back contains: the **answer**, then a brief **explanation**, and where possible a **direct quote from the source** to anchor the card to the original material.
- Keep explanations short — one or two sentences. The card is for recall, not re-reading the textbook.
- Include short examples on the back when they aid understanding (e.g., for an abstract concept like "lazy evaluation", give a one-line example).
- Use new lines <br> and/or a blank line to separate the answer from the explanation.


### What to skip

- Trivial details (page numbers, author's middle name, exact dates of minor events).
- Examples that exist purely to illustrate a concept already covered by another card.
- Anything the user is unlikely to ever need to recall.
- Restated definitions where the same idea has already been captured by a different card.

### Formatting (this is strict)

- **Never include labels** like `Q:`, `A:`, `Question:`, `Answer:`, `Front:`, `Back:`, `Cloze:` in the actual card content. Anki provides the framing.
- **Use HTML formatting** in the cards, not Markdown — Anki renders HTML natively but strips Markdown.
  - `<b>` for key terms.
  - `<i>` for emphasis or quoted phrases from the source.
  - `<br>` for line breaks within a card.
  - `<span style="color:#0066cc">…</span>` sparingly to highlight a critical word.
- **Start each side with an emoji** — one on the front, one on the back, before any other content. Vary the emojis across the deck; don't reuse the same one for every card. Pick emojis that loosely relate to the topic (🧬 for biology, ⚖️ for law, 🏛️ for history, 💡 for definitions, ⚙️ for processes, 📐 for maths, 🔁 for cycles, etc.).
- **Bold key terms** on the front and back so the eye lands on the important word fast.
- For direct quotes from the source, wrap them in `<i>` and include them on the back like: `<br><br><i>"…direct quote here…"</i>`.

### Cloze formatting

- When you do use cloze cards, follow Anki's syntax: `{{c1::hidden text}}`, `{{c2::another piece}}`, etc. Each `c1`, `c2`, `c3` produces a separate card from the same note, hiding one piece at a time. Use this for genuine lists or sequences only.
- **Lay the items out as an HTML list by default — never as a comma-separated run of clozes in a single sentence.** A cloze note almost always exists *because* it holds a list or sequence, and lists render far more legibly stacked vertically than inline: each item gets its own line, the eye can find the gap being tested, and a long enumeration doesn't wrap into an unreadable blob. Inline `{{c1::a}}, {{c2::b}}, {{c3::c}}` is the most common formatting mistake on these cards — treat it as wrong unless the content genuinely is a single flowing sentence (rare).
- Use `<ol>` for sequences or rankings where the **order matters** (chronological steps, a name-change lineage, smallest-to-largest), and `<ul>` for unordered sets where order is irrelevant. Put one cloze per `<li>`. Keep any introductory stem as a short lead-in line before the list so the card still makes sense in isolation.
- You may add a hint inside the cloze with `::hint`, e.g. `{{c1::Superior::largest by area}}`.

**Bad (inline — cramped and hard to read):**
```html
The first three US presidents were {{c1::Washington}}, {{c2::Adams}}, and {{c3::Jefferson}}.
```

**Good (ordered list — order matters, so `<ol>`):**
```html
The first three US presidents, in order, were:
<ol>
  <li>{{c1::Washington}}</li>
  <li>{{c2::Adams}}</li>
  <li>{{c3::Jefferson}}</li>
</ol>
```

**Good (unordered set — order irrelevant, so `<ul>`):**
```html
The three primary colours are:
<ul>
  <li>{{c1::red}}</li>
  <li>{{c2::blue}}</li>
  <li>{{c3::yellow}}</li>
</ul>
```

Note on the TSV file: each note must still occupy exactly one line, so write the list markup with no literal newlines inside the field (the `<li>`/`<ul>` tags handle the visual line breaks themselves). The HTML renders correctly regardless of internal whitespace.

## Output format

Produce **two TSV files** (Tab-Separated Values) saved to `/mnt/user-data/outputs/`:

1. `<deck-name>_basic.tsv` — for Q&A cards
2. `<deck-name>_cloze.tsv` — for cloze cards

Generate only the files you need — if there are no cloze cards, skip that file. If there are no basic cards (rare), skip that file.

The user will import each file separately into Anki: **File → Import** (Ctrl+Shift+I), pick the file, confirm, done. The headers handle note type and tags automatically.

### Basic TSV format

```
#separator:tab
#html:true
#notetype:Basic
#tags column:3
<front><TAB><back><TAB><tags>
<front><TAB><back><TAB><tags>
...
```

- `#separator:tab` — tells Anki the columns are tab-separated.
- `#html:true` — tells Anki to render the `<b>`, `<i>`, `<br>` etc. instead of showing them as text.
- `#notetype:Basic` — sets the note type so the user doesn't have to.
- `#tags column:3` — tells Anki the third column is the tags (space-separated).
- Each subsequent line is one card: front, tab, back, tab, tags.

### Cloze TSV format

```
#separator:tab
#html:true
#notetype:Cloze
#tags column:2
<text with {{c1::cloze}}><TAB><tags>
...
```

Cloze cards have only one content field (the text with the cloze deletions in it) plus tags.

### Tags

Derive tags from the source material's structure and topics. Use `lowercase_with_underscores`, separate multiple tags with spaces. Examples: `biology cell_structure organelles`, `python functions error_handling`, `ww1 causes alliances`. Tags help the user filter and organise within Anki — give every card 2–4 relevant tags.

### Critical TSV escaping rules

TSV breaks easily. Before writing each card, ensure:

- **No literal tabs inside fields.** If the content needs whitespace, use a regular space or `<br>`.
- **No literal newlines inside fields.** Each card must be exactly one line in the file. Use `<br>` for any line break the user should see in Anki.
- **Quotes are fine** — TSV doesn't need to escape `"` the way CSV does.
- **UTF-8 encoding** — write the file in UTF-8 (Python's default with `open(path, 'w', encoding='utf-8')`).

Generate the file with a small Python script. **Do NOT use Python's `csv` module** — `csv.QUOTE_NONE` with an `escapechar` will mangle quote characters in your card text (you'll get `\"` showing up in Anki). Just manually `\t`-join the fields, since the rule "no tabs/newlines inside fields" makes proper CSV escaping unnecessary. Example:

```python
def sanitise(cell: str) -> str:
    # Defensively strip anything that would break the row
    return cell.replace('\t', ' ').replace('\r', '').replace('\n', '<br>')

with open('/mnt/user-data/outputs/deck_basic.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('#separator:tab\n')
    f.write('#html:true\n')
    f.write('#notetype:Basic\n')
    f.write('#tags column:3\n')
    for front, back, tags in cards:
        f.write('\t'.join(sanitise(c) for c in (front, back, tags)) + '\n')
```

This keeps quote characters (`"`, `'`) intact in the output, which matters because the back of cards often contains direct quotes from the source.

## Inline preview format

Before (or alongside) saving the TSV files, show the user a clean preview of the cards in chat so they can sanity-check. Use this format:

```
**Card 1** · tags: `biology cell_structure`
Front: 🧬 Which organelle is known as the **powerhouse of the cell**?
Back: ⚡ The **mitochondrion**. It generates most of the cell's ATP through aerobic respiration.

**Card 2** · tags: `biology photosynthesis`
Front: 🌱 Where in the plant cell does **photosynthesis** occur?
Back: 🔬 In the **chloroplasts**, specifically within the thylakoid membranes.
```

For a long deck (say 30+ cards), show the first 5–10 as a preview with a note like "Showing first 8 of 47 cards — full set is in the TSV file" rather than dumping everything. Then offer to show specific cards or the full list if asked.

## Deck naming

If the user gave the source a clear name (a filename, a chapter title, a topic), use that — sanitised to lowercase with underscores. If not, ask them what to call the deck before generating the files. Don't default to a generic name like "deck" — the user will end up with five files all called the same thing.

## Edge cases

- **Source is in another language.** Generate the cards in the same language as the source unless the user asks otherwise. Adjust emoji choices and HTML escaping the same way.
- **Source contains formulas / code.** Wrap formulas in `<code>…</code>` for inline rendering, or for multi-line code use `<pre>…</pre>`. For LaTeX, Anki uses `\(…\)` for inline and `\[…\]` for display math — the user will need MathJax enabled.
- **Source is too thin to make a meaningful deck.** If the source is under ~200 words or just a list of trivia, tell the user honestly and ask whether they have more material to combine or whether they want cards on the small amount that's there.
- **User asks for a specific number of cards.** Honour it — but if the number is way out of step with the source (e.g., 5 cards for an entire textbook chapter, or 100 cards for a one-page summary), say so and suggest a more sensible count.
- **User wants only cloze, or only Q&A.** Honour the preference. Cloze-only decks are common for vocabulary or list-heavy material.

## Worked example

For more detailed guidance on a particular tricky case (medical/scientific content with lots of nested concepts, or code/syntax-heavy material) see `references/examples.md`.