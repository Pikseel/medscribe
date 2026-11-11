# notes/ — Person 3: SOAP notes and experiment

`generate_note(dialogue, role_field) -> note` — generates a SOAP note from a role-labelled
transcript with an LLM, and runs the first comparison that measures the effect of role
information on the note. Project plan section 3 (Person 3) and section 4 (calendar).

## Files

| File | What it does |
|---|---|
| `generate_note.py` | The deliverable function + CLI. Backend is automatic: transformers on GPU, otherwise Ollama |
| `istem_v1.txt` | **Frozen** prompt. Single source of truth; no copy in code |
| `data/aci_001..003.json` | 3 dialogues selected from ACI-Bench, in the shared format (`check_format` clean) |
| `build_aci_data.py` | CSV → JSON converter (downloads the raw CSV if missing) |
| `compare_notes.py` | Side-by-side rollu/rolsuz notes + objective metrics → `outputs/comparison.md` |
| `findings.md` | Manual review of the six notes: the errors, and which are inherited from the transcript |
| `colab_soap.ipynb` | Colab notebook that produces the 6 notes (clones the repo, T4) |
| `outputs/` | The 6 generated notes + the comparison report |

Slides: `notes/build_slides.py` (local `results/kisi3_slides.pptx`, not tracked). The final
deck (`app/build_deck.py`) reuses its note-generation slide.

## Usage (from the repository root)

```bash
python -m notes.generate_note --prompt-only --dialogue common/ornek_diyalog.json --role-field gold_role
python -m notes.generate_note --dialogue notes/data/aci_001.json --role-field gold_role
python -m notes.generate_note --experiment        # 3 dialogues x 2 conditions -> notes/outputs/
python -m notes.compare_notes                     # comparison report
```

`role_field`:
- `"role"` — roles predicted by Person 2 (demo)
- `"gold_role"` — gold roles ("rollu" condition)
- `None` — no speaker information ("rolsuz" condition)

## Experiment

3 dialogues × 2 conditions = **6 notes**. A note follows the format in plan section 2.3:

```json
{"dialogue_id": "aci_001", "condition": "rollu", "model": "Qwen/Qwen2.5-7B-Instruct",
 "S": "...", "O": "...", "A": "...", "P": "..."}
```

Selected dialogues (all 25–26 utterances, all containing negation):

| ID | ACI-Bench | Topic |
|---|---|---|
| `aci_001` | D2N050 | kidney stones |
| `aci_002` | D2N053 | itchy scalp — reference note says "Denies any rashes" |
| `aci_003` | D2N060 | left foot pain |

**Status: done.** All six notes were generated on Colab (T4) with `Qwen/Qwen2.5-7B-Instruct`
4-bit, temperature 0, frozen `istem_v1`. Results in `outputs/` and `findings.md`.

Headline: role labels are not uniformly better. On the longest dialogue (`aci_003`) the labelled
transcript made the model echo the conversation (3,229 chars, 65% of the transcript, 7 of 9 S
sentences in first person); without labels it summarised (1,329 chars). On `aci_002` the labels
did help: the rolsuz note scoped "no" over one item only, so fever and weight loss read as
present. Shared errors: 118/72 became 180/72 in both, and both added "push fluids" that nobody
said. See `findings.md` for the quote-level review.

### Reproducing on Colab

1. Upload `notes/colab_soap.ipynb` to Colab.
2. **Runtime → T4 GPU**.
3. Run the cells in order (the notebook clones the repo itself).
4. Cell 6 generates the example dialogue — **checkpoint**: if the chest pain that the patient
   denied comes out as present, the prompt is too weak; do not continue without `istem_v2.txt`.
5. Cell 7 produces the six notes, cell 8 the comparison. Commit `notes/outputs/`.

### If a note fails

`generate_note` retries once with a larger token budget and a shorter-output instruction.
If the error says `Unterminated string`, the reply was cut off by the token cap — that is what
happened on `aci_003` with a 700-token budget, so `MAX_NEW_TOKENS` is now 1500. Cell 7 is
resumable: notes already on disk are skipped, only failures are retried. Set
`SKIP_EXISTING = False` to regenerate everything.

## Prompt freeze rule

`istem_v1.txt` does not change once the experiment has started. If a change is needed, open
`istem_v2.txt` and regenerate all 6 notes; notes from two versions are never mixed in the same
table. `temperature = 0`.

The results suggest one concrete v2 rule: summarise in the third person and never copy
utterances verbatim. That is the fix for the `aci_003` echo; it must be applied to all six
dialogues, not just the failing one.

## Demo integration (Person 4)

```python
from notes.generate_note import generate_note   # app/pipeline.py already imports it this way
note = generate_note(dialogue, "role")
```

- The backend is chosen automatically: `transformers` on Colab/T4, Ollama otherwise.
  Force it with `SOAP_BACKEND=transformers` or `gn.set_backend("transformers")`.
- If the `role` field is empty, that utterance is written without a label — the model does
  not crash, so the demo never waits for Person 2.
- The model is loaded only on the first note request (`_load_hf`), never at import time.
- When no model is available the error message says what to do (`ollama pull ...` / Colab).

## Notes

- The raw ACI-Bench CSV lives under `data/_raw/` and is not committed (`.gitignore`);
  `build_aci_data.py` downloads it when missing. The three generated JSON files are committed.
- In `data/*.json`, `start/end`, `role` and `role_prob` are `null`; Person 2 fills those in.
- `aci_002` has a 1154-character reference note, `aci_003` has 3008 — if we move on to
  ROUGE/BERTScore, that length difference needs to be taken into account.
