"""ACI-Bench -> ortak JSON formatı dönüştürücü (Kişi 3, 7 Kasım).

Kaynak: https://github.com/wyim/aci-bench  data/challenge_data/train.csv
Sütunlar: dataset, encounter_id, dialogue, note

Dönüşüm kuralları (Proje Planı 2.3):
  [doctor]  -> speaker "A", gold_role "Doctor"
  [patient] -> speaker "B", gold_role "Patient"
  note      -> reference_note
  start/end -> null (metin verisi), role/role_prob -> null (Kişi 2 doldurur)

Etiketsiz satırlar (transkript artefaktı) bir önceki cümlenin devamı sayılıp
ona eklenir; başta gelirse atılır. Üçüncü kişiler zaten etiketli değil, bu yüzden
ayrıca bir filtre gerekmiyor.

Ham CSV `_raw/` altında tutulur ve repoya girmez (.gitignore); yoksa indirilir.
Üretilen 3 JSON repoya girer.

Kullanım:
  python -m notes.build_aci_data            # seçili 3 diyaloğu üretir
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

# Deney için seçilen 3 diyalog: kısa (25-26 cümle), prompt'a sığar,
# üçünde de olumsuzlama ("no"/"denies") var -> rollü/rolsüz farkını göstermeye uygun.
# D2N053 özellikle zengin: referans notta "Denies fever or weight loss" geçiyor.
DIALOGUES = [
    ("D2N050", "aci_001"),  # kidney stones
    ("D2N053", "aci_002"),  # itchy scalp (olumsuzlama bol)
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
            # Etiketsiz satır: önceki cümlenin devamı
            if segments and segments[-1]["text"]:
                segments[-1]["text"] = f"{segments[-1]['text']} {line}".strip()
            continue
        tag = m.group("tag").strip().lower()
        if tag not in ROLE_OF_TAG:  # üçüncü kişi -> at
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
    """Ham ACI-Bench CSV'si yoksa indir (611 KB, tek seferlik)."""
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"indiriliyor: {CSV_URL}")
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
            f"{path}: {len(d['segments'])} cümle "
            f"({n_doc} doktor / {len(d['segments']) - n_doc} hasta), "
            f"not {len(d['reference_note'])} karakter, check_format OK"
        )


if __name__ == "__main__":
    main()
