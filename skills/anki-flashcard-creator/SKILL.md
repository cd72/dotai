---
name: anki-flashcard-creator
description: Generate high-quality Anki flashcards from source material - articles, syllabi, textbook chapters, lecture notes, documentation, transcripts, or any study material. Use this skill whenever the user wants to make flashcards, study cards, revision cards, spaced-repetition cards, or Anki cards from content they share, even if they don't say the word "Anki". Also trigger when the user asks to "memorise", "revise", "study", or "learn" a piece of source material in a structured way, or asks to turn notes/a chapter/a paper/a syllabus into something they can revise from. Produces both an inline preview of the cards and tab-separated files ready to import directly into Anki.
---

# Anki Flashcard Creator

Turn any source material into a deck of well-crafted Anki flashcards that follow established spaced-repetition principles (Wozniak's 20 rules, SuperMemo guidance), then deliver them as an inline preview plus Anki-importable TSV files.

Making cards that *import* is easy; making cards that are *easy to learn* is the whole job. That second part is a judgment task, not a formatting task. The defects that make a deck painful - a back that hides three facts, six fronts that differ only by a number, a question that gives away its own answer - are all invisible to a script. So the value of this skill is in the per-card reasoning, and the workflow is built to force that reasoning into the open.

<!-- Maintainers: if you change output format (headers, columns, escaping, cloze markup, note types, files) or card-generation behaviour, run a sample deck JSON through scripts/build_deck.py and scripts/check_deck.py before shipping. -->

## Two things you must write out, not do in your head

The single most common way this skill fails is collapsing the judgment work into one mental pass and going straight to output. Two artifacts have to appear **in your response**:

1. **A committed three-slot draft of every card** (see "Draft every card in three slots"). The ANSWER slot is a forcing function, but it only binds if you actually write it down *before* assembling the back - a multi-fact back is structurally impossible once you've committed to a single-phrase answer first.
2. **A visible per-card audit table** (see "The audit") before any file is written - the judgment pass, separate from the mechanical one.

If you are about to write a deck JSON or TSV and you have not emitted both, stop and emit them first.

## Workflow

1. **Read the source in full.** Read the uploaded file, the pasted text, or fetch the URL. Card quality depends on knowing what is important versus incidental, so do not skim.
2. **Confirm scope if the source is long.** For sources over ~5,000 words or with clearly distinct sections, ask whether the user wants the whole thing or specific parts. For shorter sources, just proceed.
3. **Plan coverage.** Identify the concepts, definitions, processes, relationships, and key facts worth recalling. Aim for comprehensive coverage of *important* content - one card per atomic fact - not every sentence. Skip genuine trivia, but do not over-prune load-bearing basics.
4. **Choose the card type for each fact** - basic Q&A by default; cloze or reversed only when they genuinely fit (see "Choosing the card type").
5. **Draft and commit every card** (see "Draft every card in three slots"). Write the drafts out - as the deck JSON when you have code execution (its `front`/`answer`/`context` fields *are* the three slots), or as a visible `FRONT`/`ANSWER`/`CONTEXT` list otherwise. **Hard checkpoint: do not continue until the drafts are written out.** If any card's ANSWER cannot be a single short phrase, split it here, before the audit.
6. **Audit the committed drafts** (see "The audit"). Emit the per-card table covering every judgment gate. **Hard checkpoint: no TSV is written until this table has been emitted and every failure fixed.**
7. **Build and check.** Run `python scripts/build_deck.py deck.json /mnt/user-data/outputs/`, then `python scripts/check_deck.py /mnt/user-data/outputs/`. Preview in chat and present the files with `present_files`.

## Draft every card in three slots

Draft each card as three explicit slots, written out as a committed artifact in your response, not an internal scratchpad. With code execution the deck JSON *is* this draft - its `front`, `answer`, and `context` fields are the three slots - so write the JSON here at the draft step rather than reconstructing it later. Without code execution, write a visible list in this shape:

```
FRONT:   <the question - one unambiguous answer>
ANSWER:  <the single thing to retrieve - ideally a word or short phrase>
CONTEXT: <optional: one or two sentences of explanation or a source quote, or "none">
```

Fill in ANSWER as a single short phrase *before* you think about the back. If the answer will not fit in a short phrase, the card is testing more than one thing - split it now. Everything that is *explanation* rather than *the thing recalled* belongs in CONTEXT, which is read only after the answer. (`build_deck.py` warns when an answer still looks multi-fact, but the discipline is yours - the warning is a backstop, not the gate.)

The back is then assembled mechanically by the build script: ANSWER on its own line first, then `<br><br>`, then CONTEXT. That gives you answer-first formatting for free and makes a wall-of-text back structurally impossible.

Example:

```
FRONT:   ❄️ What kind of data does Cortex Search retrieve over?
ANSWER:  📄 Unstructured data
CONTEXT: It can dynamically adjust filters, retrieved columns, result counts, and time-decay based on the query.
```

The capability detail is context, not a second answer, so it sits below the line instead of turning the card into two facts wearing one coat. If the user also needs to recall the tunable settings, that is a *separate* card with its own ANSWER - not a longer back here.

## Card-writing rules

### One fact per card (atomicity)

This is the single most important rule and the most common failure - SuperMemo calls it the **minimum information principle**: the smaller the thing retrieved each repetition, the more reliably it sticks. Each card tests one specific piece of information. The deletable-sentence test: *if you can delete one sentence from the back and the card still makes sense, that sentence is a separate card.*

Atomicity also helps Anki's modern scheduler, **FSRS** (now built in and increasingly the default): it estimates each card's difficulty from your review history, and a card bundling several facts gets answered inconsistently, producing noisy estimates - so atomic cards schedule better as well as stick better.

Front patterns that almost always smuggle in multiple facts - treat them as a signal to split before writing:
- "What is X?" for a concept with several defining properties → split into "What does X do?", "Where does X run?", "What does X return?"
- "What are the [plural]…?" → each item is its own card (or a cloze, if they are a genuine set - see references/cloze.md).
- A front joining two concepts with "and"/"or" → two fronts.
- "How does X compare to Y?" → usually 3+ independent facts; ask one dimension per card.

Back patterns to catch before finalising: two full sentences asserting different facts; "and" joining two independent clauses; a run of 3+ comma-separated independent items.

**A 3+ item enumeration is never a basic answer - there is no "recalled as a unit" exception.** If the ANSWER slot is a list, sequence, or set of named steps (comma-joined, "and"-joined, or written `A - B - C`), the card is testing membership/order, not one fact, and recalling it from a single prompt trains nothing reliably. Resolve it one of two ways: **convert to a cloze** with an `<ol>`/`<ul>` (when membership or order is the thing to learn - see references/cloze.md), or **split into one card per distinguishing feature** (when each item carries content - "which step happens in the Snowsight playground?" not "what is step 3?"). A list of items that are **not true peers** (one contains another, or they relate hierarchically) must never be enumerated in one card - write separate cards plus one that tests the relationship. `build_deck.py` **hard-fails the build** when a basic answer literally encodes a list (an HTML list, or a 3+ item dash-join); the comma/conjunction cases it can only warn on, so they are yours to catch in the audit.

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

The retrievable answer is the first thing on the back, on its own line, in the fewest correct words. Explanation, example, and any source quote come after, separated by `<br>`. The three-slot draft already gives you this if you assembled the back from it.

For genuinely arbitrary facts (a name, an unmotivated order), a short mnemonic on the back - answer first, then `<br><i>(mnemonic: …)</i>` - can save a future leech. Don't force mnemonics onto facts that already have logical structure.

### Stamp volatile facts

Stable facts (anatomy, basic maths, history) need no stamp. Anything that goes out of date - statistics, prices, "current" office-holders, software behaviour - should carry a marker ("As of <b>2026</b>, …" or "In <b>Python 3.12</b>, …") and a tag like `as_of_2026`, so stale cards are easy to find and the user doesn't trust a figure that has moved.

## The audit (before writing any file)

There are two kinds of check, and they are not interchangeable. **Mechanical checks** - em dash, HTML escaping, column counts, cloze syntax - are lexical, so delegate them to `scripts/check_deck.py` and don't hand-roll a regex. **Judgment checks** - atomicity, one-answer fronts, telegraphing, interference, cloze-vs-Q&A - cannot be scripted and are yours alone.

The point that ties the whole skill together: **a green `check_deck.py` means only that the deck will *import*, never that the cards are good.** It will happily pass a deck where every back hides three facts and every front interferes. Never treat a passing script as evidence of quality - that is a real and easy trap, because a character-level check for `—` and emoji looks reassuring while saying nothing about whether a single card is worth learning.

Before writing any file, emit a **per-card audit table** - one row per card - and reason through each gate explicitly. Quote the offending text on any fail, fix it, and re-emit affected rows. This table is a hard precondition: the build script is not run until it has been emitted and every failure fixed. It also catches the two gates the three-slot draft does *not* - telegraphed fronts and missing volatile stamps - so do not skip those columns. The telegraphing column covers the **front emoji** as well as the text: it must be the topic's shared category marker, not an answer-specific picture, so an answer-hinting emoji (💨 on a CO₂ card) fails that column exactly as an answer-hinting word would.

| # | Front (short) | One fact only? | One answer, not yes/no, not telegraphed (text or emoji)? | No interference with siblings? | Right type (Q&A vs cloze)? | Volatile fact stamped (or n/a)? |
|---|---------------|----------------|------------------------------------------|-------------------------------|----------------------------|---------------------------------|

If you are tempted to write "all pass" without quoting specifics, that is the signal you are rubber-stamping - go back and read each card. The **type column has one banned answer: "recalled as a unit"** (or "one unit", "as a set", "one sequence") - the exact phrase a multi-item back uses to slip past. If a card's answer is a list or sequence, the type column must name the *disposition* ("cloze, order matters" or "split into N cards"), not assert the list is one fact. `build_deck.py` only hard-fails on *literally encoded* lists (HTML lists, dash-joins), so a comma- or "and"-joined enumeration ("Plan, Use tools, Reflect and respond") builds cleanly and is yours to catch here.

## Choosing the card type

- **Basic Q&A** is the default for concepts, processes, and "why/how" facts. Everything above assumes basic cards.
- **Cloze** only when a single card's answer is genuinely a list, sequence, or set of 3+ items where membership or order is the thing to memorise - and prefer recasting into Q&A by distinguishing feature first. When you do use cloze, the cloze TSV file is required alongside the basic one. See **references/cloze.md** for when it earns its place, HTML-list markup, hints, overlapping cloze for long ordered sequences, and regrouping sets.
- **Reversed (bidirectional)** only when both directions have a single well-defined answer - vocabulary, term↔symbol, abbreviation↔expansion. See **references/reversed-cards.md**.

## Formatting essentials

- **Never use an em dash (`—`)** anywhere in card content - use a spaced hyphen ` - ` or restructure. (The en dash `–` is fine in numeric ranges.)
- **Front emoji: one shared category marker per topic** (🧬 on *every* biology card, ⚖️ on every law card). Because many cards share it, it signals the subject without distinguishing their answers, so it cannot telegraph. Never use an answer-specific front emoji - 💨 on a CO₂ card or 🫁 on a "which organ?" card lets you answer from the picture. **Back emoji: free and decorative** - the back is seen only after recall, so it can't cue anything; vary it across the deck.
- **Use HTML, not Markdown** (Anki strips Markdown): `<b>` for key terms, `<i>` for emphasis or quotes, `<br>` for line breaks. Bold the key term on each side so the eye lands on it.
- **Never include labels** like `Q:`, `A:`, `Front:` in card content - Anki provides the framing.

For HTML escaping of literal `<`, `>`, `&` (the most common way code/maths cards silently break), the colour span, source-quote markup, and the deck JSON schema that `build_deck.py` expects, see **references/formatting.md**. Check it before output for any card whose content contains `<`, `>` or `&`.

## Output

The cards are written by **`scripts/build_deck.py`**, not by hand. You produce a small **deck JSON** describing the cards (pure content - fronts, answers, context, tags, card type); the script serialises it into the correct TSV files, guaranteeing correct headers, safe escaping, and answer-first backs (answer, blank line, context) so that formatting rule is enforced by the tool rather than left to memory.

Deck JSON shape (full schema and all three card types are in references/formatting.md):

```json
{
  "deck_name": "Biology::Cell Structure",
  "cards": [
    {"type": "basic", "front": "🧬 …?", "answer": "⚡ …", "context": "…", "tags": ["biology::cell_structure"]},
    {"type": "cloze", "text": "… {{c1::…}} …", "back_extra": "", "tags": ["…"]}
  ]
}
```

Then:

```
python scripts/build_deck.py deck.json /mnt/user-data/outputs/
python scripts/check_deck.py /mnt/user-data/outputs/
```

`build_deck.py` writes only the files you need (`<slug>_basic.tsv`, and `_cloze.tsv` / `_reversed.tsv` only if those cards exist) and derives the slug from `deck_name`. `check_deck.py` is the mechanical gate from "The audit" above - run it every time.

**Deck naming:** pick a descriptive `deck_name` from the topic *before* generating (e.g. `Biology::Cell Structure`, not `deck`). It sets the `#deck:` header (a default the user can override on import) and the filename slug.

**Tags:** give every card 2-4 hierarchical tags using `::` (e.g. `biology::cell_structure::organelles`), plus a flat keyword or two for cross-cutting themes (`exam_critical`, `as_of_2026`). Keep the hierarchy two or three levels deep.

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
- **references/formatting.md** - full HTML rules, escaping `<`/`>`/`&`, colour, quotes, the deck JSON schema for `build_deck.py`, and type-in answers.
- **references/edge-cases.md** - other-language sources, code/LaTeX, image-heavy material and Image Occlusion, thin sources, and requested card counts.
- **references/examples.md** - fully worked decks for tricky medical/scientific or code-heavy material.

The skill bundles two scripts in **scripts/**: `build_deck.py` (deck JSON → TSV files) and `check_deck.py` (mechanical import-safety check). Both run at output time.
