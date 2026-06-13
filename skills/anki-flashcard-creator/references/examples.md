# Worked Examples: Domain-Specific Card Patterns

These examples show how to apply the card-writing rules to common but tricky source-material types. Read this when the source involves dense technical content, code, formulas, or nested concepts where the right way to atomise isn't obvious.

---

## Example 1: A scientific concept with nested parts

**Source excerpt** (biology textbook):

> "The Krebs cycle, also called the citric acid cycle or tricarboxylic acid (TCA) cycle, takes place in the mitochondrial matrix. For each acetyl-CoA molecule that enters the cycle, it produces 3 NADH, 1 FADH2, 1 GTP (or ATP, depending on the cell type), and 2 CO2. The cycle was discovered by Hans Krebs in 1937, for which he later received the Nobel Prize."

**Bad approach** (one card, too much information):

```
Front: What is the Krebs cycle?
Back: A metabolic cycle in the mitochondrial matrix that produces NADH, FADH2, GTP, CO2, etc., discovered by Hans Krebs in 1937.
```

**Good approach** (atomic cards, multiple aspects each their own card):

```
Card 1
Front: 🧬 Where in the cell does the <b>Krebs cycle</b> take place?
Back: 🔬 In the <b>mitochondrial matrix</b>.<br><br><i>"The Krebs cycle… takes place in the mitochondrial matrix."</i>
Tags: biology metabolism krebs_cycle

Card 2
Front: ⚙️ What are the two alternative names for the <b>Krebs cycle</b>?
Back: 📚 The <b>citric acid cycle</b> and the <b>tricarboxylic acid (TCA) cycle</b>.
Tags: biology metabolism krebs_cycle

Card 3
Front: ⚡ How many <b>NADH</b> molecules does one turn of the Krebs cycle produce?
Back: 🔢 <b>3 NADH</b> per acetyl-CoA molecule entering the cycle.
Tags: biology metabolism krebs_cycle energy

Card 4
Front: 🔥 How many <b>FADH₂</b> molecules does one turn of the Krebs cycle produce?
Back: 🔢 <b>1 FADH₂</b> per acetyl-CoA.
Tags: biology metabolism krebs_cycle energy

Card 5
Front: 💨 How many <b>CO₂</b> molecules are released per turn of the Krebs cycle?
Back: 🌫️ <b>2 CO₂</b> molecules per acetyl-CoA.
Tags: biology metabolism krebs_cycle

Card 6 (cloze — list of products is a good cloze fit; items stacked as a list, not inline)
Text: 🧪 Per acetyl-CoA, the Krebs cycle produces:<ul><li>{{c1::3}} NADH</li><li>{{c2::1}} FADH₂</li><li>{{c3::1}} GTP</li><li>{{c4::2}} CO₂</li></ul>
Tags: biology metabolism krebs_cycle
```

Note: the "discovered by Hans Krebs in 1937" detail is borderline trivia for someone studying metabolism — skip it unless the user is studying history of science.

---

## Example 2: Code / syntax

**Source excerpt** (Python docs):

> "The `enumerate(iterable, start=0)` function returns an enumerate object. The iterable must be a sequence, an iterator, or some other object which supports iteration. The `__next__()` method of the iterator returned by enumerate() returns a tuple containing a count (from start which defaults to 0) and the values obtained from iterating over iterable."

**Good approach:**

```
Card 1
Front: 🐍 What does Python's <b>enumerate()</b> function return?
Back: 📦 An <b>enumerate object</b> — an iterator that yields <code>(index, value)</code> tuples.
Tags: python builtins iteration

Card 2
Front: 🔢 What is the default <b>start</b> value for Python's <code>enumerate()</code>?
Back: 0️⃣ <b>0</b> — pass <code>start=N</code> to begin counting from <i>N</i> instead.
Tags: python builtins iteration

Card 3
Front: 🐍 Write the call signature for Python's <code>enumerate()</code>.
Back: ⌨️ <code>enumerate(iterable, start=0)</code>
Tags: python builtins iteration syntax

Card 4
Front: 🔁 Given <code>enumerate(['a','b','c'], start=1)</code>, what tuples does it yield?
Back: 📦 <code>(1, 'a')</code>, <code>(2, 'b')</code>, <code>(3, 'c')</code>.
Tags: python builtins iteration examples
```

For code-heavy material, prefer Q&A format ("what does X do") and small "fill in the syntax" cards over big cloze deletions of full code blocks — those tend to be unreviewable.

---

## Example 3: A definition with multiple components

**Source excerpt** (law textbook):

> "Negligence is established when four elements are proved: (1) the defendant owed the claimant a duty of care; (2) the defendant breached that duty; (3) the breach caused the claimant's loss; and (4) the loss was not too remote."

This is a perfect cloze candidate — the four-part list maps cleanly to four cloze deletions, and the order matters.

```
Card 1 (cloze, single note → 4 cards; unordered set, so <ul>)
Text: ⚖️ <b>Negligence</b> requires four elements:<ul><li>{{c1::duty of care}}</li><li>{{c2::breach of duty}}</li><li>{{c3::causation}}</li><li>{{c4::remoteness of damage}}</li></ul>
Tags: law tort negligence
```

But also add Q&A cards for the conceptual understanding of each element:

```
Card 2
Front: ⚖️ What does the <b>"causation"</b> element of negligence require?
Back: 🔗 That the defendant's breach <i>caused</i> the claimant's loss — typically tested with the "but for" test.
Tags: law tort negligence causation

Card 3
Front: ⚖️ What does the <b>"remoteness"</b> element of negligence require?
Back: 📏 That the loss was a reasonably foreseeable consequence of the breach — losses too far removed are not recoverable.
Tags: law tort negligence remoteness
```

This pairs the structural memory (the four-element list, via cloze) with the conceptual memory (what each element actually means, via Q&A). Both are needed and they don't duplicate each other.

---

## Example 4: A process or sequence

**Source excerpt** (chemistry):

> "The OSI model has seven layers, from bottom to top: Physical, Data Link, Network, Transport, Session, Presentation, Application."

```
Card 1 (cloze for the sequence; order matters, so <ol>)
Text: 🌐 The seven layers of the <b>OSI model</b>, bottom to top, are:<ol><li>{{c1::Physical}}</li><li>{{c2::Data Link}}</li><li>{{c3::Network}}</li><li>{{c4::Transport}}</li><li>{{c5::Session}}</li><li>{{c6::Presentation}}</li><li>{{c7::Application}}</li></ol>
Tags: networking osi_model

Card 2 (Q&A for the position of each — separate card per layer)
Front: 🌐 Which OSI layer sits <b>directly above</b> the Network layer?
Back: 🚚 The <b>Transport layer</b> (layer 4).
Tags: networking osi_model

Card 3
Front: 🌐 Which is the <b>top</b> layer of the OSI model?
Back: 🖥️ The <b>Application layer</b> (layer 7).
Tags: networking osi_model
```

For a 7-item sequence, don't make 7 separate "what comes after X" cards — that's overkill and the cloze captures the order. Just add a few cards for the most-tested positions or distinguishing features.

---

## Things to avoid in any domain

- **Yes/no cards.** "Is the mitochondrion the powerhouse of the cell?" → reframe as "Which organelle is known as the powerhouse of the cell?"
- **Cards that test recognition rather than recall.** "Which of these is X?" with options is fine for a quiz, terrible for spaced repetition. The card should make you produce the answer from memory.
- **Cards where the question contains the answer.** "What is the longest river in Africa, the Nile?" — obvious, but a surprisingly common failure mode when the source is being closely paraphrased.
- **Cards that test rote memorisation of trivia** (page numbers, exact publication years for unimportant works, full names of co-authors, etc.) unless the user has explicitly said they need that.
- **One giant cloze with 8+ deletions in the same sentence.** If a list is that long, split it across multiple cloze notes or multiple cards — the user will hate doing 8 deletions on the same sentence in a row.