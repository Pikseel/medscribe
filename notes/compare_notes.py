"""Rollü / rolsüz SOAP notlarını yan yana okumak için karşılaştırma (Kişi 3).

Girdi : notes/outputs/aci_00X_rollu.json, aci_00X_rolsuz.json, notes/data/aci_00X.json
Çıktı : notes/outputs/karsilastirma.md  (+ konsola özet)

Otomatik olarak üç şeyi işaretler (insan okumasının yerine geçmez, ona ön hazırlık):
  1. Olumsuzlama hatası: referans notta "denies / no / negative for" ile geçen bir
     bulgu, üretilen notta olumsuzlama olmadan geçiyorsa -> FLAG.
  2. Referansta olmayan bilgi: notta geçen ama referans notta hiç geçmeyen
     içerik kelimeleri (kaba sezgi, kelime örtüşmesi).
  3. Bölüm uzunlukları: S/O/A/P karakter sayıları, model boş bölüm bırakmış mı.
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
    """Kaba tekilleştirme: rashes->rash, findings->finding (tam stemmer değil)."""
    if w.endswith("es") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and len(w) > 3:
        return w[:-1]
    return w


def content_words(text):
    return {stem(w) for w in words(text) if len(w) > 2 and w not in STOP}


def negated_phrases(reference):
    """Referans nottaki 'Denies X', 'No X', 'Negative for X' ifadelerindeki X'ler."""
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
    """Referansta olumsuzlanan bulgu, üretilende düz olumlu geçiyor mu?"""
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
    """Üretilende olup referansta hiç geçmeyen içerik kelimeleri."""
    return sorted(content_words(generated) - content_words(reference))


def render_one(did, ref, rollu, rolsuz):
    lines = [f"## {did}", ""]
    lines.append(f"**Referans not** ({len(ref)} karakter)")
    lines.append("")
    lines.append("```\n" + ref.strip() + "\n```")
    lines.append("")

    for name, note in (("Rollü (gold_role)", rollu), ("Rolsüz (None)", rolsuz)):
        lines.append(f"### {name} — model: `{note['model']}`")
        lines.append("")
        for sec in SECTIONS:
            body = note[sec].strip() or "(boş)"
            lines.append(f"**{sec}.** {body}")
            lines.append("")

        flags = check_negation(ref, " ".join(note[s] for s in SECTIONS))
        if flags:
            lines.append(f"**Olumsuzlama bayrakları: {len(flags)}**")
            for f in flags:
                lines.append(f"- referansta *\"{f['cue']} {f['reference_phrase']}\"* "
                             f"→ notta: _{f['sentence']}_")
            lines.append("")
        else:
            lines.append("Olumsuzlama bayrağı yok.")
            lines.append("")

        extra = novelty(ref, " ".join(note[s] for s in SECTIONS))
        if extra:
            lines.append(f"Referansta geçmeyen kelimeler ({len(extra)}): "
                         + ", ".join(extra[:20]))
            lines.append("")
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    chunks = ["# Rollü / rolsüz SOAP notu karşılaştırması", ""]
    summary = []

    for did in DIDS:
        path = lambda c: os.path.join(OUT, f"{did}_{c}.json")  # noqa: E731
        if not (os.path.exists(path("rollu")) and os.path.exists(path("rolsuz"))):
            print(f"{did}: notlar eksik, atlandı")
            continue
        ref = load(os.path.join(DATA, f"{did}.json"))["reference_note"] or ""
        rollu, rolsuz = load(path("rollu")), load(path("rolsuz"))
        chunks.append(render_one(did, ref, rollu, rolsuz))

        f_rollu = check_negation(ref, " ".join(rollu[s] for s in SECTIONS))
        f_rolsuz = check_negation(ref, " ".join(rolsuz[s] for s in SECTIONS))
        summary.append((did, len(f_rollu), len(f_rolsuz)))

    table = ["## Özet", "",
             "| Diyalog | Rollü olumsuzlama bayrağı | Rolsüz olumsuzlama bayrağı |",
             "|---|---|---|"]
    for did, a, b in summary:
        table.append(f"| {did} | {a} | {b} |")
    table.append("")
    chunks.insert(1, "\n".join(table))

    out = os.path.join(OUT, "karsilastirma.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(chunks))
    print("\n".join(table))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
