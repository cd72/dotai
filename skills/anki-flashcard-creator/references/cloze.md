# Cloze cards

Read this when a fact is a genuine list, sequence, or set. For anything else, basic Q&A is better.

## When cloze actually earns its place

Use cloze only when a single card's answer contains **3 or more independent items** - a list, sequence, enumeration, or set of named steps where the items themselves are what must be memorised. Even then, prefer recasting into Q&A first.

SuperMemo's guidance is that *enumerations and unordered sets are intrinsically hard to retain* (Wozniak's rules on avoiding sets and enumerations): even a list of genuine peers is harder to learn than a set of meaningful Q&A cards. So treat a cloze list as a last resort. Before making one, try to:

- **Recast items into Q&A by distinguishing feature or relationship.** "Which Great Lake is the largest by area?" teaches more than "list the Great Lakes."
- **Regroup the set into something meaningful** (see "Regrouping sets" below).

Reserve the bare cloze list for cases where membership or order genuinely is the thing being memorised.

**Two anti-patterns to refuse outright:**

- **Cloze lists of non-peer items.** Before writing any cloze list, ask: do these items sit at the same level, or do they relate hierarchically (X contains Y; A is a kind of B)? If they are not true peers, a flat list hides the structure that needs learning. Write separate Q&A cards instead, including at least one that tests the relationship explicitly.
- **A Q&A card duplicating an existing cloze.** If a cloze already covers a list's membership, you do not also need a Q&A asking "what are the N items?" Keep one, not both.

## Markup: lay items out as an HTML list

Anki cloze syntax: `{{c1::hidden text}}`, `{{c2::…}}`, etc. Each distinct `cN` number produces a separate card from the same note, hiding that piece. Items sharing a number are hidden together on one card.

**Always lay the items out as an HTML list - never as a comma-separated run of clozes in one sentence.** A cloze note almost always exists *because* it holds a list, and lists render far more legibly stacked: each item gets its own line and the eye can find the gap being tested. Inline `{{c1::a}}, {{c2::b}}, {{c3::c}}` is the most common formatting mistake here - treat it as wrong unless the content genuinely is one flowing sentence (rare).

- Use `<ol>` when **order matters** (chronological steps, a lineage, smallest-to-largest).
- Use `<ul>` for **unordered sets** where order is irrelevant.
- One cloze per `<li>`. Keep a short stem as a lead-in so the card stands alone.
- Add a hint with `::hint`, e.g. `{{c1::Superior::largest by area}}`.
- Put anything useful (a mnemonic, grouping hint, ordering note) in the **Back Extra** field; don't leave it blank by default.

**Bad (inline - cramped):**
```html
The first three US presidents were {{c1::Washington}}, {{c2::Adams}}, and {{c3::Jefferson}}.
```

**Good (order matters → `<ol>`):**
```html
The first three US presidents, in order, were:
<ol>
  <li>{{c1::Washington}}</li>
  <li>{{c2::Adams}}</li>
  <li>{{c3::Jefferson}}</li>
</ol>
```

**Good (order irrelevant → `<ul>`):**
```html
The three primary colours are:
<ul>
  <li>{{c1::red}}</li>
  <li>{{c2::blue}}</li>
  <li>{{c3::yellow}}</li>
</ul>
```

Each note is one row in the TSV, so write the list markup with no literal newlines inside the field - the `<li>`/`<ul>` tags handle the visual breaks. The HTML renders correctly regardless of internal whitespace.

## Overlapping cloze for long ordered sequences

A single note that hides every item at once is fine for short sets, but for a *long ordered sequence* where the user must reproduce the order, it trains ordering poorly: every other item stays visible as an anchor, so the learner never recalls what follows what. The SuperMemo remedy is **overlapping cloze** - a sliding window of notes that each hide one item while showing its neighbours, so the brain rehearses the transitions (like drilling the alphabet as "…C, ?, E…", not "recite all 26").

Use a single `c1` per note and slide it along, keeping one or two neighbours visible:

```
note 1:  Order of operations: Parentheses, {{c1::Exponents}}, Multiplication
note 2:  Order of operations: Exponents, {{c1::Multiplication}}, Division
note 3:  Order of operations: Multiplication, {{c1::Division}}, Addition
note 4:  Order of operations: Division, {{c1::Addition}}, Subtraction
```

Each note is one row and yields one card. Consecutive windows overlap deliberately (Multiplication is shown on notes 1 and 3, hidden on note 2) - that planned redundancy is what builds the chain. Use this when a sequence has roughly **6+ ordered items and the order is the point** (the alphabet, cranial nerves, a decay chain, a ranked list). For 3-5 items the single stacked-list note is simpler. To widen the gap, hide a short run with one shared number - `…A {{c1::B}} {{c1::C}} {{c1::D}} E…` hides B, C, D together. It can help to keep one whole-sequence card too, or have the user recite the full list once after the individual repetitions.

## Regrouping sets into meaningful structure

Before making *any* cloze list for a set, ask whether the set can be **regrouped into something meaningful** - almost always better than a bare membership list. Wozniak's worked example takes the 15 EU members and, instead of one impossible "list all members" card, builds small context-anchored cards around the *history* of who joined when (the founding six, then the 1973 entrants, then 1981, and so on). The flat set becomes a structured, partly-causal story that is far easier to retain and teaches more. So for a set, prefer: group by a meaningful dimension (chronology, geography, function), give each group its own small card with context, and fall back to a stacked cloze list only when no meaningful structure exists and the bare membership genuinely must be memorised.

## Cloze TSV format

When you make any cloze cards, the cloze TSV file is **required** alongside the basic one - generate it automatically, don't wait to be asked.

```
#separator:tab
#html:true
#notetype:Cloze
#deck:<readable deck name>
#tags column:3
<text with {{c1::cloze}}><TAB><back extra><TAB><tags>
```

The Cloze note type has two content fields, **Text** and **Back Extra**, plus tags - so the columns are: cloze text, then Back Extra, then tags. Back Extra shows below the answer on every card from the note, so it is the right home for the short explanation or source quote (the equivalent of a Q&A card's context). Leave it empty (an empty column, but keep the tab) only when there is genuinely nothing useful to add. Because Back Extra is column 2, tags are column 3: `#tags column:3`.

The cloze TSV is written by `scripts/build_deck.py` from your deck JSON (use cloze-type card objects); see references/formatting.md for the schema.
