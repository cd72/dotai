# Testing the anki-flashcard-creator skill

This folder is the skill's test harness. Its job is to make "remember to test
after a change" into "run a couple of commands." If you edit the skill, start here.

## Two layers of correctness

1. **Structural / mechanical** - does the deck import into Anki cleanly?
   (Right headers, column counts, escaping, no em dashes, valid cloze syntax.)
   This is deterministic and is checked by `validate.py`. It is the
   regression-prone layer - a format edit can silently break it.

2. **Card quality / judgement** - did the skill atomise well, choose cloze vs
   Q&A sensibly, reach for reversed cards, escape angle brackets, etc.?
   This depends on the model running the skill, so it can't be a pure script.
   You check it by running a prompt and reading the output. `validate.py`
   does NOT check this - a deck can pass every structural check and still be
   full of bad cards.

## What to run after a change (decision table)

| You changed...                                              | Do this |
|-------------------------------------------------------------|---------|
| Pure wording / explanation, no output-format impact         | Nothing required. |
| Output format (headers, columns, escaping rule, cloze markup, a note type, a file) | Re-run the affected eval prompt(s), save the TSV, run `validate.py` on it. |
| A behaviour/heuristic (new card type, new cloze rule, when to split) | Run the eval whose `feature` matches, read the cards for quality, AND run `validate.py`. |
| Anything you're unsure about                                | Run all four evals and validate. It takes a few minutes. |

The eval prompts live in `evals.json`. Each has a `feature` field telling you
which behaviour it exercises, so you can pick the relevant one.

## How to run a structural check

`validate.py` takes a file or a whole directory and exits non-zero if anything
fails (so it can be wired into a pre-ship check later):

```bash
# check every .tsv the skill just produced
python evals/validate.py /mnt/user-data/outputs/

# or a single file
python evals/validate.py mydeck_cloze.tsv
```

It auto-detects the expected column count from each file's `#tags column:N`
header, so you don't pass it manually.

## How to run a full test (structural + quality)

On Claude.ai / in a chat session there are no background agents, so you run the
skill yourself:

1. Open `evals.json` and pick the eval(s) matching what you changed.
2. For each, feed the `prompt` to a session that has the skill, following the
   skill's instructions. (Eval 2 needs the file `samples/immune_system.txt`.)
3. Save the generated `.tsv` file(s).
4. Run `python evals/validate.py <those files>`.
5. Read the cards against the eval's `expected_output` and the card-writing
   rules in `SKILL.md` - this is the quality check the script can't do.

The most reliable version of step 2 is a **fresh** session (so the tester isn't
the same context that wrote the change). That's the gold standard; an inline
self-run is a weaker sanity check but still catches a lot.

## The evals at a glance

- **0 code-escaping** - stresses `&lt;`/`&gt;`/`&amp;` escaping on C++ generics.
- **1 vocab-reversed** - should produce a `Basic (and reversed card)` file.
- **2 mixed-source** - basic + cloze, atomicity, cloze Back Extra (needs `samples/immune_system.txt`).
- **3 overlapping-cloze** - sliding-window cloze for a long ordered sequence.

## What this harness does NOT do

- It does not prove the cards are *good*, only that the file imports.
- It does not test rendering inside Anki (MathJax, image occlusion, etc.) - for
  anything visual, import a sample deck into Anki and eyeball it.
