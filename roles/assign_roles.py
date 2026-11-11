"""Assign Doctor/Patient roles to every speaker in a shared dialogue JSON.

``role_prob`` is the model's probability that the speaker is the Doctor.  All
segments from one speaker receive the same role and probability.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_MODEL = HERE / "models" / "role_classifier.joblib"
MODEL_ENV = "MEDSCRIBE_ROLE_MODEL"
_BUNDLE_CACHE: dict[Path, dict[str, Any]] = {}


def _load_bundle(model_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    path = Path(model_path or os.environ.get(MODEL_ENV, DEFAULT_MODEL)).resolve()
    if path in _BUNDLE_CACHE:
        return _BUNDLE_CACHE[path]
    if not path.exists():
        raise FileNotFoundError(
            f"Rol modeli bulunamadı: {path}. Önce "
            "'roles/.venv/bin/python -m roles.train_roles' komutunu çalıştırın."
        )
    try:
        import joblib
    except ImportError as exc:
        raise ImportError(
            "joblib kurulu değil. 'roles/.venv/bin/pip install -r "
            "roles/requirements.txt' komutunu çalıştırın."
        ) from exc
    bundle = joblib.load(path)
    if "model" not in bundle:
        raise ValueError(f"Geçersiz rol modeli paketi: {path}")
    _BUNDLE_CACHE[path] = bundle
    return bundle


def _doctor_probabilities(model: Any, documents: list[str]) -> list[float]:
    classes = list(model.classes_)
    if "Doctor" not in classes:
        raise ValueError("Model sınıfları arasında 'Doctor' yok")
    doctor_index = classes.index("Doctor")
    return [float(row[doctor_index]) for row in model.predict_proba(documents)]


def _pairwise_probabilities(raw: list[float]) -> list[float]:
    """For two-speaker dialogue, enforce exactly one Doctor using model odds."""
    if len(raw) != 2:
        return raw
    epsilon = 1e-9
    odds = [
        max(epsilon, min(1 - epsilon, p))
        / (1 - max(epsilon, min(1 - epsilon, p)))
        for p in raw
    ]
    total = odds[0] + odds[1]
    return [odds[0] / total, odds[1] / total]


def assign_roles(dialogue: dict, model_path: str | os.PathLike[str] | None = None) -> dict:
    """Mutate and return ``dialogue`` with role and Doctor probability fields."""
    segments = dialogue.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError("dialogue['segments'] boş olmayan bir liste olmalı")

    speaker_texts: dict[str, list[str]] = defaultdict(list)
    for index, segment in enumerate(segments):
        speaker = segment.get("speaker")
        text = segment.get("text")
        if not isinstance(speaker, str) or not speaker.strip():
            raise ValueError(f"Cümle {index}: speaker boş olamaz")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Cümle {index}: text boş olamaz")
        speaker_texts[speaker].append(text.strip())

    speakers = list(speaker_texts)
    documents = [" ".join(speaker_texts[speaker]) for speaker in speakers]
    bundle = _load_bundle(model_path)
    probabilities = _doctor_probabilities(bundle["model"], documents)
    probabilities = _pairwise_probabilities(probabilities)

    # In a two-speaker clinical dialogue, the pairwise transform makes the
    # probabilities complementary and therefore guarantees one of each role.
    by_speaker = dict(zip(speakers, probabilities))
    for segment in segments:
        probability = by_speaker[segment["speaker"]]
        segment["role"] = "Doctor" if probability >= 0.5 else "Patient"
        segment["role_prob"] = round(probability, 6)
    return dialogue


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ortak JSON dosyasına Doctor/Patient rolleri ekler."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--model", type=Path)
    args = parser.parse_args()

    dialogue = json.loads(args.input.read_text(encoding="utf-8"))
    result = assign_roles(dialogue, args.model)
    output = args.output or args.input.with_name(f"{args.input.stem}_roles.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Kaydedildi: {output}")


if __name__ == "__main__":
    main()
