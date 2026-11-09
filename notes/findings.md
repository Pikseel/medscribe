# Findings — manual review of the six notes

Model: `Qwen/Qwen2.5-7B-Instruct` (4-bit), frozen `istem_v1.txt`, temperature 0, single run.
Inputs: `notes/data/aci_001..003.json`. Outputs: `notes/outputs/*_rollu.json`, `*_rolsuz.json`.
Read side by side against the reference note and the transcript.

Short version: **role labels did not uniformly help.** They clearly helped on `aci_002`
(negation scope) and clearly hurt on `aci_003`, where the labelled transcript made the model
echo the conversation instead of summarising it.

## 1. Headline — with roles, the longest note became a transcript echo

`aci_003` (left foot / Lisfranc), 4,998-character transcript:

| | chars | note/transcript | S first person | ASR artefacts |
|---|---|---|---|---|
| rollu | 3,229 | 65% | 7 of 9 | 7 |
| rolsuz | 1,329 | 27% | 0 of 4 | 0 |

The rollu note opens `S. i'm doing alright aside from this foot pain that i have.` and keeps
`gon na`, `i i mean`, `do n't`. The Assessment section is the doctor's explanation copied
verbatim, including `you will not be able to use that left foot`.

The rolsuz note on the same dialogue is a proper third-person summary.

Interpretation: with `Doctor:` / `Patient:` prefixes the model treats the input as a dialogue
to continue, not a transcript to summarise. The prompt never says "third person, do not copy
utterances" — that is the gap.

## 2. Negation — one real error, and it is the rolsuz note

`aci_002`, S section:

- rollu: `... no joint pain, no fever, no weight loss, no rashes elsewhere ...`
- rolsuz: `... no rashes elsewhere, no joint pain, fever, weight loss, no new stressors ...`

In the rolsuz note the negation covers only `joint pain`, so `fever` and `weight loss` read as
present. This is the failure mode the plan predicted, and it is the strongest argument for
role labels on short dialogues.

Note: this is invisible to keyword screening, because the sentence does contain "no". That is
why the comparison script reports measurements and this file carries the reading.

Same dialogue, rolsuz also contradicts itself: `sister has dry scalp, no significant family
history of similar symptoms`, where rollu says `family history of similar symptoms in sister`.

## 3. Shared errors — present with and without roles

- **Number.** The doctor says `blood pressure was one eighteen over seventy two`. Both notes
  turn that into 180/72 (rollu even writes `one eighty one over seventy two`). The reference
  is 118/72.
- **Added fact.** `aci_001`: both notes put "pushing fluids" / "fluid intake" into the
  assessment. Neither the transcript nor the reference plan mentions it — a hydration prior.
- **Section bleeding.** `aci_001` rollu and `aci_002` rolsuz put plan items inside
  Assessment (`A. ... Plan includes oxycodone ...`). `aci_002` rollu's Assessment is just
  `scalp psoriasis`, correctly placed.

## 4. Not model errors — source ambiguity to state carefully

- **Laterality.** The patient says `she ended up falling directly onto my right foot`; the
  doctor says `hurt your left foot`, and the exam, X-ray and reference note are all left.
  Both notes carry "right foot" somewhere. The note is faithful to the patient's wording and
  wrong clinically, so this is a reconciliation failure, not a hallucination.
- **Pain vs ibuprofen.** The transcript says `without ibuprofen ... my pain is a three` and
  `with your ibuprofen ... like a seven eight`, which is clinically odd. The reference note
  normalises it to 3/10 with medication and 7-8/10 without. Both notes follow the transcript.
  Do not report this as a model error; report it as transcript/reference disagreement.

## 5. What this means for the slide

One sentence, defensible on three dialogues:

> Role labels fixed negation scope on a short dialogue, but on the longest one they pushed the
> model into echoing the transcript (3.2k vs 1.3k characters), so the effect of the labels is
> conditional on dialogue length — and the prompt needs an explicit summarisation rule.

## Caveats

- n = 3 dialogues, one model, one prompt, one greedy run. Directional, not significant.
- The reference notes are clinician-written and much longer than the model output; they are a
  reading aid, not a same-style gold standard.
- Transcript errors (BP, laterality, medication order) propagate into the notes; three of the
  apparent "model errors" above are inherited.
