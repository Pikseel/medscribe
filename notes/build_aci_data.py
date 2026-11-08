"""ACI-Bench -> shared JSON format converter (Person 3).

Source: https://github.com/wyim/aci-bench  data/challenge_data/train.csv
Columns: dataset, encounter_id, dialogue, note

Conversion rules (project plan 2.3):
  [doctor]  -> speaker "A", gold_role "Doctor"
  [patient] -> speaker "B", gold_role "Patient"
  note      -> reference_note
  start/end -> null (text data), role/role_prob -> null (filled in by Person 2)

Untagged lines (transcript artefacts) are treated as a continuation of the
previous utterance and appended to it; if they come first they are dropped.
Third parties are not tagged in the source, so no extra filter is needed.

The raw CSV lives under `_raw/` and is not committed (.gitignore); it is
downloaded when missing. The three generated JSON files are committed.

Usage:
  python -m notes.build_aci_data            # generates the three selected dialogues
"""

import csv
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from common.format import save  # noqa: E402

CSV_URL = "https://raw.githubusercontent.com/wyim/aci-bench/main/data/challenge_data/train.csv"
CSV_PATH = os.path.join(HERE, "data", "_raw", "train.csv")
OUT_DIR = os.path.join(HERE, "data")

# Three dialogues selected for the experiment: short (25-26 utterances) so they
# fit the prompt comfortably, and all three contain negation ("no"/"denies"),
# which is what the rollu/rolsuz comparison needs. D2N053 is the richest case:
# its reference note says "Denies any rashes" and the patient says "no, not really".
DIALOGUES = [
    ("D2N050", "aci_001"),  # kidney stones
    ("D2N053", "aci_002"),  # itchy scalp (plenty of negation)
    ("D2N060", "aci_003"),  # left foot pain
]

TAG = re.compile(r"^\[(?P<tag>[^\]]+)\]\s*(?P<text>.*)$")
ROLE_OF_TAG = {"doctor": ("A", "Doctor"), "patient": ("B", "Patient")}


def convert(encounter_id, dialogue_id, dialogue_text, note_text, source="aci-bench"):
    segments = []
    for raw in dialogue_text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        m = TAG.match(line)
        if not m:
            # Untagged line: continuation of the previous utterance
            if segments and segments[-1]["text"]:
                segments[-1]["text"] = f"{segments[-1]['text']} {line}".strip()
            continue
        tag = m.group("tag").strip().lower()
        if tag not in ROLE_OF_TAG:  # third party -> drop
            continue
        text = m.group("text").strip()
        if not text:
            continue
        speaker, gold_role = ROLE_OF_TAG[tag]
        segments.append({
            "id": len(segments),
            "start": None,
            "end": None,
            "speaker": speaker,
            "gold_role": gold_role,
            "role": None,
            "role_prob": None,
            "text": text,
        })

    return {
        "dialogue_id": dialogue_id,
        "source": source,
        "reference_note": note_text,
        "segments": segments,
    }


def fetch_csv(path=CSV_PATH):
    """Download the raw ACI-Bench CSV if it is missing (611 KB, one-off)."""
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"downloading: {CSV_URL}")
    urllib.request.urlretrieve(CSV_URL, path)
    return path


def main():
    rows = {r["encounter_id"]: r
            for r in csv.DictReader(open(fetch_csv(), encoding="utf-8"))}
    os.makedirs(OUT_DIR, exist_ok=True)

    for encounter_id, dialogue_id in DIALOGUES:
        row = rows[encounter_id]
        d = convert(encounter_id, dialogue_id, row["dialogue"], row["note"])
        path = os.path.join(OUT_DIR, f"{dialogue_id}.json")
        save(d, path)          # common.format.save -> check_format + json.dump
        n_doc = sum(s["gold_role"] == "Doctor" for s in d["segments"])
        print(
            f"{path}: {len(d['segments'])} utterances "
            f"({n_doc} doctor / {len(d['segments']) - n_doc} patient), "
            f"note {len(d['reference_note'])} chars, check_format OK"
        )


if __name__ == "__main__":
    main()
