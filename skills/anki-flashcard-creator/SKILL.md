---
name: anki-flashcard-creator
description: Generate high-quality Anki flashcards from source material - articles, syllabi, textbook chapters, lecture notes, documentation, transcripts, or any study material. Use this skill whenever the user wants to make flashcards, study cards, revision cards, spaced-repetition cards, or Anki cards from content they share, even if they don't say the word "Anki". Also trigger when the user asks to "memorise", "revise", "study", or "learn" a piece of source material in a structured way, or asks to turn notes/a chapter/a paper/a syllabus into something they can revise from. Produces both an inline preview of the cards and tab-separated files ready to import directly into Anki.
---

# Anki Flashcard Creator

Turn any source material into a deck of well-crafted Anki flashcards that follow established spaced-repetition principles (Wozniak's 20 rules, SuperMemo guidance), then deliver them as an inline preview plus Anki-importable TSV files.

<!-- Maintainers: if you change output format (headers, columns, escaping, cloze markup, note types, files) or card-generation behaviour, test before shipping - see evals/README.md and run evals/validate.py. -->

## Why this skill is built around a loop

Making cards that *import* is easy. Making cards that are *easy to learn* is the whole job, and it is a judgment task, not a formatting task. The defects that make a deck painful to review - a back that hides three facts, six fronts that differ only by a number, a question that gives away its own answer - are all invisible to a script. `evals/validate.py` can confirm a deck will import cleanly; it cannot tell you whether a single card is worth learning. Only careful per-card reasoning does that.

So the workflow below forces two things a first draft almost always skips:

1. **Drafting each card in a shape that makes a multi-fact back impossible to miss** (the three-slot draft).
2. **A visible, written audit of every card before any file is written** - the judgment pass, separate from the mechanical one.

Do not collapse or skip these. They are the difference between a draft and a deck worth importing. If you ever find yourself about to write TSV files without having emitted the three-slot drafts and the audit table, stop and do them first.

## Workflow

1. **Read the source in full.** Read the uploaded file, the pasted text, or fetch the URL. Card quality depends on knowing what is important versus incidental, so do not skim.
2. **Confirm scope if the source is long.** For sources over ~5,000 words or with clearly distinct sections, ask whether the user wants the whole thing or specific parts. For shorter sources, just proceed.
3. **Plan coverage.** Identify the concepts, definitions, processes, relationships, and key facts worth recalling. Aim for comprehensive coverage of *important* content - one card per atomic fact - not every sentence. Skip genuine trivia, but do not over-prune load-bearing basics.
4. **Choose the card type for each fact** - basic Q&A by default; cloze or reversed only when they genuinely fit (see "Choosing the card type").
5. **Draft every card in three slots** (see next section). This is where atomicity is enforced.
6. **Run the audit** (see "The audit"). Emit the per-card table. Fix every failure, then re-check.
7. **Preview in chat**, then **write the TSV files** to `/mnt/user-data/outputs/`, run `validate.py` on them, and present them with `present_files`.

## Draft every card in three slots

Before writing any prose back or any TSV, draft each card as three explicit slots:

```
FRONT:   <the question - one unambiguous answer>
ANSWER:  <the single thing to retrieve - ideally a word or short phrase>
CONTEXT: <optional: one or two sentences of explanation or a source quote, or "none">
```

**The ANSWER slot is the forcing function.** If the retrievable answer will not fit in a single short phrase, the card is testing more than one thing - split it now, before it becomes a dense back. Everything that is *explanation* rather than *the thing recalled* belongs in CONTEXT, which is read only after the answer is recalled.

The back is then assembled mechanically: ANSWER on its own line first, then `<br><br>` then CONTEXT. This gives you answer-first formatting for free and makes a wall-of-text back structurally impossible.

Example:

```
FRONT:   🔍 What kind of data does Cortex Search retrieve over?
ANSWER:  📄 Unstructured data
CONTEXT: It can dynamically adjust filters, retrieved columns, result counts, and time-decay based on the query.
```

The capability detail is context, not a second answer, so it sits below the line instead of turning the card into two facts wearing one coat. If the user also needs to recall the tunable settings, that is a *separate* card with its own ANSWER - not a longer back here.

## Card-writing rules

### One fact per card (atomicity)

This is the single most important rule and the most common failure - SuperMemo calls it the **minimum information principle**: the smaller the thing retrieved each repetition, the more reliably it sticks. Each card tests one specific piece of information. The deletable-sentence test: *if you can delete one sentence from the back and the card still makes sense, that sentence is a separate card.*

Front patterns that almost always smuggle in multiple facts - treat them as a signal to split before writing:
- "What is X?" for a concept with several defining properties → split into "What does X do?", "Where does X run?", "What does X return?"
- "What are the [plural]…?" → each item is its own card (or a cloze, if they are a genuine set - see references/cloze.md).
- A front joining two concepts with "and"/"or" → two fronts.
- "How does X compare to Y?" → usually 3+ independent facts; ask one dimension per card.

Back patterns to catch before finalising: two full sentences asserting different facts; "and" joining two independent clauses; a run of 3+ comma-separated independent items. A list whose items are **not true peers** (one contains another, or they relate hierarchically) must not be enumerated in one card - write separate cards plus one that tests the relationship explicitly.

**Bad (too much at once):** Front: What is photosynthesis? · Back: The process by which plants convert light energy into chemical energy, using carbon dioxide and water to produce glucose and oxygen, in the chloroplasts.

**Good (atomic):** "What is the purpose of photosynthesis?" → convert light energy to chemical energy. "What two raw materials does it need?" → carbon dioxide and water. "What two products does it yield?" → glucose and oxygen. "Where does it occur?" → the chloroplasts.

### Write a front with exactly one answer

A good front has one correct answer and gives enough context to stand alone when reviewed in six months ("In Python's `range()`, what does the second argument specify?" not "what does the second argument do?").

- **No yes/no fronts** - a 50% guess rate tests nothing. "Which organelle is the powerhouse of the cell?" not "Is the mitochondrion the powerhouse?"
- **Do not telegraph the answer in the question.** "When should you use Cortex Agents for reasoning across structured and unstructured data?" answers itself. Ask instead "Which Cortex Agents capability combines SQL over semantic views with retrieval from documents?" The cue and the answer must not overlap.

### Avoid interference between near-identical cards

Interference - similar cards making each other hard to recall - is one of the biggest causes of forgetting. If two cards could be answered by swapping their answers without anyone noticing, they will interfere.

**Numbered-sequence fronts are the most common instance, and a hard defect to fix:**

Bad (fronts differ only by an ordinal; trains rote "step 3 = X"):
- "What is the first step in the 5-step lifecycle?"
- "What is the second step in the 5-step lifecycle?"

Good (each front is self-differentiating by content; the number is gone):
- "In the lifecycle, what do you do in the Snowsight playground before integrating an agent?"
- "After an agent is built, how do you call it from your own application?"

If the *order or membership* of the sequence is itself worth memorising, add one cloze card with an `<ol>` (see references/cloze.md) - do not spread the sequence across numbered Q&A fronts.

### Put the answer first on the back

The retrievable answer is the first thing on the back, on its own line, in the fewest correct words. Explanation, example, and any source quote come after, separated by `<br>`. Never deliver a back as a single dense paragraph when it holds more than one distinct point - a wall of text is hard to scan in review and is a defect to fix before output. (The three-slot draft already gives you this if you assembled the back from it.)

For genuinely arbitrary facts (a name, an unmotivated order), a short mnemonic on the back - answer first, then `<br><i>(mnemonic: …)</i>` - can save a future leech. Don't force mnemonics onto facts that already have logical structure.

### Stamp volatile facts

Stable facts (anatomy, basic maths, history) need no stamp. Anything that goes out of date - statistics, prices, "current" office-holders, software behaviour - should carry a marker ("As of <b>2026</b>, …" or "In <b>Python 3.12</b>, …") and a tag like `as_of_2026`, so stale cards are easy to find and the user doesn't trust a figure that has moved.

## The audit (before writing any file)

There are two kinds of check, and they are not interchangeable.

**Mechanical checks - delegate to the script.** Em dash, HTML escaping, column counts, cloze syntax, emoji presence: these are lexical and `evals/validate.py` already checks them reliably. Run it on the finished TSV files (`python evals/validate.py /mnt/user-data/outputs/`). Do not hand-roll a regex for these.

**Judgment checks - reason about every card yourself.** Atomicity, one-answer fronts, answer-telegraphing, interference, and cloze-vs-Q&A choice cannot be checked by any script. A green `validate.py` says only that the deck will *import* - it will happily pass a deck where every back hides three facts and every front interferes. **Never treat a passing script as evidence the cards are good.** (This is a real and easy trap: a character-level check for `—` and emoji can rubber-stamp a deck riddled with multi-fact backs.)

Before writing any file, emit a **per-card audit table** - one row per card - and reason through each judgment gate explicitly. Quote the offending text on any fail, fix it, and re-emit affected rows:

| # | Front (short) | One fact only? | One answer, not yes/no, not telegraphed? | No interference with siblings? | Right type (Q&A vs cloze)? |
|---|---------------|----------------|------------------------------------------|-------------------------------|----------------------------|

Emitting this table is mandatory and is the main quality gate. If you are tempted to write "all pass" without quoting specifics, that is the signal you are rubber-stamping - go back and read each card.

## Choosing the card type

- **Basic Q&A** is the default for concepts, processes, and "why/how" facts. Everything above assumes basic cards.
- **Cloze** only when a single card's answer is genuinely a list, sequence, or set of 3+ items where membership or order is the thing to memorise - and prefer recasting into Q&A by distinguishing feature first. When you do use cloze, the cloze TSV file is required alongside the basic one. See **references/cloze.md** for when it earns its place, HTML-list markup, hints, overlapping cloze for long ordered sequences, and regrouping sets into something meaningful.
- **Reversed (bidirectional)** only when both directions have a single well-defined answer - vocabulary, term↔symbol, abbreviation↔expansion. See **references/reversed-cards.md**.

## Formatting essentials

- **Never use an em dash (`—`)** anywhere in card content - use a spaced hyphen ` - ` or restructure. (The en dash `–` is fine in numeric ranges.)
- **Start each side with an emoji**, varied across the deck and only *loosely* topical - an emoji that uniquely identifies the answer becomes an unwanted retrieval cue.
- **Use HTML, not Markdown** (Anki strips Markdown): `<b>` for key terms, `<i>` for emphasis or quotes, `<br>` for line breaks. Bold the key term on each side so the eye lands on it.
- **Never include labels** like `Q:`, `A:`, `Front:` in card content - Anki provides the framing.

For HTML escaping of literal `<`, `>`, `&` (the most common way code/maths cards silently break), the colour span, source-quote markup, and the TSV-writing script, see **references/formatting.md**. Check it before output for any card whose content contains `<`, `>` or `&`.

## Output

Write up to three TSV files to `/mnt/user-data/outputs/`: `<slug>_basic.tsv` always; `<slug>_cloze.tsv` if you made cloze cards; `<slug>_reversed.tsv` if you made reversed cards. Generate only what you produced.

**Basic TSV format:**

```
#separator:tab
#html:true
#notetype:Basic
#deck:<readable deck name>
#tags column:3
<front><TAB><back><TAB><tags>
```

`#html:true` renders your tags; `#deck:` pre-selects a deck (a default the user can override); `#tags column:3` marks the third data column as space-separated tags. The cloze and reversed formats live in their reference files.

**Deck naming:** pick a descriptive name from the topic *before* generating (e.g. `Biology::Cell Structure`, not `deck`), use it for `#deck:` and derive the filename slug from it in `lowercase_with_underscores`.

**Tags:** give every card 2-4 hierarchical tags using `::` (e.g. `biology::cell_structure::organelles`), plus a flat keyword or two for cross-cutting themes (`exam_critical`, `as_of_2026`). Keep the hierarchy two or three levels deep.

**Write the file with a small Python script** (manual `\t`-join, never the `csv` module - it mangles quotes) and **run `validate.py` on the result** before presenting. The script and `sanitise()` helper are in references/formatting.md.

**Preview format** (show first 5-10 for long decks, noting "showing first 8 of 47"):

```
**Card 1** · tags: `biology::cell_structure::organelles`
Front: 🧬 Which organelle is known as the **powerhouse of the cell**?
Back: ⚡ The **mitochondrion**.<br><br>It generates most of the cell's ATP through aerobic respiration.
```

## Reference files

Read these when the situation calls for them - they are not needed for an ordinary basic-Q&A deck:

- **references/cloze.md** - when cloze is justified, HTML-list markup, `<ol>` vs `<ul>`, hints, overlapping cloze for 6+ ordered sequences, regrouping sets, and the cloze TSV format.
- **references/reversed-cards.md** - bidirectional cards, when both directions are single-answer, and the reversed TSV format.
- **references/formatting.md** - full HTML rules, escaping `<`/`>`/`&`, colour, quotes, the TSV-writing script, and edge cases for type-in answers.
- **references/edge-cases.md** - other-language sources, code/LaTeX, image-heavy material and Image Occlusion, thin sources, and requested card counts.
- **references/examples.md** - fully worked decks for tricky medical/scientific or code-heavy material.
