---
name: anki-flashcard-creator
description: Generate high-quality Anki flashcards from source material - articles, syllabi, textbook chapters, lecture notes, documentation, transcripts, or any study material. Use this skill whenever the user wants to make flashcards, study cards, revision cards, spaced-repetition cards, or Anki cards from content they share, even if they don't say the word "Anki". Also trigger when the user asks to "memorise", "revise", "study", or "learn" a piece of source material in a structured way, or asks to turn notes/a chapter/a paper/a syllabus into something they can revise from. Produces both an inline preview of the cards and tab-separated files ready to import directly into Anki.
---

# Anki Flashcard Creator

Turn any source material into a deck of well-crafted Anki flashcards that follow established spaced-repetition principles, then deliver them both as an inline preview and as Anki-importable TSV files.

<!-- Maintainers: if you change the output format (headers, columns, escaping, cloze markup, note types, files) or any card-generation behaviour, test before shipping - see evals/README.md for the decision table and how to run evals/validate.py. -->

## Workflow

Follow these steps in order.

1. **Read the source material in full.** If a file was uploaded, read it. If the user pasted text, work from that. If they referenced a URL, fetch it. Don't skim - card quality depends on understanding what's actually important versus what's incidental.
2. **Confirm scope briefly if the source is very long.** For sources over ~5,000 words or with clearly distinct sections, ask the user whether they want cards on the whole thing or specific chapters/topics. For shorter sources, just proceed.
3. **Plan the cards mentally before writing them.** Identify the important concepts, definitions, processes, relationships, causes-and-effects, and key facts. Skip trivia, examples that exist only to illustrate the concept, and anything the user is unlikely to need to recall. Aim for **comprehensive coverage of important content** - one card per atomic fact - not exhaustive coverage of every sentence.
4. **Draft the cards** following the rules in the next section.
5. **Review every drafted card for atomicity before writing any output.** For each card ask two questions: (a) *Does the front have exactly one correct answer?* (b) *If I deleted one sentence from the back, would the card still be a complete, valid card?* If the answer to (a) is no, narrow the front. If the answer to (b) is yes, that sentence belongs on a separate card. This step is not optional - failure to split is the single most common quality problem in generated decks.
6. **Display a preview in chat** - show the cards in a readable format so the user can sanity-check before importing.
7. **Generate the TSV files** in `/mnt/user-data/outputs/`, then present them with the `present_files` tool.

## Card-writing rules

These rules are the heart of the skill. Follow them carefully - they're based on established spaced-repetition principles (Wozniak's 20 rules, SuperMemo guidance) and produce cards that are actually retainable.

### Atomicity and minimum information

Each card tests **one specific piece of information**. If a concept has multiple aspects (e.g., a function has a name, a return type, and a side effect), make a separate card for each aspect. If the answer to a question contains multiple distinct facts, split it into multiple cards. The "minimum information principle" is the single most important rule - cards that try to test too much at once are the main reason flashcards fail.

**Red flags on the front:** these question patterns almost always produce multi-fact backs - treat them as a signal to split before you write:
- "What is X?" for any concept with multiple defining properties → split into "What does X do?", "Where does X run?", "What does X return?", etc.
- "What are the [plural noun]…?" → each item in the answer is its own card.
- Fronts containing "and" or "or" joining two distinct concepts → split into two fronts.
- "How does X compare to Y?" → usually hides 3+ independent facts; ask one specific dimension per card instead.

**Red flags on the back:** before finalising, scan the back for:
- A list of 3+ comma-separated items that are independent facts (not a fixed sequence) → split into separate Q&A cards or a cloze.
- Two or more full sentences each asserting a different fact → split; the second sentence is a new card.
- The word "and" joining two independent clauses → often a split point.
- **A list whose items are not true peers** → do NOT enumerate them in one card. If one item contains the others, or the items relate hierarchically (X contains Y; X joins to Z; X is a kind of Y), the flat list hides the structure that actually needs learning. Source material often presents such items as a single flat bullet list, which obscures the hierarchy - do not mirror that layout. Instead write separate cards that each test one item *and* at least one card that tests the containment or relationship explicitly (e.g. "How do Y and Z relate to X?"). Only enumerate as a single list/cloze when the items genuinely sit at the same level (e.g. the five Great Lakes, lifecycle stages in sequence).

**Bad (too much at once):**
- Front: What is photosynthesis?
- Back: The process by which plants convert light energy into chemical energy, using carbon dioxide and water to produce glucose and oxygen, taking place in the chloroplasts.

**Good (split into atomic cards):**
- Card 1 - Front: What is the purpose of photosynthesis? Back: To convert light energy into chemical energy.
- Card 2 - Front: What two raw materials do plants need for photosynthesis? Back: Carbon dioxide and water.
- Card 3 - Front: What two products does photosynthesis produce? Back: Glucose and oxygen.
- Card 4 - Front: Where in the plant cell does photosynthesis occur? Back: In the chloroplasts.

### Question style

- **Default to Q&A format.** Rephrase facts as a clear question with a definitive answer. Use Q&A for conceptual understanding, processes, and "why" / "how" questions.
- **Use cloze when a single card's answer contains 3 or more independent items** - a list, sequence, enumeration, or set of named steps where the items themselves are what needs memorising. When you do, lay the items out as an HTML list (one cloze per `<li>`) rather than as a comma-separated sentence - see "Cloze formatting" below for the required markup. For example, the five Great Lakes become:
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
  If you can write a clean Q&A card instead, do that. Don't reach for cloze just because the source sentence is convenient to gut. Bear in mind the SuperMemo guidance that *enumerations and unordered sets are intrinsically hard to retain* (Wozniak's rules on avoiding sets and enumerations): even a list of genuine peers is harder to learn than a set of meaningful Q&A cards. So treat a cloze list as a last resort - prefer recasting the items into Q&A by distinguishing feature or relationship ("Which Great Lake is the largest by area?"), and reserve the cloze list for cases where the bare membership or order of the list really is the thing being memorised.
- **When cloze cards exist, the cloze TSV file is required** - generate it automatically alongside the basic TSV. Do not wait to be asked.
- **Write unambiguous prompts.** A good prompt has exactly one correct answer. If the question could reasonably have several answers, narrow it: "What was the **immediate** cause of WWI?" rather than "What caused WWI?"
- **Avoid yes/no questions.** They give a 50% chance of being right by guessing and don't test real understanding. Reframe: instead of "Is the mitochondrion the powerhouse of the cell?" ask "Which organelle is known as the powerhouse of the cell?"
- **Add enough context that the card makes sense in isolation.** When the user reviews this card in 6 months, they won't remember it came from chapter 3 of a specific book. "What does the second argument do?" is unreviewable; "In Python's `range()` function, what does the second argument specify?" is fine.
- **Watch for interference between near-identical cards.** Interference - similar cards making each other hard to recall - is one of the biggest causes of forgetting. When several cards share almost the same front (e.g. "Which layer sits above X?" repeated for every layer, or many drug-dosage numbers), they blur together. Defend against it: make each front unambiguous, add a distinguishing cue or example that pins down the specific one, and prefer a few well-differentiated cards over a dozen interchangeable ones. If two cards could be answered by swapping their answers without anyone noticing, they will interfere.
- **Date- or version-stamp volatile facts.** Stable facts (anatomy, basic maths, history) need no stamp. But anything that goes out of date - statistics, prices, economic figures, "current" office-holders, software behaviour - should carry a marker so the user knows when it was true: put a year or version in the card (e.g. "As of <b>2026</b>, …" or "In <b>Python 3.12</b>, …") and add a tag like `as_of_2026`. This makes stale cards easy to find and update later, and stops the user trusting a figure that has since moved.

### Answer / back-of-card style

- **The core answer must be as short as possible and stand alone.** What the learner has to *retrieve* is the first thing on the back, on its own line, in the fewest words that are correct - ideally a single word or phrase. Everything else (explanation, example, source quote) is secondary context to be read *after* recall, not part of what's being recalled. This is the minimum information principle applied to the back: the shorter the thing you pull from memory each repetition, the more reliably it sticks.
- After the answer, you may add a brief **explanation** and, where possible, a **direct quote from the source** to anchor the card. Keep the explanation to one or two sentences - the card is for recall, not re-reading the textbook.
- Include short examples on the back when they aid understanding (e.g., for an abstract concept like "lazy evaluation", give a one-line example).
- **For arbitrary, hard-to-associate facts, consider adding a short mnemonic.** When a fact has no logical hook - a name, a date, an order with no inherent reason - a small memory aid on the back (a wordplay link, an acronym, a vivid image described in words) can turn a future leech into a stable card. Keep it brief and clearly secondary to the answer, e.g. answer first, then `<br><i>(mnemonic: …)</i>`. Don't force mnemonics onto facts that already have a logical structure; reserve them for the genuinely arbitrary ones.
- Use new lines <br> and/or a blank line to separate the answer from the explanation, so the eye lands on the answer first.
- **Never deliver a back as a single dense paragraph when it contains more than one distinct point.** Even within an atomic card, put the answer on its own line, then the explanation, then any quote - each separated by `<br>`. A wall of text with no line breaks is hard to scan during review and is treated as a defect to fix before output.


### Reversed (bidirectional) cards

Some material needs to be recalled in *both* directions, and a one-way Q&A card only trains one of them. The classic case is anything where the front and back are a symmetric pair the user must produce either way round:

- **Vocabulary and translation** - `gato` ↔ `cat`, a foreign word and its meaning. The learner needs to go word→meaning *and* meaning→word.
- **Term ↔ definition** where both recall directions are genuinely useful (e.g. a symbol and its name, an abbreviation and its expansion).

For these, use Anki's **`Basic (and reversed card)`** note type instead of `Basic`. It takes the same two fields (Front, Back) but generates *two* cards per note - one in each direction - so you write the pair once. Emit a third TSV file for these, identical to the basic format but with `#notetype:Basic (and reversed card)`:

```
#separator:tab
#html:true
#notetype:Basic (and reversed card)
#deck:<deck name>
#tags column:3
<front><TAB><back><TAB><tags>
```

When the source is clearly a vocabulary list, a glossary, or term/definition pairs, default to offering reversed cards (or just produce them and say so in the preview). Do **not** make cards reversible by default for ordinary factual Q&A - "Which organelle is the powerhouse of the cell?" reversed becomes "🧬 mitochondrion → ?", which has many valid answers and trains nothing. Reverse only when *both* directions have a single, well-defined answer.


### What to skip (and what not to skip)

- Trivial details (page numbers, author's middle name, exact dates of minor events).
- Examples that exist purely to illustrate a concept already covered by another card.
- Anything the user is unlikely to ever need to recall.

**But do not over-prune the basics.** A fact being *obvious* or *simple* is not a reason to skip it - foundational facts are cheap to memorise, are leaned on constantly, and a lapse on one is costly. Skip genuine *trivia* (incidental, low-value detail), not load-bearing basics. When in doubt about a basic, keep it.

**Deliberate redundancy is good - don't confuse it with lazy duplication.** Two cards that say the same thing the same way are waste; cut the weaker one. But planned redundancy on a *high-value* fact is beneficial and does not violate the minimum information principle: a reversed card (active *and* passive recall of the same pair), or two cards probing the same important idea from different angles, each strengthen recall and resist interference. So keep purposeful redundancy on the facts that matter; only cut redundancy that adds nothing.

### Formatting (this is strict)

- **Never include labels** like `Q:`, `A:`, `Question:`, `Answer:`, `Front:`, `Back:`, `Cloze:` in the actual card content. Anki provides the framing.
- **Never use the em dash (—) anywhere in card content** - not on the front, the back, or in cloze text. Where you would reach for one, use a normal hyphen with spaces around it (` - `), or restructure the sentence with a comma, colon, or parentheses. This is a firm house-style preference, so treat any em dash in a generated card as a defect to fix before output. Note that the en dash (–) is fine and expected inside numeric or date ranges (e.g. `1917–91`, `pages 4–7`); the ban is on the em dash only.
- **Use HTML formatting** in the cards, not Markdown - Anki renders HTML natively but strips Markdown.
  - `<b>` for key terms.
  - `<i>` for emphasis or quoted phrases from the source.
  - `<br>` for line breaks within a card.
  - `<span style="color:#0066cc">…</span>` sparingly to highlight a critical word.
- **Escape literal `<`, `>` and `&` that are NOT your own markup.** Because the files set `#html:true`, Anki parses every `<…>` as an HTML tag. So literal angle brackets in the *content* - `vector<int>`, `List<String>`, `template<T>`, or an inequality like `x < y` - will be swallowed and vanish on the rendered card. Write these as `&lt;` and `&gt;` (and a literal ampersand, e.g. `R&D`, `AT&T`, the `&&` operator, as `&amp;`). Do **not** blanket-escape the whole field - that would destroy your intentional `<b>`, `<br>`, `<ul>` tags. Escape only the literal source characters, leaving the formatting tags as real HTML. This is the most common way a code or maths card silently breaks, so check every card whose content contains `<`, `>` or `&` before output.
- **Start each side with an emoji** - one on the front, one on the back, before any other content. This is a house-style preference, not a spaced-repetition principle. Vary the emojis across the deck; don't reuse the same one for every card. Pick emojis that loosely relate to the topic (🧬 for biology, ⚖️ for law, 🏛️ for history, 💡 for definitions, ⚙️ for processes, 📐 for maths, 🔁 for cycles, etc.). One caution: keep the emoji *loosely* topical, not a giveaway - an emoji that uniquely identifies the answer becomes an incidental retrieval cue (the learner recognises the picture instead of recalling the fact). If a user prefers plain cards, drop the emojis entirely.
- **Bold key terms** on the front and back so the eye lands on the important word fast.
- For direct quotes from the source, wrap them in `<i>` and include them on the back like: `<br><br><i>"…direct quote here…"</i>`.

### Cloze formatting

- When you do use cloze cards, follow Anki's syntax: `{{c1::hidden text}}`, `{{c2::another piece}}`, etc. Each `c1`, `c2`, `c3` produces a separate card from the same note, hiding one piece at a time. Use this for genuine lists or sequences only.
- **Lay the items out as an HTML list by default - never as a comma-separated run of clozes in a single sentence.** A cloze note almost always exists *because* it holds a list or sequence, and lists render far more legibly stacked vertically than inline: each item gets its own line, the eye can find the gap being tested, and a long enumeration doesn't wrap into an unreadable blob. Inline `{{c1::a}}, {{c2::b}}, {{c3::c}}` is the most common formatting mistake on these cards - treat it as wrong unless the content genuinely is a single flowing sentence (rare).
- Use `<ol>` for sequences or rankings where the **order matters** (chronological steps, a name-change lineage, smallest-to-largest), and `<ul>` for unordered sets where order is irrelevant. Put one cloze per `<li>`. Keep any introductory stem as a short lead-in line before the list so the card still makes sense in isolation.
- You may add a hint inside the cloze with `::hint`, e.g. `{{c1::Superior::largest by area}}`.

**Bad (inline - cramped and hard to read):**
```html
The first three US presidents were {{c1::Washington}}, {{c2::Adams}}, and {{c3::Jefferson}}.
```

**Good (ordered list - order matters, so `<ol>`):**
```html
The first three US presidents, in order, were:
<ol>
  <li>{{c1::Washington}}</li>
  <li>{{c2::Adams}}</li>
  <li>{{c3::Jefferson}}</li>
</ol>
```

**Good (unordered set - order irrelevant, so `<ul>`):**
```html
The three primary colours are:
<ul>
  <li>{{c1::red}}</li>
  <li>{{c2::blue}}</li>
  <li>{{c3::yellow}}</li>
</ul>
```

Note on the TSV file: each note must still occupy exactly one line, so write the list markup with no literal newlines inside the field (the `<li>`/`<ul>` tags handle the visual line breaks themselves). The HTML renders correctly regardless of internal whitespace.

### Overlapping cloze for long ordered sequences

The single-note list above (one card hiding every item at once) is fine for short sets, but for a *long ordered sequence* where the user must reproduce the order - and especially where the transitions between items are the hard part - it trains the ordering poorly: the learner sees every other item as a stable anchor and never has to recall what follows what. The SuperMemo remedy is **overlapping cloze**: a sliding window of notes that each hide one item while *showing its neighbours*, so the brain rehearses the transitions. Think of how you'd drill the alphabet - not "recite all 26", but "…C, **?**, E…".

The key mechanic is cloze numbering: **items sharing the same `cN` number are hidden together on one card; different numbers make separate cards.** For a sliding window you want one card per note, so use a single `c1` per note and slide it along the sequence, keeping one or two neighbours visible on each side as context:

```
note 1:  Order of operations: Parentheses, {{c1::Exponents}}, Multiplication
note 2:  Order of operations: Exponents, {{c1::Multiplication}}, Division
note 3:  Order of operations: Multiplication, {{c1::Division}}, Addition
note 4:  Order of operations: Division, {{c1::Addition}}, Subtraction
```

Each note is one row in the cloze TSV and yields exactly one card. Consecutive windows overlap (Multiplication is shown on notes 1 and 3 and hidden on note 2), which is the *planned redundancy* of rule 17 - the overlap is what builds the chain, not bloat. Use this when a sequence has roughly 6+ ordered items and the order itself is the point (the alphabet, the cranial nerves, a decay chain, a ranked list). For short sequences (3-5 items) the single stacked-list note is simpler and still fine. If you want a wider gap, hide a short *run* with one shared number - `…A {{c1::B}} {{c1::C}} {{c1::D}} E…` makes one card that hides B, C and D together - but the one-item sliding window is the easiest to get right. It can also help to keep one whole-sequence card, or to have the user recite the full list once after the individual repetitions.

### Converting a set into a meaningful structure (rather than a flat cloze)

Before you make *any* cloze list for a set, ask whether the set can be **regrouped into something meaningful** - this is almost always better than memorising a bare membership list. Wozniak's worked example takes the 15 members of the EU and, instead of one impossible "list all members" card, builds a series of small context-anchored cards around the *history* of who joined when (founding six, then the 1973 entrants, then 1981, and so on). The flat set becomes a structured, partly-causal story that's far easier to retain and teaches more. So for a set, prefer: group by a meaningful dimension (chronology, geography, function), give each group its own small card with context, and only fall back to a stacked cloze list when no meaningful structure exists and the bare membership genuinely must be memorised.

## Output format

Produce up to **three TSV files** (Tab-Separated Values) saved to `/mnt/user-data/outputs/`, depending on which card types you generated:

1. `<deck-name>_basic.tsv` - for one-way Q&A cards (`#notetype:Basic`)
2. `<deck-name>_cloze.tsv` - for cloze cards (`#notetype:Cloze`)
3. `<deck-name>_reversed.tsv` - for bidirectional cards such as vocabulary (`#notetype:Basic (and reversed card)`)

Generate only the files you need - skip any type you didn't produce. Most decks are just basic, or basic + cloze; the reversed file appears mainly for vocabulary/glossary sources.

The user will import each file separately into Anki: **File → Import** (Ctrl+Shift+I), pick the file, confirm, done. The headers set the note type and tags automatically, and **pre-select** a deck (see `#deck:` below) - the user can still pick a different deck in the import dialog before confirming.

**Re-importing / duplicates.** Anki detects duplicate notes by the **first field** (the front, or the cloze text). Two consequences worth knowing: keep fronts unique, or near-identical fronts will trip the duplicate check; and if the user re-runs this skill on the same source and re-imports, Anki's import dialog has an "Existing notes" setting (Update / Preserve / Duplicate) that decides whether matching notes are updated or added again. Mention this if the user is iterating on a deck they've already imported.

### Basic TSV format

```
#separator:tab
#html:true
#notetype:Basic
#deck:<deck name>
#tags column:3
<front><TAB><back><TAB><tags>
<front><TAB><back><TAB><tags>
...
```

- `#separator:tab` - tells Anki the columns are tab-separated.
- `#html:true` - tells Anki to render the `<b>`, `<i>`, `<br>` etc. instead of showing them as text.
- `#notetype:Basic` - sets the note type so the user doesn't have to.
- `#deck:<deck name>` - pre-selects a deck in the import dialog. This is a default, not a lock.  Use a readable deck name here (e.g. `Spanish Verbs`, `Biology::Cell Structure`), **not** the underscored filename slug. Omit this line if you don't have a sensible deck name. (Do **not** use a per-note `#deck column:` instead - that one *does* force placement and auto-creates decks, which is not what we want.)
- `#tags column:3` - tells Anki the third *data* column is the tags (space-separated). Note: this number counts the tab-separated columns in the card rows, not the header lines - adding the `#deck:` line above does **not** change it.
- Each subsequent line is one card: front, tab, back, tab, tags.

### Cloze TSV format

```
#separator:tab
#html:true
#notetype:Cloze
#deck:<deck name>
#tags column:3
<text with {{c1::cloze}}><TAB><back extra><TAB><tags>
...
```

The built-in Cloze note type has two content fields, **Text** and **Back Extra**, plus tags - so the columns are: cloze text, then Back Extra, then tags. Back Extra shows *below* the answer on the back of every card generated from the note, so it's the right home for the short explanation and source quote that Q&A cards put on their back - this keeps cloze cards anchored to the source too, rather than being bare gutted sentences. Leave the Back Extra field empty (an empty column, but keep the tab) when there's genuinely nothing useful to add. Because Back Extra is now column 2, tags move to column 3: set `#tags column:3`.

### Tags

Derive tags from the source material's structure and topics, and prefer **hierarchical tags** using `::` to nest subtopics under a parent - this is the modern Anki convention and filters far better than a flat list, because the user can collapse a whole branch or select a parent to catch everything beneath it. Use `lowercase_with_underscores` for each level. Examples: `biology::cell_structure::organelles`, `python::functions::error_handling`, `history::ww1::causes`. Give every card 2-4 relevant tags. A good default is one or two hierarchy tags that place the card in the deck's topic tree, plus a flat keyword tag or two for cross-cutting themes (e.g. `exam_critical`, `as_of_2026`). Keep the hierarchy shallow - two or three levels is plenty; deeper nesting is rarely worth the verbosity.

### Critical TSV escaping rules

TSV breaks easily. Before writing each card, ensure:

- **No literal tabs inside fields.** If the content needs whitespace, use a regular space or `<br>`.
- **No literal newlines inside fields.** Each card must be exactly one line in the file. Use `<br>` for any line break the user should see in Anki.
- **Literal `<`, `>`, `&` must already be escaped to `&lt;`, `&gt;`, `&amp;` in the card text** (see the formatting rules above). This is a content decision made while drafting each card - the `sanitise()` helper below deliberately does NOT touch angle brackets, because it can't tell your real `<b>` tags from a literal `vector<int>`. Get it right when you write the card.
- **Quotes are fine** - TSV doesn't need to escape `"` the way CSV does.
- **UTF-8 encoding** - write the file in UTF-8 (Python's default with `open(path, 'w', encoding='utf-8')`).

Generate the file with a small Python script. **Do NOT use Python's `csv` module** - `csv.QUOTE_NONE` with an `escapechar` will mangle quote characters in your card text (you'll get `\"` showing up in Anki). Just manually `\t`-join the fields, since the rule "no tabs/newlines inside fields" makes proper CSV escaping unnecessary. Example:

```python
def sanitise(cell: str) -> str:
    # Defensively strip anything that would break the row
    return cell.replace('\t', ' ').replace('\r', '').replace('\n', '<br>')

with open('/mnt/user-data/outputs/deck_basic.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('#separator:tab\n')
    f.write('#html:true\n')
    f.write('#notetype:Basic\n')
    f.write(f'#deck:{deck_display_name}\n')  # readable name; pre-selects an existing deck, user can override
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

This keeps quote characters (`"`, `'`) intact in the output, which matters because the back of cards often contains direct quotes from the source.

## Inline preview format

Before (or alongside) saving the TSV files, show the user a clean preview of the cards in chat so they can sanity-check. Use this format:

```
**Card 1** · tags: `biology::cell_structure::organelles`
Front: 🧬 Which organelle is known as the **powerhouse of the cell**?
Back: ⚡ The **mitochondrion**. It generates most of the cell's ATP through aerobic respiration.

**Card 2** · tags: `biology::photosynthesis`
Front: 🌱 Where in the plant cell does **photosynthesis** occur?
Back: 🔬 In the **chloroplasts**, specifically within the thylakoid membranes.
```

For a long deck (say 30+ cards), show the first 5–10 as a preview with a note like "Showing first 8 of 47 cards - full set is in the TSV file" rather than dumping everything. Then offer to show specific cards or the full list if asked.

## Deck naming

Choose a descriptive deck name from the source topic *before* generating the files, and use it both for the `#deck:` header and the filename slug. Don't default to a generic name like "deck" or "flashcards" - if you do, a user who builds several decks ends up with a pile of files all called the same thing, and `#deck:deck` dumped together in Anki. Good names read like `Spanish Verbs`, `Biology::Cell Structure`, `Tort Law - Negligence` (the `::` creates a subdeck). Derive the filename slug from the same name in `lowercase_with_underscores` (e.g. `biology_cell_structure_basic.tsv`).

## Edge cases

- **Source is in another language.** Generate the cards in the same language as the source unless the user asks otherwise. Adjust emoji choices and HTML escaping the same way.
- **Source contains formulas / code.** Wrap formulas in `<code>…</code>` for inline rendering, or for multi-line code use `<pre>…</pre>`. For LaTeX, Anki uses `\(…\)` for inline and `\[…\]` for display math - the user will need MathJax enabled. Remember that literal `<`, `>` and `&` inside code or inequalities must be escaped to `&lt;`, `&gt;`, `&amp;` (see the formatting rules) or they'll vanish under HTML rendering.
- **Source has images/diagrams worth learning (anatomy, maps, charts).** Imagery is one of the most powerful learning aids - a labelled diagram can be far more memorable than the equivalent prose, and a single illustration can seed many cards by hiding one labelled part at a time (graphic deletion). But TSV import cannot bundle media: Anki only finds images already in the profile's `collection.media` folder, which this skill can't write to. So don't emit `<img>` tags pointing at files the user doesn't have - they'll show as broken images. Instead: (a) describe the visual in words on the text cards so the deck still works, and (b) when the source is genuinely visual, tell the user that the strongest cards here would be image-based, and point them at Anki's built-in **Image Occlusion** note type (Anki 23.10+), which is purpose-built for hiding labelled regions of a diagram - they add the image once inside Anki and it generates one card per hidden region. Flag this whenever text-only cards clearly lose something important.
- **Source is too thin to make a meaningful deck.** If the source is under ~200 words or just a list of trivia, tell the user honestly and ask whether they have more material to combine or whether they want cards on the small amount that's there.
- **User asks for a specific number of cards.** Honour it - but if the number is way out of step with the source (e.g., 5 cards for an entire textbook chapter, or 100 cards for a one-page summary), say so and suggest a more sensible count.
- **User wants only cloze, or only Q&A.** Honour the preference. Cloze-only decks are common for vocabulary or list-heavy material.
- **Exact spelling matters (vocabulary, terminology, formulae written out).** Anki can require the user to *type* the answer and will highlight any mistake, which is valuable when knowing roughly the right answer isn't enough. To use it, the front field includes a `{{type:Back}}` marker referencing the answer field (e.g. a `Basic` card whose front ends with `<br>{{type:Back}}`). Mention this option when spelling or exact form is the point - but don't apply it by default, since for most conceptual cards "recall the gist" is the goal and forced typing just adds friction.

## Worked example

For more detailed guidance on a particular tricky case (medical/scientific content with lots of nested concepts, or code/syntax-heavy material) see `references/examples.md`.