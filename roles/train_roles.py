"""Train the Person 2 doctor/patient role classifier on ACI-Bench.

The classifier deliberately does not use speaker names such as ``A`` or
``SPEAKER_00``.  All turns belonging to one speaker in an encounter are
joined, then classified from their language.  The train/test split is made by
encounter so turns from the same consultation cannot leak into both sets.

Usage from the repository root::

    roles/.venv/bin/python -m roles.train_roles
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import ssl
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

import joblib
import certifi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, cross_validate
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CSV_URL = (
    "https://raw.githubusercontent.com/wyim/aci-bench/"
    "main/data/challenge_data/train.csv"
)
DEFAULT_CSV = HERE / "data" / "_raw" / "train.csv"
DEFAULT_MODEL = HERE / "models" / "role_classifier.joblib"
DEFAULT_METRICS = ROOT / "results" / "kisi2_role_metrics.json"
TAG = re.compile(r"^\[(?P<tag>[^\]]+)\]\s*(?P<text>.*)$")
LABELS = ("Doctor", "Patient")


def fetch_csv(path: Path = DEFAULT_CSV) -> Path:
    """Download ACI-Bench's training CSV once and return its local path."""
    path = Path(path)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"ACI-Bench indiriliyor: {CSV_URL}")
    # Python.org macOS installations may not inherit the Keychain CA store.
    # certifi keeps TLS verification enabled instead of using an unsafe
    # unverified SSL context.
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(CSV_URL, context=context) as response:
        with path.open("wb") as output:
            shutil.copyfileobj(response, output)
    return path


def _speakers_from_dialogue(dialogue: str) -> dict[str, list[str]]:
    turns: dict[str, list[str]] = defaultdict(list)
    for raw_line in dialogue.splitlines():
        match = TAG.match(raw_line.strip())
        if not match:
            continue
        tag = match.group("tag").strip().lower()
        text = match.group("text").strip()
        if tag in ("doctor", "patient") and text:
            turns[tag].append(text)
    return turns


def load_samples(csv_path: Path) -> tuple[list[str], list[str], list[str]]:
    """Return speaker documents, labels and encounter groups from ACI-Bench."""
    texts: list[str] = []
    labels: list[str] = []
    groups: list[str] = []
    with Path(csv_path).open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            encounter_id = row["encounter_id"]
            turns = _speakers_from_dialogue(row["dialogue"])
            for source_tag, label in (("doctor", "Doctor"), ("patient", "Patient")):
                if turns[source_tag]:
                    texts.append(" ".join(turns[source_tag]))
                    labels.append(label)
                    groups.append(encounter_id)
    if len(set(labels)) != 2:
        raise ValueError("Eğitim verisinde hem Doctor hem Patient örnekleri bulunmalı")
    return texts, labels, groups


def build_pipeline() -> Pipeline:
    """TF-IDF word/character features plus a balanced logistic classifier."""
    features = FeatureUnion(
        [
            (
                "word",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=30_000,
                    sublinear_tf=True,
                    strip_accents="unicode",
                ),
            ),
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    max_features=50_000,
                    sublinear_tf=True,
                ),
            ),
        ]
    )
    classifier = LogisticRegression(
        class_weight="balanced",
        max_iter=2_000,
        random_state=42,
    )
    return Pipeline([("features", features), ("classifier", classifier)])


def train_and_evaluate(
    csv_path: Path = DEFAULT_CSV,
    model_path: Path = DEFAULT_MODEL,
    metrics_path: Path = DEFAULT_METRICS,
) -> dict:
    texts, labels, groups = load_samples(csv_path)

    # Grouped cross-validation gives a less split-dependent estimate than one
    # small holdout. Every encounter stays entirely inside a single fold.
    cross_validation = cross_validate(
        build_pipeline(),
        texts,
        labels,
        groups=groups,
        cv=GroupKFold(n_splits=5),
        scoring={"accuracy": "accuracy", "macro_f1": "f1_macro"},
    )
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(splitter.split(texts, labels, groups=groups))

    x_train = [texts[i] for i in train_idx]
    y_train = [labels[i] for i in train_idx]
    x_test = [texts[i] for i in test_idx]
    y_test = [labels[i] for i in test_idx]

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    metrics = {
        "group_5fold": {
            "accuracy_scores": cross_validation["test_accuracy"].tolist(),
            "accuracy_mean": float(mean(cross_validation["test_accuracy"])),
            "accuracy_std": float(pstdev(cross_validation["test_accuracy"])),
            "macro_f1_scores": cross_validation["test_macro_f1"].tolist(),
            "macro_f1_mean": float(mean(cross_validation["test_macro_f1"])),
            "macro_f1_std": float(pstdev(cross_validation["test_macro_f1"])),
        },
        "holdout": {
            "accuracy": float(accuracy_score(y_test, predictions)),
            "macro_f1": float(f1_score(y_test, predictions, average="macro")),
            "confusion_matrix_labels": list(LABELS),
            "confusion_matrix": confusion_matrix(
                y_test, predictions, labels=list(LABELS)
            ).tolist(),
            "classification_report": classification_report(
                y_test,
                predictions,
                labels=list(LABELS),
                output_dict=True,
                zero_division=0,
            ),
            "train_speakers": len(train_idx),
            "test_speakers": len(test_idx),
            "train_encounters": len({groups[i] for i in train_idx}),
            "test_encounters": len({groups[i] for i in test_idx}),
        },
        "evaluation_unit": "one aggregated document per speaker",
        "split_unit": "encounter_id",
    }

    # Refit on all labelled encounters after honest held-out evaluation.
    pipeline.fit(texts, labels)
    bundle = {
        "model": pipeline,
        "labels": list(LABELS),
        "positive_probability": "Doctor",
        "aggregation": "all utterances per speaker",
        "dataset_url": CSV_URL,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)

    metrics_path = Path(metrics_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    args = parser.parse_args()

    csv_path = fetch_csv(args.csv)
    metrics = train_and_evaluate(csv_path, args.model, args.metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"\nModel kaydedildi: {args.model}")


if __name__ == "__main__":
    main()
