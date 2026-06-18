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
7. **Build and check.** Run `python scripts/build_deck.py deck.json /mnt/user-data/outputs/`, then `python scripts/check_deck.py /mnt/user-data/outputs/`. The checker is mainly structural, but it also emits **judgment-warnings** for a few front defects it can detect heuristically (yes/no fronts, binary "A or B?" fronts) - treat any such warning as a card to revisit, not noise to ignore. Preview in chat and present the files with `present_files`.

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

The test applies to the **context slot too**, which is where extra facts most often hide. Because context is framed as harmless explanation, it is easy to park a second or third testable fact there - "Also: slower R/W speeds and higher power consumption," or "ROM also stores encryption keys" tacked onto a card about firmware. Context should *explain or anchor the one answer*, not assert new facts the card never tests. A useful inversion: a fact that appears **only** in a context slot and is never the answer of any card is not context - it is a missing card. When you spot one, promote it to its own card rather than leaving it to be passively reread.

Atomicity also helps Anki's modern scheduler, **FSRS** (now built in and increasingly the default): it estimates each card's difficulty from your review history, and a card bundling several facts gets answered inconsistently, producing noisy estimates - so atomic cards schedule better as well as stick better.

Front patterns that almost always smuggle in multiple facts - treat them as a signal to split before writing:
- "What is X?" for a concept with several defining properties → split into "What does X do?", "Where does X run?", "What does X return?"
- "What are the [plural]…?" → each item is its own card (or a cloze, if they are a genuine set - see references/cloze.md).
- A front joining two concepts with "and"/"or" → two fronts.
- "How does X compare to Y?" → usually 3+ independent facts; ask one dimension per card.

Back patterns to catch before finalising: two full sentences asserting different facts; "and" joining two independent clauses; a run of 3+ comma-separated independent items.

**A 3+ item enumeration is never a basic answer - there is no "recalled as a unit" exception.** If the ANSWER slot is a list, sequence, or set of named steps (comma-joined, "and"-joined, or written `A - B - C`), the card is testing membership/order, not one fact, and recalling it from a single prompt trains nothing reliably. Resolve it one of two ways: **convert to a cloze** with an `<ol>`/`<ul>` (when membership or order is the thing to learn - see references/cloze.md), or **split into one card per distinguishing feature** (when each item carries content - "which step happens in the Snowsight playground?" not "what is step 3?"). A list of items that are **not true peers** (one contains another, or they relate hierarchically) must never be enumerated in one card - write separate cards plus one that tests the relationship. `build_deck.py` **hard-fails the build** when a basic answer literally encodes a list (an HTML list, or a 3+ item dash-join); the comma/conjunction cases it can only warn on, so they are yours to catch in the audit.

Revising against an exam **mark scheme** is the one case that bends this - a 3-mark question whose scheme lists five acceptable points is asking you to *generate* a set, not recall a single fact. That does not license a five-fact back; it calls for a deliberately layered deck. See "Mark-scheme and exam revision" below before you fold an enumeration into one basic card.

**Bad (too much at once):** Front: What is photosynthesis? · Back: The process by which plants convert light energy into chemical energy, using carbon dioxide and water to produce glucose and oxygen, in the chloroplasts.

**Good (atomic):** "What is the purpose of photosynthesis?" → convert light energy to chemical energy. "What two raw materials does it need?" → carbon dioxide and water. "What two products does it yield?" → glucose and oxygen. "Where does it occur?" → the chloroplasts.

### Write a front with exactly one answer

A good front has one correct answer and gives enough context to stand alone when reviewed in six months ("In Python's `range()`, what does the second argument specify?" not "what does the second argument do?").

- **No yes/no fronts, and no two-option "A or B?" fronts** - both hand the learner a 50% guess. "Is the mitochondrion the powerhouse?" is the obvious case; "Which processor type has the larger instruction set - CISC or RISC?" is the same defect in disguise, and the more tempting one because it reads like a real question. A binary choice baked into the front also lets the learner memorise the *position* ("the first option is always right") instead of the fact. Recast as an open front: "What does CISC's instruction set size tell you about its design?" or test the property directly without naming both options.
- **Do not telegraph the answer in the question.** This includes *entailment*, not just word overlap. The lexical case ("When should you use Cortex Agents for reasoning across structured and unstructured data?" - the front lists the answer) is easy to spot. The subtler case is a premise that *entails* its own answer: "Why is flash storage more <b>durable</b> than magnetic?" all but writes "no moving parts," because at this level durability has only one cause. Ask instead "What physical property of flash storage suits a device that gets knocked about?" The cue and the answer must not overlap or imply each other.

### Avoid interference between near-identical cards

Interference - similar cards making each other hard to recall - is one of the biggest causes of forgetting. If two cards could be answered by swapping their answers without anyone noticing, they will interfere.

**Numbered-sequence fronts are the most common instance, and a hard defect to fix:**

Bad (fronts differ only by an ordinal; trains rote "step 3 = X"):
- "What is the first step in the 5-step lifecycle?"
- "What is the second step in the 5-step lifecycle?"

Good (each front is self-differentiating by content; the number is gone):
- "In the lifecycle, what do you do in the Snowsight playground before integrating an agent?"
- "After an agent is built, how do you call it from your own application?"

The ordinal need not be a literal number to cause this. Prose **stage cues** - "what does the BIOS do *when first powered on*?" versus "what does it do *after POST*?" - differentiate the fronts by position in a sequence rather than by content, so they interfere exactly like "step 1 / step 2." The fix is the same: rebuild each front around the content of its own answer ("What test does the BIOS run to check hardware is present?" / "What does the BIOS load into memory once hardware checks pass?") so neither front leans on the stage word.

If the *order or membership* of the sequence is itself worth memorising, add one cloze card with an `<ol>` (see references/cloze.md) - do not spread the sequence across numbered Q&A fronts.

### Put the answer first on the back

The retrievable answer is the first thing on the back, on its own line, in the fewest correct words. Explanation, example, and any source quote come after, separated by `<br>`. The three-slot draft already gives you this if you assembled the back from it.

For genuinely arbitrary facts (a name, an unmotivated order), a short mnemonic on the back - answer first, then `<br><i>(mnemonic: …)</i>` - can save a future leech. Don't force mnemonics onto facts that already have logical structure.

### Stamp volatile facts

Stable facts (anatomy, basic maths, history) need no stamp. Anything that goes out of date - statistics, prices, "current" office-holders, software behaviour - should carry a marker ("As of <b>2026</b>, …" or "In <b>Python 3.12</b>, …") and a tag like `as_of_2026`, so stale cards are easy to find and the user doesn't trust a figure that has moved.

## The audit (before writing any file)

There are two kinds of check, and they are not interchangeable. **Mechanical checks** - em dash, HTML escaping, column counts, cloze syntax - are lexical, so delegate them to `scripts/check_deck.py` and don't hand-roll a regex. **Judgment checks** - atomicity, one-answer fronts, telegraphing, interference, cloze-vs-Q&A - cannot be scripted and are yours alone. The one overlap: `check_deck.py` now also emits *heuristic* warnings for the two front defects that happen to be lexically detectable (yes/no fronts, binary "A or B?" fronts). Those warnings are a safety net for when the audit misses them - they do not replace the audit, and they catch none of the defects that actually need reading the card (telegraphing, interference, smuggled context). A clean run with no front-warnings still tells you nothing about quality.

The point that ties the whole skill together: **a green `check_deck.py` means only that the deck will *import*, never that the cards are good.** It will happily pass a deck where every back hides three facts and every front interferes. Never treat a passing script as evidence of quality - that is a real and easy trap, because a character-level check for `—` and emoji looks reassuring while saying nothing about whether a single card is worth learning.

Before writing any file, emit a **per-card audit table** - one row per card - and reason through each gate explicitly. Quote the offending text on any fail, fix it, and re-emit affected rows. This table is a hard precondition: the build script is not run until it has been emitted and every failure fixed. It also catches the two gates the three-slot draft does *not* - telegraphed fronts and missing volatile stamps - so do not skip those columns. The telegraphing column covers the **front emoji** as well as the text: it must be the topic's shared category marker, not an answer-specific picture, so an answer-hinting emoji (💨 on a CO₂ card) fails that column exactly as an answer-hinting word would.

**Audit as a critic, not as the author.** You just wrote these cards, so your instinct is to confirm they are fine - that instinct is the problem, and it is why a deck that "passed" its own audit still falls apart when someone else reads it cold. Switch stance deliberately:

- **Re-read the card-writing rules first** (the "Card-writing rules", "Write a front with exactly one answer", and "Avoid interference" sections above) before you fill in a single row. Audit against the text on the page, not against your memory of it - memory is where the rules quietly soften.
- **Assume every card is broken until you can quote why it passes.** A row clears only when you have named the specific thing that *could* have failed and shown it does not ("answer is one phrase: 'no moving parts'; front says 'durable' - would entail the answer, so reworded"). A bare "pass" with nothing quoted is not an audit, it is a rubber stamp.
- **Zero revisions is a red flag, not a triumph.** First drafts of a deck essentially never come out clean; if your audit changed nothing, you almost certainly skimmed. Go back and find the weakest two or three cards - there are always some - and either fix them or write down the explicit reason each survives scrutiny.

| # | Front (short) | One fact only? (incl. context slot) | One answer (not yes/no or "A or B?", not telegraphed inc. entailment, text or emoji)? | No interference with siblings (incl. stage cues)? | Right type (Q&A vs cloze; closed set only)? | Volatile fact stamped (or n/a)? |
|---|---------------|----------------|------------------------------------------|-------------------------------|----------------------------|---------------------------------|

If you are tempted to write "all pass" without quoting specifics, that is the signal you are rubber-stamping - go back and read each card. The **one-fact column covers the context slot**: if a card's context asserts a fact that is never any card's answer, that is a smuggled fact - fail the row and promote it to its own card. The **type column has one banned answer: "recalled as a unit"** (or "one unit", "as a set", "one sequence") - the exact phrase a multi-item back uses to slip past. If a card's answer is a list or sequence, the type column must name the *disposition* ("cloze, order matters" or "split into N cards"), not assert the list is one fact. `build_deck.py` only hard-fails on *literally encoded* lists (HTML lists, dash-joins), so a comma- or "and"-joined enumeration ("Plan, Use tools, Reflect and respond") builds cleanly and is yours to catch here.

## Choosing the card type

- **Basic Q&A** is the default for concepts, processes, and "why/how" facts. Everything above assumes basic cards.
- **Cloze** only when a single card's answer is genuinely a list, sequence, or set of 3+ items where membership or order is the thing to memorise - and prefer recasting into Q&A by distinguishing feature first. When you do use cloze, the cloze TSV file is required alongside the basic one. See **references/cloze.md** for when it earns its place, HTML-list markup, hints, overlapping cloze for long ordered sequences, and regrouping sets.
- **Reversed (bidirectional)** only when both directions have a single well-defined answer - vocabulary, term↔symbol, abbreviation↔expansion. See **references/reversed-cards.md**.

## Mark-scheme and exam revision

Revising against an exam mark scheme is a special case, because the thing being assessed is not only "do you know fact X" but "can you, cold, produce N distinct valid points about a topic." A question worth 3 marks often has a scheme listing five or more acceptable points: you earn one mark per distinct point up to the cap, and you choose which to write. That is an *enumeration* skill - generating a list from a topic name under time pressure - and a deck of purely atomic cards does not train it. A student can know every individual advantage of flash storage and still freeze on "give three," because they have practised recognising single facts but never producing the list.

The temptation is to "solve" this by relaxing atomicity - one card, five facts on the back, grade yourself *good* if you got three. Resist it. That is the exact failure atomicity guards against: the easy points hide the hard ones, you mark success on partial recall, and FSRS's difficulty estimate for the card goes to noise. The right move keeps atomic cards doing the memorising and adds *separate* cards whose job is the enumeration skill. Build the deck in three layers.

**Layer 1 - atomic cards (the backbone).** Exactly as everywhere else in this skill: one mark-scheme point per card, one retrievable answer. This is where each fact is actually learned, so build these first and never skip them. The audit's atomicity gate applies to this layer in full.

**Layer 2 - membership via cloze lists.** When the scheme is a genuine *closed, canonical* set ("the advantages of flash storage" - a bounded list every textbook agrees on), encode the whole set as a cloze with an `<ul>`/`<ol>`, one `{{cN::}}` per item (see references/cloze.md). This is not a workaround - it is what cloze is *for*. Anki schedules each deletion as its own review event, so you keep almost all of the atomic benefit (one blank shown at a time, clean per-item difficulty) while encoding which items belong together. But check the set is actually closed first: a mark scheme that says "state **two** output devices" from a long open list of valid answers is *not* a closed set, and a cloze of the two you happened to pick teaches the false lesson that those two are *the* answer. For "name any N from many," skip the cloze - use Layer 3 free recall, or a few distinguishing-feature Q&A cards ("which output device gives the editor *audio* feedback?"). Where the set genuinely is closed, learn *all* the listed points, not just the number of marks on offer - more valid points banked means a safer pick under exam pressure.

**Layer 3 - free recall (sparse).** Cloze lists still *cue* you: the visible items prompt the blank, so they train membership, not cold generation. For the open extended-answer questions (the 9- and 12-mark "discuss" items), add one free-recall card per topic - a plain prompt like "Give three or more advantages of flash storage," the full list on the back, and a self-grade rule written on the back ("<i>Again if fewer than 3, Good if 3+</i>"). These deliberately break atomicity, and that is the point: their job is to rehearse cold enumeration, which neither atomic nor cloze cards do. Keep them rare - one per discussable topic, not one per fact - and tag them (e.g. `enumeration`) so the noisier scheduling they cause is contained and easy to find. The compare-and-discuss questions benefit most.

Rule of thumb for a mark-scheme deck: atomic cards carry the knowledge, cloze lists carry the set membership, and a handful of tagged free-recall cards rehearse the generate-N-points task. Layers 2 and 3 are *named, deliberate* exceptions to atomicity for one specific skill - not a general loosening, and not an excuse to skip the audit on Layer 1.

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
