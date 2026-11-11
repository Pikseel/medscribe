"""Frozen-test evaluation of speaker role assignment (Person 4, mid-project rubric).

Splits are ACI-Bench's own (CC BY 4.0), never mixed:
    train = challenge_data/train.csv                    (67 encounters)
    dev   = challenge_data/valid.csv                    (20)
    test  = challenge_data/clinicalnlp_taskB_test1.csv  (40)   <- frozen, evaluated once
[patient_guest] lines are dropped (plan rule: third persons are removed).

Systems (speaker level: one decision per encounter -> both speakers labelled):
    first_speaker   : whoever speaks first is the doctor
    you_ratio       : speaker with the higher rate of "you/your" is the doctor
    tfidf_lr        : Person 2's pipeline (roles/train_roles.build_pipeline), trained on train
Ablation: an utterance-level TF-IDF+LR (each line classified alone). Reported twice:
    utterance_tfidf_lr            : utterance accuracy (different unit, not comparable to the above)
    utterance_model_speaker_mean  : its P(Doctor) averaged per speaker -> speaker-level accuracy
Its test errors -> error analysis. dev is only measured (no model selection uses it).

Spread: 95% percentile bootstrap over encounters (2,000 resamples, seed 0); for utterance
accuracy whole encounters are resampled (cluster bootstrap).

    python -m eval.role_eval        (writes results/kisi4_role_eval.json, kisi4_utterance_errors.csv)
"""
import csv
import json
import random
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from roles.train_roles import build_pipeline  # noqa: E402

RAW = ROOT / "eval" / "data"
BASE = "https://raw.githubusercontent.com/wyim/aci-bench/main/data/challenge_data/"
SPLITS = {"train": "train", "dev": "valid", "test": "clinicalnlp_taskB_test1"}
TAG = re.compile(r"^\[([^\]]+)\]\s*(.*)$")
YOU = re.compile(r"\b(you|your|you're|you've|yourself)\b")
SEED, N_BOOT = 0, 2000


def load(split):
    path = RAW / f"{SPLITS[split]}.csv"
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(BASE + path.name, path)
    encs = []
    for row in csv.DictReader(path.open(encoding="utf-8")):
        utts = []
        for line in row["dialogue"].splitlines():
            m = TAG.match(line.strip())
            if m and m.group(1).lower() in ("doctor", "patient") and m.group(2).strip():
                utts.append((m.group(1).capitalize(), m.group(2).strip()))
        encs.append({"id": row["encounter_id"], "utts": utts})
    return encs


def speaker_docs(enc):
    return {r: " ".join(t for rr, t in enc["utts"] if rr == r) for r in ("Doctor", "Patient")}


# --- speaker-level systems: return the role predicted for the true doctor's turns
def first_speaker(enc, _):
    return enc["utts"][0][0] == "Doctor"


def you_ratio(enc, _):
    rate = {}
    for r, doc in speaker_docs(enc).items():
        words = doc.split()
        rate[r] = len(YOU.findall(doc)) / max(len(words), 1)
    return rate["Doctor"] > rate["Patient"]


def tfidf_lr(enc, model):
    d = speaker_docs(enc)
    i = list(model.classes_).index("Doctor")
    p = model.predict_proba([d["Doctor"], d["Patient"]])[:, i]
    return p[0] > p[1]          # exactly one doctor: higher P(doctor) wins


def boot_ci(correct):
    """Percentile bootstrap over encounters. `correct` holds one 0/1 per encounter, or one
    list of 0/1 per encounter (utterance level: whole encounters are resampled, so the
    dependence between utterances of one conversation is kept)."""
    rng = random.Random(SEED)
    groups = [c if isinstance(c, list) else [c] for c in correct]
    n = len(groups)
    stats = []
    for _ in range(N_BOOT):
        sample = [groups[rng.randrange(n)] for _ in range(n)]
        stats.append(sum(map(sum, sample)) / sum(map(len, sample)))
    stats.sort()
    return stats[int(0.025 * N_BOOT)], stats[int(0.975 * N_BOOT) - 1]


def category(text, gold):
    w = text.split()
    low = text.lower()
    if len(w) <= 3:
        return "short backchannel (<=3 words)"
    if gold == "Patient" and ("?" in text or re.match(r"^(so|and|but)?\s*(what|how|should|can|do|is|will|would)\b", low)):
        return "patient asks a question"
    if gold == "Doctor" and re.search(r"\b(i|i'm|i've|my|me)\b", low) and not YOU.search(low):
        return "doctor speaks in first person (no 'you')"
    if gold == "Patient" and YOU.search(low):
        return "patient addresses the doctor ('you')"
    return "other / content overlap"


def main():
    data = {s: load(s) for s in SPLITS}
    counts = {s: {"encounters": len(e), "speakers": 2 * len(e),
                  "utterances": sum(len(x["utts"]) for x in e)} for s, e in data.items()}

    texts, labels = [], []
    for enc in data["train"]:
        for r, doc in speaker_docs(enc).items():
            texts.append(doc)
            labels.append(r)
    model = build_pipeline().fit(texts, labels)

    results = {}
    for name, fn in (("first_speaker", first_speaker), ("you_ratio", you_ratio), ("tfidf_lr", tfidf_lr)):
        results[name] = {}
        for split in ("dev", "test"):
            correct = [int(fn(e, model)) for e in data[split]]
            lo, hi = boot_ci(correct)
            results[name][split] = {"accuracy": sum(correct) / len(correct),
                                    "ci95": [lo, hi], "n_encounters": len(correct),
                                    "errors": [e["id"] for e, c in zip(data[split], correct) if not c]}

    # utterance level: each line alone (what aggregation fixes) -> error analysis on test
    ut_x = [t for e in data["train"] for _, t in e["utts"]]
    ut_y = [r for e in data["train"] for r, _ in e["utts"]]
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    clf = LogisticRegression(max_iter=2000, class_weight="balanced").fit(vec.fit_transform(ut_x), ut_y)
    ut, pooled = {}, {}
    rows = []
    doc_i = list(clf.classes_).index("Doctor")
    for split in ("dev", "test"):
        xs = [(e["id"], r, t) for e in data[split] for r, t in e["utts"]]
        pred = clf.predict(vec.transform([t for _, _, t in xs]))
        correct = [int(p == r) for (_, r, _), p in zip(xs, pred)]
        per_enc = {}
        for (eid, _, _), c in zip(xs, correct):
            per_enc.setdefault(eid, []).append(c)
        lo, hi = boot_ci(list(per_enc.values()))
        ut[split] = {"accuracy": sum(correct) / len(correct), "ci95": [lo, hi], "n_utterances": len(xs),
                     "unit": "utterance; encounter-cluster bootstrap"}
        # same per-utterance model, scores averaged per speaker -> speaker-level decision
        enc_ok = []
        for e in data[split]:
            p = clf.predict_proba(vec.transform([t for _, t in e["utts"]]))[:, doc_i]
            mean = {r: sum(pp for pp, (rr, _) in zip(p, e["utts"]) if rr == r) /
                       max(1, sum(rr == r for rr, _ in e["utts"])) for r in ("Doctor", "Patient")}
            enc_ok.append(int(mean["Doctor"] > mean["Patient"]))
        lo, hi = boot_ci(enc_ok)
        pooled[split] = {"accuracy": sum(enc_ok) / len(enc_ok), "ci95": [lo, hi], "n_encounters": len(enc_ok),
                         "errors": [e["id"] for e, c in zip(data[split], enc_ok) if not c]}
        if split == "test":
            for (eid, r, t), p in zip(xs, pred):
                if p != r:
                    rows.append({"encounter": eid, "gold": r, "pred": p, "words": len(t.split()),
                                 "category": category(t, r), "text": t})
    results["utterance_tfidf_lr"] = ut
    results["utterance_model_speaker_mean"] = pooled
    cats = Counter(r["category"] for r in rows)
    examples = {c: next(r["text"] for r in rows if r["category"] == c and len(r["text"]) < 90) if any(
        r["category"] == c and len(r["text"]) < 90 for r in rows) else next(r["text"] for r in rows if r["category"] == c)
        for c in cats}

    out = {"splits": {s: f"{SPLITS[s]}.csv" for s in SPLITS}, "counts": counts, "licence": "CC BY 4.0",
           "results": results, "seed": SEED, "bootstrap_resamples": N_BOOT,
           "utterance_errors_test": {"total": len(rows), "by_category": dict(cats.most_common()),
                                     "examples": examples}}
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results" / "kisi4_role_eval.json", "w"), indent=2, ensure_ascii=False)
    with open(ROOT / "results" / "kisi4_utterance_errors.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["encounter", "gold", "pred", "words", "category", "text"])
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({k: v for k, v in out.items() if k in ("counts",)}, indent=1))
    for n, r in results.items():
        print(n, {s: (round(v["accuracy"], 4), [round(x, 3) for x in v["ci95"]]) for s, v in r.items()})
    print(out["utterance_errors_test"]["by_category"])


if __name__ == "__main__":
    main()
