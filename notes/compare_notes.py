"""Side-by-side comparison of rollu / rolsuz SOAP notes (Person 3).

Input : notes/outputs/aci_00X_rollu.json, aci_00X_rolsuz.json, notes/data/aci_00X.json
Output: notes/outputs/comparison.md  (+ a summary on the console)

It reports objective, reproducible measurements, not quality judgements:
  - section lengths S/O/A/P, and empty sections
  - note size relative to the transcript (a note close to 1.0 is a transcript echo)
  - first-person sentences in S (the model copying the patient instead of summarising)
  - ASR artefacts ("i i", "gon na", "do n't") carried into the note

An earlier version tried to detect lost negation with keyword rules. It produced
false positives on phrases like "no pain with palpation of the abdomen" and missed
a real coordination error ("no joint pain, fever, weight loss"), so that heuristic
was removed. Negation is reviewed by hand in notes/findings.md.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "outputs")

DIDS = ["aci_001", "aci_002", "aci_003"]
SECTIONS = ["S", "O", "A", "P"]

# Utterance-level artefacts that survive from the transcript into the note.
ASR_MARKERS = re.compile(r"(?:\bi i\b|\bgon na\b|\bdo n't\b|\bwan na\b|\buh\b|\bum\b|n't\b)")

# Thresholds for the objective warning; deliberately blunt and stated in the report.
ECHO_RATIO = 0.50
FIRST_PERSON_LIMIT = 2


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def transcript_chars(dialogue):
    return sum(len(s["text"]) for s in dialogue["segments"])


def metrics(note, dialogue):
    body = " ".join(note[k] for k in SECTIONS)
    s_sents = sentences(note["S"])
    first_person = sum(1 for s in s_sents if re.match(r"(i|we)\b|i'", s.lower()))
    return {
        "chars": len(body),
        "ratio": len(body) / max(transcript_chars(dialogue), 1),
        "s_sentences": len(s_sents),
        "first_person": first_person,
        "asr_markers": len(ASR_MARKERS.findall(body)),
        "empty": [k for k in SECTIONS if not note[k].strip()],
    }


def echo_warning(m):
    """Blunt flags for a note that copies the transcript instead of summarising."""
    out = []
    if m["ratio"] >= ECHO_RATIO:
        out.append(f"note is {m['ratio']:.0%} of the transcript")
    if m["first_person"] >= FIRST_PERSON_LIMIT:
        out.append(f"{m['first_person']}/{m['s_sentences']} S sentences in first person")
    if m["asr_markers"] >= 3:
        out.append(f"{m['asr_markers']} ASR artefacts carried over")
    return out


def render_one(did, ref, notes, metrics_by_cond):
    lines = [f"## {did}", ""]
    lines.append(f"**Reference note** ({len(ref)} chars)")
    lines.append("")
    lines.append("```\n" + ref.strip() + "\n```")
    lines.append("")

    for cond, label in (("rollu", "With roles (gold_role)"),
                        ("rolsuz", "Without roles (None)")):
        note, m = notes[cond], metrics_by_cond[cond]
        lines.append(f"### {label} — model: `{note['model']}`")
        lines.append("")
        lines.append(f"{m['chars']} chars · {m['ratio']:.0%} of transcript · "
                     f"S first person {m['first_person']}/{m['s_sentences']} · "
                     f"ASR artefacts {m['asr_markers']}")
        lines.append("")
        warnings = echo_warning(m)
        if warnings:
            lines.append("**Transcript echo warning:** " + "; ".join(warnings))
            lines.append("")
        if m["empty"]:
            lines.append(f"**Empty sections:** {', '.join(m['empty'])}")
            lines.append("")
        for sec in SECTIONS:
            body = note[sec].strip() or "(empty)"
            lines.append(f"**{sec}.** {body}")
            lines.append("")
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    chunks = ["# Rollu / rolsuz SOAP note comparison", "",
              "Objective measurements only. Negation and content errors are reviewed "
              "by hand in `notes/findings.md`.", ""]
    rows, details = [], []

    for did in DIDS:
        paths = {c: os.path.join(OUT, f"{did}_{c}.json") for c in ("rollu", "rolsuz")}
        if not all(os.path.exists(p) for p in paths.values()):
            print(f"{did}: notes missing, skipped")
            continue
        dialogue = load(os.path.join(DATA, f"{did}.json"))
        notes = {c: load(p) for c, p in paths.items()}
        m = {c: metrics(notes[c], dialogue) for c in notes}
        details.append(render_one(did, dialogue["reference_note"] or "", notes, m))

        for cond in ("rollu", "rolsuz"):
            rows.append((did, cond, m[cond]["chars"], m[cond]["ratio"],
                         m[cond]["first_person"], m[cond]["asr_markers"],
                         len(echo_warning(m[cond]))))

    table = ["## Summary", "",
             "| Dialogue | Condition | Chars | Note/transcript | S first person | ASR artefacts | Echo warnings |",
             "|---|---|---|---|---|---|---|"]
    for did, cond, chars, ratio, fp, asr, warn in rows:
        table.append(f"| {did} | {cond} | {chars} | {ratio:.0%} | {fp} | {asr} | {warn} |")
    table += ["", f"Echo warning when note/transcript >= {ECHO_RATIO:.0%}, "
                  f"S first person >= {FIRST_PERSON_LIMIT}, or >= 3 ASR artefacts."]

    chunks.insert(3, "\n".join(table))
    out = os.path.join(OUT, "comparison.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n\n".join(chunks + details))
    print("\n".join(table))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
