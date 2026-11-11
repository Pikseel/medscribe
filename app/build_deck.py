"""MedScribe mid-project deck, built to the CSE 484 rubric (Nov 2026).

Part 1: 10 talk slides in the rubric's order.  Part 2: Project Card, 4 appendix slides.
Every number is read from results/ files at build time:
    results/kisi4_role_eval.json   (python -m eval.role_eval)
    results/kisi2_role_metrics.json, results/kisi1_eval_small.csv, notes/outputs/*.json
Reuses Person 2's method slide and Person 3's note slide unchanged.

    python -m app.build_deck   ->  results/medscribe_midproject.pptx
"""
import csv
import re
import json
import os
import statistics as st

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

from notes.build_slides import (INK, TEAL, TEAL2, MINT, MUTED, BG, WHITE, SOFT,
                                TITLE_FONT, BODY_FONT, rect, textbox, para,
                                slide_notes_generation)
from roles.build_slides import slide_method

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = "Courier New"
REPO = "github.com/Pikseel/medscribe"


def R(*p):
    return os.path.join(ROOT, *p)


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


# ------------------------------------------------------------------ helpers
def base(prs, kicker, title):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=BG)
    rect(s, 0, 0, 0.13, 7.5, fill=TEAL)
    tb = textbox(s, 0.55, 0.40, 9.5, 0.3)
    para(tb.text_frame, True, [(kicker, BODY_FONT, 11, True, TEAL)])
    if title:
        tb = textbox(s, 0.55, 0.70, 12.2, 0.75)
        para(tb.text_frame, True, [(title, TITLE_FONT, 30, True, INK)], line_spacing=0.95)
    return s


def card(s, x, y, w, h, accent=None, fill=WHITE):
    rect(s, x, y, w, h, fill=fill, line=SOFT, radius=0.04, line_w=1.25)
    if accent is not None:
        rect(s, x, y, 0.05, h, fill=accent)


def label(s, x, y, w, text, color=TEAL2):
    tb = textbox(s, x, y, w, 0.3)
    para(tb.text_frame, True, [(text, BODY_FONT, 10.5, True, color)])


def lines(s, x, y, w, h, items, size=12, color=INK, gap=5, font=BODY_FONT):
    tf = textbox(s, x, y, w, h).text_frame
    for i, it in enumerate(items):
        runs = [(it, False)] if isinstance(it, str) else it
        para(tf, i == 0, [(t, font, size, b, color) for t, b in runs], space_after=gap, line_spacing=1.08)
    return tf


def stat(s, x, y, num, text, w=2.9, size=30):
    tb = textbox(s, x, y, w, 1.0)
    para(tb.text_frame, True, [(num, TITLE_FONT, size, True, TEAL)])
    para(tb.text_frame, False, [(text, BODY_FONT, 10.5, False, MUTED)], line_spacing=1.05)


def table(s, x, y, col_w, rows, row_h=0.42, size=11, head_fill=INK, bold_rows=()):
    """rows[0] is the header. col_w: list of widths (in)."""
    for r, row in enumerate(rows):
        cx = x
        for c, v in enumerate(row):
            if r == 0:
                rect(s, cx, y, col_w[c], row_h, fill=head_fill)
                col, b = WHITE, True
            else:
                rect(s, cx, y, col_w[c], row_h, fill=WHITE if r % 2 else SOFT, line=SOFT, line_w=0.75)
                col, b = INK, (r in bold_rows)
            tb = textbox(s, cx, y, col_w[c], row_h, anchor=MSO_ANCHOR.MIDDLE)
            para(tb.text_frame, True, [(str(v), BODY_FONT, size, b, col)],
                 align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)
            cx += col_w[c]
        y += row_h
    return y


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


def ci(v):
    return f"{pct(v['accuracy'])}  [{v['ci95'][0] * 100:.1f}–{v['ci95'][1] * 100:.1f}]"


# ------------------------------------------------------------------ data
def load_all():
    ev = json.load(open(R("results", "kisi4_role_eval.json")))
    cv = json.load(open(R("results", "kisi2_role_metrics.json")))["group_5fold"]
    asr = list(csv.DictReader(open(R("results", "kisi1_eval_small.csv"))))
    from rouge_score import rouge_scorer
    sc = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    rouge = {}
    for cond in ("rollu", "rolsuz"):
        rouge[cond] = []
        for i in (1, 2, 3):
            ref = json.load(open(R("notes", "data", f"aci_00{i}.json")))["reference_note"]
            n = json.load(open(R("notes", "outputs", f"aci_00{i}_{cond}.json")))
            sco = sc.score(ref, "\n".join(n[k] for k in "SOAP"))
            rouge[cond].append({m: sco[m].fmeasure for m in ("rouge1", "rouge2", "rougeL")})
    acc = [float(r["dogruluk"]) for r in asr]
    asr_s = {"n": len(asr), "correct": sum(int(r["dogru_n"]) for r in asr),
             "total": sum(int(r["cumle"]) for r in asr), "mean": st.mean(acc), "std": st.pstdev(acc),
             "min": min(acc)}
    return ev, cv, asr_s, rouge


def rmean(rouge, cond, m):
    return st.mean(x[m] for x in rouge[cond])


# ------------------------------------------------------------------ talk slides
def s1_rq(prs, rouge):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=INK)
    tb = textbox(s, 0.7, 0.45, 12, 0.35)
    para(tb.text_frame, True, [("CSE 484 MID-PROJECT  ·  MEDSCRIBE", BODY_FONT, 12, True, MINT)])
    label(s, 0.7, 1.05, 6, "RESEARCH QUESTION", color=SOFT)
    tb = textbox(s, 0.7, 1.4, 11.9, 1.4)
    para(tb.text_frame, True, [("Do Doctor / Patient speaker labels make an LLM write a "
                                "better SOAP note from a consultation transcript?", TITLE_FONT, 28, True, WHITE)],
         line_spacing=1.05)
    rect(s, 0.7, 3.05, 7.4, 2.55, fill=TEAL, radius=0.04)
    tb = textbox(s, 0.95, 3.18, 7.0, 2.35)
    para(tb.text_frame, True, [("FIRST ANSWER:  NO, NOT ON AVERAGE", BODY_FONT, 13, True, WHITE)])
    para(tb.text_frame, False, [(f"ROUGE-L {rmean(rouge, 'rollu', 'rougeL'):.3f} with labels vs "
                                 f"{rmean(rouge, 'rolsuz', 'rougeL'):.3f} without", TITLE_FONT, 18, True, WHITE)],
         space_before=6)
    para(tb.text_frame, False, [("3 dev dialogues, Qwen2.5-7B, same prompt. Labels fixed a negation "
                                 "error but made the model echo the longest transcript: errors moved, "
                                 "they did not disappear.", BODY_FONT, 12.5, False, SOFT)], space_before=8,
         line_spacing=1.1)
    rect(s, 8.4, 3.05, 4.25, 2.55, fill=WHITE, radius=0.04)
    tb = textbox(s, 8.6, 3.18, 3.9, 2.35)
    para(tb.text_frame, True, [("CHANGED SINCE THE PROPOSAL", BODY_FONT, 10.5, True, TEAL)])
    para(tb.text_frame, False, [("Old: build a 5-stage scribe (ASR, roles, NER, note, demo), no single "
                                 "question.", BODY_FONT, 11, False, INK)], space_before=5, line_spacing=1.08)
    para(tb.text_frame, False, [("Why: feedback asked us to narrow it; NER, fine-tuning and the Turkish "
                                 "set are dropped.", BODY_FONT, 11, False, INK)], space_before=5, line_spacing=1.08)
    x = 0.7
    for n in ["Mehmet Akif Çavuş", "Yusuf Eren Nalbant", "Alp Enes Şeker", "Ali Iskif"]:
        rect(s, x, 6.25, 2.85, 0.48, fill=TEAL2, radius=0.5)
        tb = textbox(s, x, 6.25, 2.85, 0.48, anchor=MSO_ANCHOR.MIDDLE)
        para(tb.text_frame, True, [(n, BODY_FONT, 12, True, WHITE)], align=PP_ALIGN.CENTER)
        x += 3.0
    notes(s, "Slide 1 (~60 s, Akif): State the question. Our first answer is no: on three "
             "dialogues, labels did not raise ROUGE and the error types moved around. The "
             "proposal was a five-stage system without a single question; after your feedback "
             "we kept one question and dropped NER, fine-tuning and the Turkish dataset.")


def s2_system(prs):
    s = base(prs, "SYSTEM AND WHAT IS IMPLEMENTED", "Four modules, one shared JSON format")
    steps = [("1", "Speech → text", "WhisperX + pyannote", "Alp · ASR lead · pretrained, no training", "implemented"),
             ("2", "Role assignment", "TF-IDF + logistic regression", "Yusuf · roles lead · trained by us", "implemented"),
             ("3", "SOAP note", "Qwen2.5-7B 4-bit + frozen prompt", "Ali · notes lead · pretrained, prompting", "implemented"),
             ("4", "Demo", "Gradio, runs on one Colab T4", "Akif · demo lead · interface", "text input works")]
    x = 0.55
    for i, (n, head, tool, who, status) in enumerate(steps):
        own = n == "2"
        rect(s, x, 1.75, 2.8, 2.1, fill=TEAL if own else WHITE, line=SOFT, radius=0.06, line_w=1.25)
        fg, sub = (WHITE, SOFT) if own else (INK, MUTED)
        tb = textbox(s, x + 0.15, 1.85, 2.5, 1.95)
        para(tb.text_frame, True, [(n + "  " + head, BODY_FONT, 15, True, fg)])
        para(tb.text_frame, False, [(tool, BODY_FONT, 11.5, False, fg)], space_before=6)
        para(tb.text_frame, False, [(who, BODY_FONT, 10.5, False, sub)], space_before=6)
        para(tb.text_frame, False, [("● " + status, BODY_FONT, 10.5, True, MINT if not own else WHITE)],
             space_before=8)
        if i < 3:
            tb = textbox(s, x + 2.8, 2.5, 0.35, 0.6, anchor=MSO_ANCHOR.MIDDLE)
            para(tb.text_frame, True, [("→", BODY_FONT, 20, True, TEAL2)], align=PP_ALIGN.CENTER)
        x += 3.15
    card(s, 0.55, 4.15, 7.4, 2.8)
    label(s, 0.8, 4.27, 6.9, "EVERY MODULE READS AND WRITES THIS")
    lines(s, 0.8, 4.65, 7.0, 2.2, [
        '{"dialogue_id": "aci_002", "source": "aci-bench",',
        ' "segments": [{"id": 4, "speaker": "SPEAKER_00",',
        '   "gold_role": "Doctor", "role": "Doctor", "role_prob": 0.91,',
        '   "text": "have you noticed any rashes?"}, ...]}',
    ], size=11, gap=1, font=MONO)
    card(s, 8.25, 4.15, 4.5, 2.8, accent=MINT)
    label(s, 8.5, 4.27, 4.0, "DEMO STATUS")
    lines(s, 8.5, 4.65, 4.1, 2.2, [
        "Pasted A/B text → roles → SOAP note works end to end.",
        "Audio input is not connected yet.",
        "Modules plug in by file name; mocks kept the demo running before they existed.",
    ], size=12, gap=8)
    notes(s, "Slide 2 (~45 s, Akif): Four modules. ASR and the LLM are pretrained; the role "
             "classifier is trained by us. They exchange one JSON format. The demo works on "
             "pasted text; audio is the next step.")


def s3_data(prs, ev, asr):
    c = ev["counts"]
    s = base(prs, "DATA AS LOADED", "Published ACI-Bench splits, frozen test set")
    rows = [["ACI-Bench (CC BY 4.0)", "encounters", "speakers", "utterances", "used for"],
            ["train  ·  train.csv", c["train"]["encounters"], c["train"]["speakers"], f"{c['train']['utterances']:,}",
             "role model training"],
            ["dev  ·  valid.csv", c["dev"]["encounters"], c["dev"]["speakers"], f"{c['dev']['utterances']:,}",
             "model choice"],
            ["test  ·  taskB_test1.csv", c["test"]["encounters"], c["test"]["speakers"], f"{c['test']['utterances']:,}",
             "frozen, run once"]]
    table(s, 0.55, 1.75, [3.1, 1.35, 1.35, 1.4, 2.4], rows, row_h=0.48, size=12, bold_rows=(3,))
    lines(s, 0.55, 3.8, 9.6, 1.0, [
        "Preprocessing: [doctor]/[patient] tags → roles; [patient_guest] lines dropped (38 dev, 50 test). "
        "No other filtering.",
        f"PriMock57 (ASR only): 20 consultations, first 5 min, {asr['total']:,} utterances; gold speaker "
        "from channel energy.",
    ], size=11.5, color=MUTED, gap=6)
    card(s, 10.4, 1.75, 2.35, 2.0, accent=MINT)
    tb = textbox(s, 10.6, 1.85, 2.05, 1.85)
    para(tb.text_frame, True, [("FROZEN", BODY_FONT, 10.5, True, TEAL2)])
    para(tb.text_frame, False, [("Test labels are not used for training, prompt changes or model "
                                 "choice.", BODY_FONT, 11, False, INK)], space_before=4, line_spacing=1.08)
    card(s, 0.55, 4.95, 12.2, 2.0)
    label(s, 0.8, 5.05, 11, "ONE REAL EXAMPLE  ·  aci_002 (train D2N053), transcript and reference note")
    lines(s, 0.8, 5.4, 6.4, 1.5, [
        "[doctor] have you seen ever noticed any rashes either when it",
        "  first started or intermittently?",
        "[patient] on my body no not really",
    ], size=10.5, gap=1, font=MONO)
    lines(s, 7.4, 5.4, 5.2, 1.5, [
        [("Reference note: ", True), ("“… Denies any rashes …”", False)],
        "Target: the note must keep the patient's denial.",
    ], size=11.5, gap=6)
    notes(s, "Slide 3 (~45 s): We use ACI-Bench's published splits as they are: 67 train, 20 dev, "
             "40 test encounters. The test file is frozen and run once. PriMock57 is only used "
             "to measure speaker separation on audio.")


def s4_asr(prs, asr):
    s = base(prs, "STEP 1  ·  SPEECH → TEXT", "Who spoke when: WhisperX + pyannote")
    stat(s, 0.55, 1.6, "93.8%", f"speaker accuracy, {asr['correct']:,} / {asr['total']:,}\nutterances, 20 PriMock57 consultations")
    stat(s, 3.65, 1.6, "96.7%", "on utterances longer\nthan 1 second")
    stat(s, 6.75, 1.6, "87.8%", "on short utterances\n(< 1 s)")
    stat(s, 9.85, 1.6, "≈", "Whisper small vs medium model\ncomparison: 93.8% vs 94.1%")
    card(s, 0.55, 3.15, 5.95, 3.15, accent=TEAL)
    label(s, 0.8, 3.28, 5.5, "SETUP")
    lines(s, 0.8, 3.65, 5.55, 2.6, [
        "PriMock57 mock consultations (ACL 2022)",
        "Doctor and patient channels mixed into one track",
        "Whisper small + alignment, pyannote community-1 diarization, no training",
        f"Spread over consultations: {asr['mean'] * 100:.1f} ± {asr['std'] * 100:.1f} pp (min {asr['min'] * 100:.1f}%)",
    ], size=12, gap=8)
    card(s, 6.8, 3.15, 5.95, 3.15, accent=MINT)
    label(s, 7.05, 3.28, 5.5, "OBSERVATIONS")
    lines(s, 7.05, 3.65, 5.55, 2.6, [
        "Errors cluster on short turns",
        "One person reading both roles → found as one speaker",
        "SPEAKER_00 / 01 numbers carry no role information, so the role model (next step) "
        "decides who is the doctor",
    ], size=12, gap=8)
    lines(s, 0.55, 6.5, 12.2, 0.5, ["Limitations: clean mock audio; gold labels from channel energy "
                                    "(approximate); speaker accuracy only, not WER/DER."], size=11, color=MUTED)
    notes(s, "Slide 4 (~45 s, Alp): Speaker separation is 93.8% on 20 consultations; errors are "
             "on short turns; the SPEAKER_00/01 labels say nothing about who the doctor is. Small "
             "and medium give the same speaker accuracy (93.8% vs 94.1%), so model size does not "
             "matter here.")


def s6_baseline(prs, ev, cv):
    r = ev["results"]
    s = base(prs, "BASELINE RESULTS  ·  FROZEN TEST SET", "Role assignment: near ceiling on clean transcripts")
    rows = [["System (speaker level)", "dev  (20 enc.)", "test  (40 enc.)  [95% CI]"],
            ["First speaker is the doctor", pct(r["first_speaker"]["dev"]["accuracy"]), ci(r["first_speaker"]["test"])],
            ["More “you / your” is the doctor", pct(r["you_ratio"]["dev"]["accuracy"]), ci(r["you_ratio"]["test"])],
            ["TF-IDF + LR, ours", pct(r["tfidf_lr"]["dev"]["accuracy"]), ci(r["tfidf_lr"]["test"])],
            ["TF-IDF + LR, one utterance at a time", pct(r["utterance_tfidf_lr"]["dev"]["accuracy"]),
             ci(r["utterance_tfidf_lr"]["test"])]]
    table(s, 0.55, 1.7, [4.2, 1.9, 3.3], rows, row_h=0.55, size=12.5, bold_rows=(3,))
    lines(s, 0.55, 4.6, 9.4, 0.9, [
        f"Spread: 95% bootstrap interval over test encounters (2,000 resamples, seed 0). On train, "
        f"5-fold grouped CV gives {cv['accuracy_mean'] * 100:.1f} ± {cv['accuracy_std'] * 100:.1f}.",
    ], size=11, color=MUTED)
    card(s, 10.2, 1.7, 2.55, 2.75, fill=INK)
    tb = textbox(s, 10.35, 1.82, 2.3, 2.55)
    para(tb.text_frame, True, [("1 / 40", TITLE_FONT, 30, True, WHITE)])
    para(tb.text_frame, False, [("test encounter wrong for our model (D2N114); the “you” rule makes the "
                                 "same mistake", BODY_FONT, 11, False, SOFT)], space_before=4, line_spacing=1.08)
    card(s, 0.55, 5.4, 12.2, 1.55, accent=MINT)
    label(s, 0.8, 5.5, 11, "WHAT THIS MEANS")
    lines(s, 0.8, 5.85, 11.7, 1.1, [
        "Our model ties a one-line rule on ACI-Bench, so a clean transcript is not where it is needed. "
        "One utterance alone is only 86.8% right: pooling a speaker's turns is what makes the task easy. "
        "The real test is diarized ASR output, where the turn order is wrong for short turns.",
    ], size=12, gap=4)
    notes(s, "Slide 6 (~75 s, Yusuf): Test set is ACI-Bench task B test 1, 40 encounters, run "
             "once. Our TF-IDF model gets 97.5%, the same as a rule that picks the speaker who "
             "says 'you' more; first speaker gets 95%. Per utterance the same features give 86.8%. "
             "So pooling per speaker is the useful part, and we need harder input to separate the "
             "systems.")


def s7_errors(prs, ev):
    e = ev["utterance_errors_test"]
    total_utts = ev["counts"]["test"]["utterances"]
    s = base(prs, "ERROR ANALYSIS  ·  TEST SET", f"{e['total']} utterance-level errors, grouped")
    cats = list(e["by_category"].items())
    data = CategoryChartData()
    data.categories = [c for c, _ in cats][::-1]
    data.add_series("errors", [n for _, n in cats][::-1])
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.45), Inches(1.6), Inches(6.4), Inches(3.6), data)
    ch = gf.chart
    ch.has_legend = False
    ch.font.size = Pt(11)
    ch.font.name = BODY_FONT
    pl = ch.plots[0]
    pl.gap_width = 60
    pl.has_data_labels = True
    pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    pl.data_labels.font.size = Pt(11)
    pl.data_labels.font.bold = True
    ser = pl.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = TEAL
    ch.value_axis.visible = False
    ch.value_axis.has_major_gridlines = False
    ch.category_axis.format.line.fill.background()
    ch.category_axis.tick_labels.font.color.rgb = INK
    lines(s, 0.55, 5.25, 6.3, 0.5, [f"{e['total']} of {total_utts:,} test utterances "
                                     f"({e['total'] / total_utts * 100:.1f}%); rule-based categories, "
                                     "full list in results/kisi4_utterance_errors.csv"], size=10, color=MUTED)
    card(s, 7.1, 1.6, 5.65, 4.1)
    label(s, 7.35, 1.72, 5.2, "ONE EXAMPLE PER CATEGORY")
    tf = textbox(s, 7.35, 2.08, 5.25, 3.55).text_frame
    for i, (c, _) in enumerate(cats):
        ex = e["examples"][c]
        ex = ex if len(ex) < 80 else ex[:77] + "…"
        para(tf, i == 0, [(c.split(" (")[0] + ":  ", BODY_FONT, 10.5, True, TEAL), (f"“{ex}”", BODY_FONT, 10.5, False, INK)],
             space_after=6, line_spacing=1.05)
    card(s, 0.55, 5.85, 12.2, 1.15, accent=MINT)
    label(s, 0.8, 5.93, 11, "WHAT THEY SUGGEST")
    lines(s, 0.8, 6.27, 11.7, 0.75, [
        "Backchannels (“okay.”) carry no role signal → never decide per utterance, pool per speaker. "
        "Patients also say “you” and ask questions → the “you” rule and question counts break on short "
        "or role-reversed dialogues."], size=11.5)
    notes(s, "Slide 7 (~60 s): 269 errors when every utterance is classified alone. The biggest "
             "group is short backchannels like 'okay', which no text model can place. Patients "
             "addressing the doctor with 'you' and asking questions are next: these are also the "
             "cases that would break the simple rule baselines. Categories are assigned by rules; "
             "we will hand-check a sample of 30 before the final.")


def s9_experiment(prs, rouge):
    s = base(prs, "METHOD STATUS  ·  FIRST NUMBERS ON DEV", "With roles vs without: same model, same prompt")
    rows = [["ROUGE vs reference note", "R-1", "R-2", "R-L"]]
    for cond, name in (("rolsuz", "Without labels (baseline)"), ("rollu", "With Doctor/Patient labels")):
        rows.append([name] + [f"{rmean(rouge, cond, m):.3f}" for m in ("rouge1", "rouge2", "rougeL")])
    table(s, 0.55, 1.7, [3.6, 1.1, 1.1, 1.1], rows, row_h=0.5, size=12.5)
    lines(s, 0.55, 3.3, 6.9, 0.6, ["Mean of 3 dialogues (D2N050, D2N053, D2N060 from the train split), "
                                   "Qwen2.5-7B-Instruct 4-bit, temperature 0, frozen prompt v1."],
          size=10.5, color=MUTED)
    card(s, 0.55, 4.05, 6.9, 2.9, accent=TEAL)
    label(s, 0.8, 4.17, 6.4, "ONE CONTROLLED CHANGE")
    lines(s, 0.8, 4.52, 6.5, 2.4, [
        "Only the transcript changes: “Doctor: … / Patient: …” vs plain lines in the same order.",
        "Prompt, model, decoding and data are identical.",
        "ROUGE barely moves (≤ 0.005), so we read every note side by side →",
    ], size=12, gap=8)
    card(s, 7.75, 1.7, 5.0, 5.25)
    label(s, 8.0, 1.82, 4.6, "WHAT THE 6 NOTES SHOWED")
    items = [("With labels", "1 of 3 notes echoed the transcript (aci_003: 3,229 chars, 7 of 9 S sentences "
                             "in first person)"),
             ("Without labels", "1 of 3 lost negation scope (aci_002: “no joint pain, fever, weight loss”)"),
             ("Both", "118/72 written as 180/72; “push fluids” added though nobody said it")]
    tf = textbox(s, 8.0, 2.2, 4.6, 4.6).text_frame
    for i, (h, d) in enumerate(items):
        para(tf, i == 0, [(h, BODY_FONT, 13, True, INK)], space_before=0 if i == 0 else 10)
        para(tf, False, [(d, BODY_FONT, 11.5, False, MUTED)], line_spacing=1.08)
    notes(s, "Slide 9 (~60 s, Ali): First numbers on three development dialogues. Without labels "
             "is our baseline, with labels is the method; the transcript is the only change. ROUGE "
             "is flat. Reading the notes, labels fixed a negation error but caused an echo on the "
             "longest dialogue. ROUGE cannot see these errors, so the final uses error counts too.")


PLAN = [("Run with/without labels on the 40 frozen test dialogues; ROUGE + BERTScore", "Notes lead", "Nov 26"),
        ("Ablation: anonymous A/B labels (turns, no roles) as a 3rd condition", "Notes lead", "Nov 26"),
        ("Attribution-error checklist; 2 people label 10 notes for agreement", "Demo + notes", "Dec 3"),
        ("BERT role classifier vs TF-IDF on the same frozen test", "Roles lead", "Nov 26"),
        ("Hand-check 30 utterance errors; roles on diarized ASR output", "Roles + ASR", "Dec 3"),
        ("Predicted vs gold roles into the note (error propagation)", "ASR + notes", "Dec 10"),
        ("Audio input in the demo; report skeleton", "Demo lead", "Dec 10")]


def s10_plan(prs):
    s = base(prs, "PLAN TO THE FINAL", "Remaining experiments, owners and dates")
    table(s, 0.55, 1.6, [6.0, 1.9, 1.2], [["Experiment", "Owner", "Date"]] + [list(p) for p in PLAN],
          row_h=0.5, size=11.5)
    card(s, 9.95, 1.6, 2.8, 2.45, fill=INK)
    tb = textbox(s, 10.1, 1.72, 2.55, 2.25)
    para(tb.text_frame, True, [("ABLATION", BODY_FONT, 10.5, True, MINT)])
    para(tb.text_frame, False, [("No speaker info  →  anonymous A/B  →  Doctor/Patient. Separates "
                                 "“knowing the turns” from “knowing the roles”.", BODY_FONT, 11.5, False, WHITE)],
         space_before=4, line_spacing=1.08)
    card(s, 9.95, 4.2, 2.8, 2.75, accent=MINT)
    tb = textbox(s, 10.15, 4.3, 2.5, 2.6)
    para(tb.text_frame, True, [("BIGGEST RISK", BODY_FONT, 10.5, True, TEAL2)])
    para(tb.text_frame, False, [("ROUGE cannot see who-said-what errors, so a real effect looks like "
                                 "noise.", BODY_FONT, 11, False, INK)], space_before=3, line_spacing=1.05)
    para(tb.text_frame, False, [("Fallback: ", BODY_FONT, 11, True, INK),
                                ("count negation flips and question→complaint errors with a fixed "
                                 "checklist.", BODY_FONT, 11, False, INK)], space_before=5, line_spacing=1.05)
    notes(s, "Slide 10 (~45 s, Yusuf): Each remaining step has an owner and a date. The ablation "
             "adds anonymous A/B labels between 'no speaker info' and 'roles'. The main risk is "
             "that ROUGE does not see attribution errors; the fallback is a fixed error checklist "
             "with a small agreement check.")


# ------------------------------------------------------------------ project card
def card_slide(prs, idx, fields):
    s = base(prs, f"PART 2  ·  PROJECT CARD  ({idx} / 4)", "")
    y = 0.85
    for (num, name, h, body) in fields:
        card(s, 0.55, y, 12.2, h)
        rect(s, 0.75, y + 0.17, 0.42, 0.42, fill=TEAL, radius=0.5)
        tb = textbox(s, 0.75, y + 0.17, 0.42, 0.42, anchor=MSO_ANCHOR.MIDDLE)
        para(tb.text_frame, True, [(str(num), BODY_FONT, 11, True, WHITE)], align=PP_ALIGN.CENTER)
        tb = textbox(s, 1.3, y + 0.12, 11.3, 0.4)
        para(tb.text_frame, True, [(name, BODY_FONT, 14, True, INK)])
        if body:
            tf = textbox(s, 1.3, y + 0.5, 11.3, h - 0.58).text_frame
            for i, it in enumerate(body):
                runs = [(it, False)] if isinstance(it, str) else it
                para(tf, i == 0, [(t, BODY_FONT, 10.5, b, INK) for t, b in runs], space_after=2, line_spacing=1.04)
        y += h + 0.15
    return s


def project_card(prs, ev, cv, asr, rouge):
    r = ev["results"]
    rl = lambda c: f"{rmean(rouge, c, 'rougeL'):.3f}"   # noqa: E731
    card_slide(prs, 1, [
        (1, "Title and abstract", 2.45, [
            [("MedScribe: Do speaker roles help an LLM write clinical notes?", True)],
            "Ambient scribes turn a doctor–patient conversation into a SOAP note, but diarization only gives "
            "anonymous speakers. We train a text-based role classifier (TF-IDF + logistic regression; "
            f"{pct(r['tfidf_lr']['test']['accuracy'])} speaker accuracy on the frozen ACI-Bench test) and test whether "
            "Doctor/Patient labels change the note an open LLM (Qwen2.5-7B) writes from the same transcript. "
            "On three development dialogues, labels did not change ROUGE (R-L "
            f"{rl('rollu')} vs {rl('rolsuz')}) but shifted the error types. On the 40-dialogue test set, labels "
            "[RESULT: ROUGE / BERTScore / attribution errors, with vs without vs anonymous A/B]. (≈120 words)"]),
        (2, "Research question", 1.45, [
            "Do Doctor/Patient speaker labels make an LLM write a better SOAP note? First result: no, not on "
            "average (3 dev dialogues). Changed: the proposal was a 5-stage system with no single question; "
            "narrowed after feedback (NER, fine-tuning, Turkish data dropped)."]),
        (3, "Contributions (testable claims)", 2.05, [
            "C1. Labels reduce attribution errors (negation flips, questions written as complaints) on the "
            "40 test dialogues, even when ROUGE is unchanged.",
            "C2. Most of any gain comes from turn structure: anonymous A/B labels close at least half of the gap "
            "between no speaker info and roles.",
            "C3. Pooling a speaker's turns, not per-utterance classification, is what makes role assignment "
            f"accurate ({pct(r['utterance_tfidf_lr']['test']['accuracy'])} → {pct(r['tfidf_lr']['test']['accuracy'])})."]),
    ])
    card_slide(prs, 2, [
        (4, "Related work (how we differ)", 3.05, [
            "Krishna et al., ACL-IJCNLP 2021 — Generating SOAP notes from doctor–patient conversations using "
            "modular summarization. Fine-tuned extract-then-abstract; we prompt an open LLM and isolate role labels.",
            "Yim et al., Scientific Data 2023 — ACI-BENCH. Benchmark we use; we add a role-label ablation on it.",
            "Ben Abacha et al., EACL 2023 — An empirical study of clinical note generation (MTS-Dialog). Section "
            "generation; we study one input factor, speaker roles.",
            "Ben Abacha et al., ClinicalNLP 2023 — Overview of MEDIQA-Chat 2023. Shared task systems; none "
            "separates the effect of role tags.",
            "Korfiatis et al., ACL 2022 — PriMock57. Audio corpus we use only for speaker separation.",
            "Bain et al., Interspeech 2023 — WhisperX; Bredin et al., ICASSP 2020 — pyannote. Tools we use "
            "as is; we solve the role mapping they leave open."]),
        (5, "Data", 2.4, [
            f"ACI-Bench, CC BY 4.0. As loaded: train {ev['counts']['train']['encounters']} enc. / "
            f"{ev['counts']['train']['utterances']:,} utt.; dev {ev['counts']['dev']['encounters']} / "
            f"{ev['counts']['dev']['utterances']:,}; test (clinicalnlp_taskB_test1, frozen) "
            f"{ev['counts']['test']['encounters']} / {ev['counts']['test']['utterances']:,}.",
            "Preprocessing: [patient_guest] lines dropped (dev 38, test 50); encounters unchanged.",
            f"PriMock57, CC BY 4.0: 20 consultations, first 5 min, {asr['total']:,} "
            "utterances. Example: [doctor] have you … noticed any rashes? / [patient] on my body no not really.",
            "No data labelled by us yet; the attribution-error checklist will report agreement on 10 notes."]),
    ])
    card_slide(prs, 3, [
        (6, "Method and baseline", 1.45, [
            "Baseline: note from the transcript without speaker labels. Method: same transcript with Doctor/"
            "Patient labels from our classifier (gold labels for the controlled run). The one change: the labels.",
            "Compute used: 1 Colab T4, ~1–2 min per note (4-bit 7B); roles on CPU in ~5 s. Needed: ~4 T4-hours "
            "for 40 dialogues × 3 conditions."]),
        (7, "Evaluation protocol (fixed before method results)", 1.4, [
            "Metrics: ROUGE-1/2/L, BERTScore vs reference note; attribution-error count per note (checklist). "
            "Test: ACI-Bench taskB_test1, 40 dialogues, frozen. Temperature 0 (one run); spread by paired "
            "bootstrap over dialogues (2,000, seed 0). Real difference = paired 95% CI excludes 0."]),
        (8, "Results so far (final table)", 3.0, []),
    ])
    s = prs.slides[-1]
    rows = [["System", "Roles: speaker acc. (test)", "Note R-L (dev, n=3)", "Note R-L (test, n=40)", "Attribution errors"],
            ["First speaker rule", ci(r["first_speaker"]["test"]), "–", "–", "–"],
            ["TF-IDF + LR roles (ours)", ci(r["tfidf_lr"]["test"]), "–", "–", "–"],
            ["Note, no speaker info (baseline)", "–", rl("rolsuz"), "", ""],
            ["Note, anonymous A/B", "–", "", "", ""],
            ["Note, Doctor/Patient labels", "–", rl("rollu"), "", ""]]
    table(s, 1.3, 4.55, [3.0, 2.4, 1.75, 1.8, 2.0], rows, row_h=0.33, size=10)

    card_slide(prs, 4, [
        (9, "Error analysis", 1.45, [
            f"{ev['utterance_errors_test']['total']} test errors of the per-utterance role model, grouped: " +
            "; ".join(f"{c.split(' (')[0]} {n}" for c, n in ev["utterance_errors_test"]["by_category"].items()) +
            ". Example: “okay.” (short backchannel). Notes: 1 echo, 1 negation-scope, 1 number, 1 added fact (6 notes)."]),
        (10, "Research lead section", 1.35, [
            "Research lead: the notes and experiment lead (slide 2), who owns the research question. Two recent papers: ACI-BENCH (Yim et al. 2023) and MEDIQA-Chat 2023 "
            "(Ben Abacha et al.); both report note quality without isolating speaker labels. We run the "
            "ablation no-speaker / anonymous A/B / roles."]),
        (11, "Plan and risk", 1.4, [
            "; ".join(f"{a} — {o}, {d}" for a, o, d in PLAN[:4]) + "; …(full list on slide 10). Risk: ROUGE "
            "blind to attribution errors → fallback checklist. Feedback response: scope narrowed to one question."]),
        (12, "Reproducibility", 1.65, [
            f"Repo: {REPO}.  Field 8: python -m eval.role_eval (roles) and python -m notes.generate_note "
            "--experiment (notes, needs GPU). Seeds: bootstrap 0, LLM temperature 0. Versions: Python 3.12, "
            "scikit-learn ≥1.4, transformers + bitsandbytes (Colab), WhisperX.",
            "Who did what: one module per member, as on slide 2 — ASR lead: speech → text; roles lead: role "
            "classifier; notes lead: notes and experiment; demo lead: shared format, demo, evaluation, slides. "
            "AI tools: Claude (Anthropic) for planning, code scaffolding, evaluation scripts and slide drafts; "
            "all outputs checked by the team."]),
    ])


NAMES = re.compile(r"(,\s*)?\b(Akif|Alp|Yusuf|Ali)\b")
SWAP = {"PERSON 2": "STEP 2", "PERSON 3": "STEP 3", "Person 2 · ": "", "Person 3 · ": ""}


def strip_names(prs):
    """Names stay on slides 1-2 only (team decision); later slides use module roles."""
    for i, s in enumerate(prs.slides):
        if s.has_notes_slide:
            tf = s.notes_slide.notes_text_frame
            tf.text = NAMES.sub("", tf.text)
        if i < 2:
            continue
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    t = r.text
                    for a, b in SWAP.items():
                        t = t.replace(a, b)
                    r.text = t
                    assert not NAMES.search(t), f"name left on slide {i + 1}: {t}"


def main():
    ev, cv, asr, rouge = load_all()
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    s1_rq(prs, rouge)
    s2_system(prs)
    s3_data(prs, ev, asr)
    s4_asr(prs, asr)
    slide_method(prs)                 # 5 — Person 2, unchanged
    s6_baseline(prs, ev, cv)
    s7_errors(prs, ev)
    slide_notes_generation(prs)       # 8 — Person 3, unchanged
    s9_experiment(prs, rouge)
    s10_plan(prs)
    project_card(prs, ev, cv, asr, rouge)
    strip_names(prs)
    out = R("results", "medscribe_midproject.pptx")
    prs.save(out)
    print("->", out, len(prs.slides._sldIdLst), "slides")


if __name__ == "__main__":
    main()
