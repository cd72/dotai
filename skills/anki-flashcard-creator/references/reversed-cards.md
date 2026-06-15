# Reversed (bidirectional) cards

Read this when the source is vocabulary, a glossary, or term/definition pairs.

## When both directions are worth training

Some material must be recalled in *both* directions, and a one-way Q&A trains only one. Use reversed cards when the front and back are a symmetric pair the user must produce either way round:

- **Vocabulary and translation** - `gato` ↔ `cat`. The learner needs word→meaning *and* meaning→word.
- **Term ↔ definition** where both directions are genuinely useful - a symbol and its name, an abbreviation and its expansion.

The test is whether *each* direction has a single, well-defined answer. Only reverse when that holds.

**Do not reverse ordinary factual Q&A.** "Which organelle is the powerhouse of the cell?" reversed becomes "mitochondrion → ?", which has many valid answers and trains nothing. When the source is clearly a vocabulary list or glossary, default to offering reversed cards (or produce them and say so). Otherwise leave cards one-way.

This is *deliberate redundancy*, not duplication: active and passive recall of the same pair each strengthen the memory and resist interference, which does not violate the minimum-information principle. (Two cards that say the same thing the same way, by contrast, are waste - cut the weaker one.)

## Reversed TSV format

Use Anki's **`Basic (and reversed card)`** note type. It takes the same two fields (Front, Back) but generates *two* cards per note, one in each direction, so you write the pair once. Emit a third TSV file, identical to the basic format but with the reversed note type:

```
#separator:tab
#html:true
#notetype:Basic (and reversed card)
#deck:<readable deck name>
#tags column:3
<front><TAB><back><TAB><tags>
```

The writing script is the same as for basic cards (see references/formatting.md) - only the `#notetype:` header changes.
