# Edge cases

Read this when a source has an unusual shape. For ordinary prose sources, you won't need it.

## Source is in another language

Generate the cards in the same language as the source unless the user asks otherwise. Adjust emoji choices and HTML escaping the same way.

## Source contains formulas or code

Wrap inline formulas/code in `<code>…</code>`; for multi-line code use `<pre>…</pre>`. For LaTeX, Anki uses `\(…\)` inline and `\[…\]` for display math - the user needs MathJax enabled. Literal `<`, `>` and `&` inside code or inequalities must be escaped to `&lt;`, `&gt;`, `&amp;` (see references/formatting.md) or they vanish under HTML rendering. This is the single most common way a code card silently breaks.

## Source has images or diagrams worth learning (anatomy, maps, charts)

Imagery is one of the most powerful learning aids - a labelled diagram can be far more memorable than the equivalent prose, and a single illustration can seed many cards by hiding one labelled part at a time (graphic deletion).

But **TSV import cannot bundle media**: Anki only finds images already in the profile's `collection.media` folder, which this skill cannot write to. So do not emit `<img>` tags pointing at files the user doesn't have - they show as broken images. Instead:

1. Describe the visual in words on the text cards so the deck still works, and
2. When the source is genuinely visual, tell the user the strongest cards would be image-based, and point them at Anki's built-in **Image Occlusion** note type (Anki 23.10+), which is purpose-built for hiding labelled regions of a diagram. They add the image once inside Anki and it generates one card per hidden region.

Flag this whenever text-only cards clearly lose something important.

## Source is too thin

If the source is under ~200 words or just a list of trivia, say so honestly and ask whether the user has more material to combine, or wants cards on the small amount that is there.

## User asks for a specific number of cards

Honour it - but if the number is badly out of step with the source (5 cards for a whole chapter, or 100 for a one-page summary), say so and suggest a more sensible count.

## User wants only cloze, or only Q&A

Honour the preference. Cloze-only decks are common for vocabulary or list-heavy material.

## Exact spelling matters

See "Forcing exact spelling (type-in answers)" in references/formatting.md.
