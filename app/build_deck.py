"""MedScribe interim presentation (12 Nov) — full merged deck.

Uses the style helpers and slides 7-8 from notes/build_slides.py (Person 3), so the
whole deck looks the same. Slides 5 and 6 are drafts from asr/ and roles/ results;
their owners should check the numbers and speaker notes.

    python -m app.build_deck      ->  results/medscribe_interim.pptx
"""
import json
import os

from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from notes.build_slides import (INK, TEAL, TEAL2, MINT, MUTED, BG, WHITE, SOFT,
                                TITLE_FONT, BODY_FONT, rect, textbox, para,
                                slide_notes_generation, slide_experiment)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = "Courier New"


def base(prs, kicker, title):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=BG)
    rect(s, 0, 0, 0.13, 7.5, fill=TEAL)
    tb = textbox(s, 0.55, 0.42, 9.0, 0.3)
    para(tb.text_frame, True, [(kicker, BODY_FONT, 11, True, TEAL)])
    tb = textbox(s, 0.55, 0.72, 12.0, 0.8)
    para(tb.text_frame, True, [(title, TITLE_FONT, 32, True, INK)])
    return s


def card(s, x, y, w, h, accent=None):
    rect(s, x, y, w, h, fill=WHITE, line=SOFT, radius=0.05, line_w=1.25)
    if accent is not None:
        rect(s, x, y, 0.05, h, fill=accent)


def label(s, x, y, w, text, color=TEAL2):
    tb = textbox(s, x, y, w, 0.3)
    para(tb.text_frame, True, [(text, BODY_FONT, 10.5, True, color)])


def lines(s, x, y, w, h, items, size=12, color=INK, gap=5, font=BODY_FONT):
    """items: str or list of (text, bold) runs."""
    tf = textbox(s, x, y, w, h).text_frame
    for i, it in enumerate(items):
        runs = [(it, False)] if isinstance(it, str) else it
        para(tf, i == 0, [(t, font, size, b, color) for t, b in runs],
             space_after=gap, line_spacing=1.1)
    return tf


def chip(s, x, y, text, fill=TEAL, w=0.36):
    c = rect(s, x, y, w, 0.36, fill=fill, radius=0.5)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, True, [(text, BODY_FONT, 9.5, True, WHITE)], align=PP_ALIGN.CENTER)


def stat(s, x, y, num, text, w=2.9):
    tb = textbox(s, x, y, w, 1.0)
    para(tb.text_frame, True, [(num, TITLE_FONT, 34, True, TEAL)])
    para(tb.text_frame, False, [(text, BODY_FONT, 11, False, MUTED)], line_spacing=1.05)


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


# ------------------------------------------------------------------ slides
def s1_title(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=INK)
    tb = textbox(s, 0.9, 1.6, 11.5, 0.4)
    para(tb.text_frame, True, [("NLP COURSE PROJECT  ·  INTERIM PRESENTATION", BODY_FONT, 13, True, MINT)])
    tb = textbox(s, 0.9, 2.15, 11.5, 1.2)
    para(tb.text_frame, True, [("MedScribe", TITLE_FONT, 60, True, WHITE)])
    tb = textbox(s, 0.9, 3.4, 11.0, 1.0)
    para(tb.text_frame, True, [("Speaker role detection and automatic SOAP notes from "
                                "doctor–patient conversations", BODY_FONT, 20, False, SOFT)])
    names = ["Mehmet Akif Çavuş", "Yusuf Eren Nalbant", "Alp Enes Şeker", "Ali Iskif"]
    x = 0.9
    for n in names:
        rect(s, x, 5.35, 2.75, 0.5, fill=TEAL, radius=0.5)
        tb = textbox(s, x, 5.35, 2.75, 0.5, anchor=MSO_ANCHOR.MIDDLE)
        para(tb.text_frame, True, [(n, BODY_FONT, 12, True, WHITE)], align=PP_ALIGN.CENTER)
        x += 2.95
    tb = textbox(s, 0.9, 6.3, 8, 0.4)
    para(tb.text_frame, True, [("12 November 2026", BODY_FONT, 12, False, MUTED)])
    notes(s, "Slide 1 (~15 s, Akif): 'We are the MedScribe team. In ten minutes we show what "
             "changed since the proposal, a working demo and our first results.'")


def s2_problem(prs):
    s = base(prs, "PROBLEM", "Doctors write notes instead of listening")
    card(s, 0.55, 1.85, 5.9, 4.6)
    label(s, 0.8, 2.0, 5.4, "THE BURDEN")
    lines(s, 0.8, 2.4, 5.45, 3.9, [
        "Every visit ends in a clinical note, usually typed into the record system during "
        "or after the consultation.",
        "Documentation time is a widely reported driver of physician burnout.",
        "“Ambient scribes” listen to the visit and draft the note; we build a small, "
        "open version of that pipeline.",
    ], size=13, gap=10)
    card(s, 6.85, 1.85, 5.9, 4.6, accent=MINT)
    label(s, 7.1, 2.0, 5.4, "THE NLP GAP WE TARGET")
    lines(s, 7.1, 2.4, 5.4, 1.4, [
        "Diarization separates voices but only says who spoke, not which one is the doctor:",
    ], size=13)
    for i, (spk, role, col) in enumerate([("SPEAKER_00", "Doctor ?", TEAL), ("SPEAKER_01", "Patient ?", TEAL2)]):
        y = 3.55 + i * 0.7
        rect(s, 7.1, y, 2.2, 0.48, fill=SOFT, radius=0.3)
        tb = textbox(s, 7.1, y, 2.2, 0.48, anchor=MSO_ANCHOR.MIDDLE)
        para(tb.text_frame, True, [(spk, MONO, 12, True, INK)], align=PP_ALIGN.CENTER)
        tb = textbox(s, 9.4, y, 0.6, 0.48, anchor=MSO_ANCHOR.MIDDLE)
        para(tb.text_frame, True, [("→", BODY_FONT, 18, True, MUTED)], align=PP_ALIGN.CENTER)
        rect(s, 10.1, y, 2.2, 0.48, fill=col, radius=0.3)
        tb = textbox(s, 10.1, y, 2.2, 0.48, anchor=MSO_ANCHOR.MIDDLE)
        para(tb.text_frame, True, [(role, BODY_FONT, 12, True, WHITE)], align=PP_ALIGN.CENTER)
    lines(s, 7.1, 5.05, 5.4, 1.2, [
        "We predict the role from what each speaker says, and measure whether the role "
        "changes the note an LLM writes.",
    ], size=13)
    notes(s, "Slide 2 (~45 s, Akif): Doctors spend a large part of the visit documenting. "
             "Ambient scribes try to automate the note. The NLP gap: diarization gives "
             "SPEAKER_00 / SPEAKER_01 but not who the doctor is. That is what we solve from text.")


def s3_scope(prs):
    s = base(prs, "WHAT CHANGED AFTER YOUR FEEDBACK", "Narrower scope, one research question")
    cols = [
        (0.55, "KEPT", TEAL, [
            "Speech → speaker-separated transcript (WhisperX)",
            "Doctor / Patient role classifier (ours, trained)",
            "SOAP note generation with an open LLM (prompting, no training)",
            "With-roles vs without-roles experiment",
            "Gradio web demo",
        ]),
        (4.75, "DROPPED", MUTED, [
            "Clinical NER model and hand annotation",
            "Flan-T5 fine-tuning",
            "Building a Turkish dataset",
            "Large human evaluation",
            "Separate WER/DER study",
        ]),
    ]
    for x, head, col, items in cols:
        card(s, x, 1.85, 3.95, 4.15, accent=col)
        label(s, x + 0.25, 2.0, 3.5, head, color=col)
        lines(s, x + 0.25, 2.4, 3.55, 3.5, items, size=12.5, gap=9)
    rect(s, 8.95, 1.85, 3.8, 4.15, fill=INK, radius=0.05)
    label(s, 9.2, 2.0, 3.4, "RESEARCH QUESTION", color=MINT)
    tb = textbox(s, 9.2, 2.45, 3.35, 3.4)
    para(tb.text_frame, True, [("Does telling the LLM who is the doctor and who is the "
                                "patient change the SOAP note it writes?", TITLE_FONT, 17, True, WHITE)],
         line_spacing=1.1)
    para(tb.text_frame, False, [("Same model, same prompt; only the speaker labels in the "
                                 "transcript change.", BODY_FONT, 11.5, False, SOFT)], space_before=12)
    lines(s, 0.55, 6.3, 12.2, 0.6, [[("NLP contribution: ", True),
          ("two role classifiers compared + error analysis, and a controlled measurement of "
           "what role labels do to the generated note.", False)]], size=12.5, color=INK)
    notes(s, "Slide 3 (~60 s, Akif): You told us the proposal was too wide. We kept the "
             "pipeline, dropped NER, fine-tuning, the Turkish dataset and the big human "
             "evaluation. The research question is now one sentence: does role information "
             "change the note? Prompt and model are fixed, only the labels change.")


def s4_arch(prs):
    s = base(prs, "ARCHITECTURE", "Four modules, one shared JSON format")
    steps = [("1", "Speech → text", "WhisperX + pyannote", "Alp · off-the-shelf"),
             ("2", "Role assignment", "TF-IDF + logistic reg.", "Yusuf · our model"),
             ("3", "SOAP note", "Qwen2.5-7B, 4-bit, prompt", "Ali · off-the-shelf"),
             ("4", "Demo", "Gradio", "Akif · interface")]
    x = 0.55
    for i, (n, head, tool, who) in enumerate(steps):
        own = n == "2"
        rect(s, x, 1.9, 2.75, 1.75, fill=TEAL if own else WHITE, line=SOFT, radius=0.08, line_w=1.25)
        fg, sub = (WHITE, SOFT) if own else (INK, MUTED)
        tb = textbox(s, x + 0.15, 2.0, 2.45, 1.6)
        para(tb.text_frame, True, [(n + "  " + head, BODY_FONT, 15, True, fg)])
        para(tb.text_frame, False, [(tool, BODY_FONT, 11.5, False, fg)], space_before=6)
        para(tb.text_frame, False, [(who, BODY_FONT, 10.5, False, sub)], space_before=6)
        if i < 3:
            tb = textbox(s, x + 2.75, 2.45, 0.45, 0.6, anchor=MSO_ANCHOR.MIDDLE)
            para(tb.text_frame, True, [("→", BODY_FONT, 22, True, TEAL2)], align=PP_ALIGN.CENTER)
        x += 3.15
    card(s, 0.55, 4.0, 7.3, 3.0)
    label(s, 0.8, 4.12, 6.8, "EVERY MODULE READS AND WRITES THIS")
    lines(s, 0.8, 4.48, 6.9, 2.45, [
        '{"dialogue_id": "aci_001", "source": "aci-bench",',
        ' "segments": [',
        '   {"id": 0, "speaker": "SPEAKER_00", "start": 0.0,',
        '    "gold_role": "Doctor", "role": "Doctor",',
        '    "role_prob": 0.94, "text": "Any chest pain?"}, ...]}',
    ], size=11, gap=1, font=MONO)
    card(s, 8.15, 4.0, 4.6, 3.0, accent=MINT)
    label(s, 8.4, 4.12, 4.1, "WHY IT WORKED FOR 4 PEOPLE")
    lines(s, 8.4, 4.5, 4.2, 2.4, [
        "One function per module, fixed signature",
        "check_format() before every push",
        "Mock functions: the demo ran before the real modules existed",
    ], size=12, gap=8)
    notes(s, "Slide 4 (~45 s, Akif): Four steps. ASR and the LLM are off-the-shelf; the "
             "role classifier is ours. All modules exchange one JSON format, so each of us "
             "worked independently with mock functions and we integrated at the end.")


def s5_asr(prs):
    s = base(prs, "STEP 1  ·  SPEECH → TEXT", "Who spoke when: WhisperX + pyannote")
    stat(s, 0.55, 1.85, "93.8%", "speaker accuracy, 1,923 / 2,050\nutterances (20 PriMock57 visits)")
    stat(s, 3.65, 1.85, "96.7%", "on utterances longer\nthan 1 second")
    stat(s, 6.75, 1.85, "87.8%", "on short utterances\n(< 1 s, interruptions)")
    stat(s, 9.85, 1.85, "≈", "Whisper small vs medium:\n96.0% vs 96.5%")
    card(s, 0.55, 3.45, 5.95, 3.4, accent=TEAL)
    label(s, 0.8, 3.58, 5.5, "SETUP")
    lines(s, 0.8, 3.95, 5.55, 2.8, [
        "PriMock57 mock consultations (ACL 2022) instead of our own recordings",
        "Doctor and patient channels mixed into one track; gold speaker from channel energy",
        "Whisper small + alignment, pyannote community-1 diarization, no training",
    ], size=12, gap=8)
    card(s, 6.8, 3.45, 5.95, 3.4, accent=MINT)
    label(s, 7.05, 3.58, 5.5, "OBSERVATIONS")
    lines(s, 7.05, 3.95, 5.55, 2.8, [
        "Errors cluster on short turns and interruptions",
        "One person reading both roles → found as one speaker",
        "ASR slips on clinical words (“start” → “stop”)",
        "Output order of SPEAKER_00 / 01 is arbitrary → roles must come from text",
    ], size=12, gap=8)
    notes(s, "Slide 5 (~60 s, Alp) — DRAFT built from asr/README.md and results/kisi1_*.csv; "
             "Alp, please check. Key line: speaker separation is good enough (94%), errors are "
             "on short turns, and the labels SPEAKER_00/01 say nothing about who the doctor is.")


def s6_roles(prs, m):
    f = m["group_5fold"]
    s = base(prs, "STEP 2  ·  ROLE ASSIGNMENT (OUR MODEL)", "Who is the doctor? Predicted from text")
    card(s, 0.55, 1.85, 6.0, 2.55, accent=TEAL)
    label(s, 0.8, 1.98, 5.5, "METHOD")
    lines(s, 0.8, 2.35, 5.6, 2.0, [
        "All utterances of one speaker → one document",
        "Word 1–2-gram + char 3–5-gram TF-IDF → logistic regression",
        "Two speakers: exactly one Doctor, one Patient",
    ], size=12, gap=7)
    card(s, 0.55, 4.6, 6.0, 2.3, accent=MINT)
    label(s, 0.8, 4.72, 5.5, "DATA AND EVALUATION")
    lines(s, 0.8, 5.08, 5.6, 1.8, [
        "ACI-Bench, 67 encounters; split by encounter, no leakage",
        "5-fold group cross-validation, speaker level",
        "Swapping A/B labels swaps the prediction: it reads text, not names",
    ], size=12, gap=7)
    stat(s, 7.0, 1.85, f"{f['accuracy_mean']*100:.1f}%", f"accuracy, 5-fold mean\n(± {f['accuracy_std']*100:.1f})", w=2.8)
    stat(s, 9.9, 1.85, f"{f['macro_f1_mean']:.2f}", "macro-F1, 5-fold mean", w=2.8)
    card(s, 7.0, 3.45, 5.75, 3.45)
    label(s, 7.25, 3.58, 5.3, "HOLD-OUT (14 ENCOUNTERS)")
    cm = m["holdout"]["confusion_matrix"]
    hdr = [("", "pred Doctor", "pred Patient"), ("Doctor", str(cm[0][0]), str(cm[0][1])),
           ("Patient", str(cm[1][0]), str(cm[1][1]))]
    for r, row in enumerate(hdr):
        for c, v in enumerate(row):
            x, y = 7.3 + c * 1.75, 4.0 + r * 0.6
            if r and c:
                rect(s, x, y, 1.6, 0.5, fill=SOFT if r != c else TEAL, radius=0.15)
            tb = textbox(s, x, y, 1.6, 0.5, anchor=MSO_ANCHOR.MIDDLE)
            col = WHITE if (r and c and r == c) else (MUTED if not (r and c) else INK)
            para(tb.text_frame, True, [(v, BODY_FONT, 12, bool(r and c), col)], align=PP_ALIGN.CENTER)
    lines(s, 7.25, 5.95, 5.3, 0.9, [
        f"Hold-out accuracy {m['holdout']['accuracy']*100:.0f}%; the 5-fold mean is the "
        "number we report."], size=11, color=MUTED)
    notes(s, "Slide 6 (~90 s, Yusuf) — DRAFT built from roles/README.md and "
             "results/kisi2_role_metrics.json; Yusuf, please check. Key line: each speaker's "
             "text is classified as a whole; 92.5% mean accuracy over 5 folds split by "
             "encounter. Plan deviation: trained on ACI-Bench, not MTS-Dialog.")


def s9_demo(prs, demo):
    s = base(prs, "LIVE DEMO", "Paste a dialogue, get roles and a note")
    for i, (h, d) in enumerate([("Paste", "Speakers are only “A:” and “B:”"),
                                ("Run", "Our model decides who the doctor is"),
                                ("Read", "Colored transcript + S / O / A / P note")]):
        y = 1.95 + i * 1.0
        chip(s, 0.55, y, str(i + 1))
        tb = textbox(s, 1.05, y - 0.06, 3.6, 0.9)
        para(tb.text_frame, True, [(h, BODY_FONT, 14, True, INK)])
        para(tb.text_frame, False, [(d, BODY_FONT, 11.5, False, MUTED)])
    lines(s, 0.55, 5.2, 4.1, 1.6, [
        "Runs on one Colab T4: Whisper + 4-bit 7B LLM + TF-IDF.",
        "Audio upload: next step.",
    ], size=11.5, color=MUTED, gap=6)
    card(s, 4.95, 1.85, 7.8, 5.05)
    label(s, 5.2, 1.98, 7.3, "REAL OUTPUT OF OUR ROLE MODEL ON THE DEMO TEXT")
    y = 2.4
    for seg in demo["segments"][:6]:
        doc = seg["role"] == "Doctor"
        rect(s, 5.2, y, 7.3, 0.56, fill=SOFT if doc else WHITE, line=SOFT, radius=0.15)
        tb = textbox(s, 5.3, y, 7.1, 0.56, anchor=MSO_ANCHOR.MIDDLE)
        txt = seg["text"] if len(seg["text"]) < 70 else seg["text"][:67] + "…"
        para(tb.text_frame, True, [(("Doctor  " if doc else "Patient  "), BODY_FONT, 11, True, TEAL if doc else TEAL2),
                                   (f"{seg['speaker']}  ", MONO, 10, False, MUTED),
                                   (txt, BODY_FONT, 11, False, INK)])
        y += 0.63
    pa = {g["speaker"]: g["role_prob"] for g in demo["segments"]}
    lines(s, 5.2, 6.25, 7.3, 0.4, [f"P(doctor):  A = {pa['A']:.2f}   ·   B = {pa['B']:.2f}"],
          size=11, color=MUTED)
    notes(s, "Slide 9 (~2 min, Akif): Switch to the Gradio tab (opened before the talk). "
             "Paste app/demo_metin.txt, press Run. Say: 'Only A and B are given; our model "
             "decided A is the doctor.' Show the colors and probabilities, then the note: point "
             "at one symptom in S and the plan in P. If anything fails, go to the next "
             "(hidden) backup slide.")


def s9b_backup(prs, dlg, note):
    s = base(prs, "BACKUP  ·  PRE-RECORDED OUTPUT (aci_002)", "Same pipeline, output captured before the talk")
    card(s, 0.55, 1.85, 5.6, 5.05)
    label(s, 0.8, 1.98, 5.2, "ROLES PREDICTED BY OUR MODEL")
    tf = textbox(s, 0.8, 2.35, 5.2, 4.45).text_frame
    for i, seg in enumerate(dlg["segments"][:15]):
        t = seg["text"] if len(seg["text"]) < 62 else seg["text"][:59] + "…"
        para(tf, i == 0, [(seg["role"] + ": ", BODY_FONT, 10.5, True, TEAL if seg["role"] == "Doctor" else TEAL2),
                          (t, BODY_FONT, 10.5, False, INK)], space_after=3)
    card(s, 6.45, 1.85, 6.3, 5.05, accent=MINT)
    label(s, 6.7, 1.98, 5.8, "SOAP NOTE  ·  " + note["model"])
    tf = textbox(s, 6.7, 2.35, 5.9, 4.45).text_frame
    for i, k in enumerate("SOAP"):
        v = note[k] if len(note[k]) < 210 else note[k][:207] + "…"
        para(tf, i == 0, [(k + "   ", TITLE_FONT, 13, True, TEAL), (v, BODY_FONT, 10.5, False, INK)],
             space_after=7)
    s._element.set("show", "0")   # hidden slide
    notes(s, "HIDDEN backup for slide 9. Use only if the live demo fails: 'Here is the output "
             "we captured before the talk.' Roles come from our classifier (all 26 utterances "
             "correct); the note was generated by Qwen2.5-7B on Colab.")


def s10_next(prs):
    s = base(prs, "NEXT STEPS", "Until the final presentation")
    items = [
        ("Roles", "Fine-tune BERT and compare with TF-IDF; error analysis on 20–30 misclassified utterances."),
        ("Experiment", "Grow with/without-roles to 20 held-out dialogues; ROUGE + BERTScore + error counts."),
        ("Prompt", "Add a third-person summarisation rule — the echo problem from slide 8."),
        ("Demo", "Connect audio upload: recording → transcript → roles → note."),
    ]
    for i, (h, d) in enumerate(items):
        x, y = 0.55 + (i % 2) * 6.2, 1.9 + (i // 2) * 2.35
        card(s, x, y, 5.95, 2.1, accent=TEAL if i % 3 == 0 else MINT)
        chip(s, x + 0.25, y + 0.25, str(i + 1))
        tb = textbox(s, x + 0.8, y + 0.2, 4.95, 1.8)
        para(tb.text_frame, True, [(h, BODY_FONT, 15, True, INK)])
        para(tb.text_frame, False, [(d, BODY_FONT, 12.5, False, MUTED)], space_before=6, line_spacing=1.1)
    lines(s, 0.55, 6.75, 12, 0.4, ["Thank you — questions?"], size=13, color=TEAL)
    notes(s, "Slide 10 (~45 s, Yusuf): BERT vs TF-IDF and error analysis; the experiment "
             "grows to 20 dialogues that the role model never saw in training; prompt fix for "
             "the echo problem; audio input in the demo.")


def main():
    from app.pipeline import parse_text
    from roles.assign_roles import assign_roles

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)

    m = json.load(open(os.path.join(ROOT, "results", "kisi2_role_metrics.json")))
    demo = assign_roles(parse_text(open(os.path.join(ROOT, "app", "demo_metin.txt")).read()))
    dlg = json.load(open(os.path.join(ROOT, "notes", "data", "aci_002.json")))
    for seg in dlg["segments"]:
        seg["role"] = None
    dlg = assign_roles(dlg)
    note = json.load(open(os.path.join(ROOT, "notes", "outputs", "aci_002_rollu.json")))

    s1_title(prs); s2_problem(prs); s3_scope(prs); s4_arch(prs)
    s5_asr(prs); s6_roles(prs, m)
    slide_notes_generation(prs); slide_experiment(prs)
    s9_demo(prs, demo); s9b_backup(prs, dlg, note); s10_next(prs)

    out = os.path.join(ROOT, "results", "medscribe_interim.pptx")
    prs.save(out)
    print("->", out, len(prs.slides._sldIdLst), "slides")


if __name__ == "__main__":
    main()
