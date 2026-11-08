"""Side-by-side comparison of rollu / rolsuz SOAP notes (Person 3).

Input : notes/outputs/aci_00X_rollu.json, aci_00X_rolsuz.json, notes/data/aci_00X.json
Output: notes/outputs/comparison.md  (+ a summary on the console)

It flags three things automatically. This prepares the human reading, it does
not replace it:
  1. Negation error: a finding that the reference note records as denied
     ("denies / no / negative for") appears in the generated note without a
     negation cue -> FLAG.
  2. Information not in the reference: content words that appear in the note
     but never in the reference note (rough lexical check).
  3. Section lengths: S/O/A/P character counts, so an empty section is visible.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "outputs")

DIDS = ["aci_001", "aci_002", "aci_003"]
SECTIONS = ["S", "O", "A", "P"]

NEG_CUES = ("denies", "denied", "no ", "not ", "negative for", "without", "none",
            "never", "unremarkable")
STOP = set("""a an the and or of to in on at for with is are was were be been being
patient patients reports report denies denied no not negative for without none never
he she his her their them they it this that these those has have had has has
mild moderate severe left right bilateral also well year old years ago today
""".split())


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def words(text):
    return re.findall(r"[a-z']+", text.lower())


def stem(w):
    """Crude singularisation: rashes->rash, findings->finding (not a real stemmer)."""
    if w.endswith("es") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and len(w) > 3:
        return w[:-1]
    return w


def content_words(text):
    return {stem(w) for w in words(text) if len(w) > 2 and w not in STOP}


def negated_phrases(reference):
    """The X in 'Denies X', 'No X', 'Negative for X' from the reference note."""
    out = []
    for m in re.finditer(
            r"(denies|denied|negative for|no|without)\s+([^.;\n]{3,80})", reference, re.I):
        cue, phrase = m.group(1).lower(), m.group(2).strip()
        phrase = re.split(r",|\band\b", phrase)[0].strip()
        out.append((cue, phrase))
    return out


def is_negated_sentence(sentence):
    s = sentence.lower()
    return any(cue in s for cue in NEG_CUES)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def check_negation(reference, generated):
    """Does a finding denied in the reference appear as plain positive in the output?"""
    flags = []
    for cue, phrase in negated_phrases(reference):
        keys = content_words(phrase) - {"any"}
        if not keys:
            continue
        for sent in sentences(generated):
            sw = {stem(w) for w in words(sent)}
            if keys & sw and not is_negated_sentence(sent):
                flags.append({"cue": cue, "reference_phrase": phrase, "sentence": sent})
                break
    return flags


def novelty(reference, generated):
    """Content words present in the output but absent from the reference."""
    return sorted(content_words(generated) - content_words(reference))


def render_one(did, ref, rollu, rolsuz):
    lines = [f"## {did}", ""]
    lines.append(f"**Reference note** ({len(ref)} chars)")
    lines.append("")
    lines.append("```\n" + ref.strip() + "\n```")
    lines.append("")

    for name, note in (("With roles (gold_role)", rollu), ("Without roles (None)", rolsuz)):
        lines.append(f"### {name} — model: `{note['model']}`")
        lines.append("")
        for sec in SECTIONS:
            body = note[sec].strip() or "(empty)"
            lines.append(f"**{sec}.** {body}")
            lines.append("")

        flags = check_negation(ref, " ".join(note[s] for s in SECTIONS))
        if flags:
            lines.append(f"**Negation flags: {len(flags)}**")
            for f in flags:
                lines.append(f"- reference has *\"{f['cue']} {f['reference_phrase']}\"* "
                             f"→ note says: _{f['sentence']}_")
            lines.append("")
        else:
            lines.append("No negation flags.")
            lines.append("")

        extra = novelty(ref, " ".join(note[s] for s in SECTIONS))
        if extra:
            lines.append(f"Words absent from the reference ({len(extra)}): "
                         + ", ".join(extra[:20]))
            lines.append("")
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    chunks = ["# Rollu / rolsuz SOAP note comparison", ""]
    summary = []

    for did in DIDS:
        path = lambda c: os.path.join(OUT, f"{did}_{c}.json")  # noqa: E731
        if not (os.path.exists(path("rollu")) and os.path.exists(path("rolsuz"))):
            print(f"{did}: notes missing, skipped")
            continue
        ref = load(os.path.join(DATA, f"{did}.json"))["reference_note"] or ""
        rollu, rolsuz = load(path("rollu")), load(path("rolsuz"))
        chunks.append(render_one(did, ref, rollu, rolsuz))

        f_rollu = check_negation(ref, " ".join(rollu[s] for s in SECTIONS))
        f_rolsuz = check_negation(ref, " ".join(rolsuz[s] for s in SECTIONS))
        summary.append((did, len(f_rollu), len(f_rolsuz)))

    table = ["## Summary", "",
             "| Dialogue | Rollu negation flags | Rolsuz negation flags |",
             "|---|---|---|"]
    for did, a, b in summary:
        table.append(f"| {did} | {a} | {b} |")
    table.append("")
    chunks.insert(1, "\n".join(table))

    out = os.path.join(OUT, "comparison.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(chunks))
    print("\n".join(table))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
