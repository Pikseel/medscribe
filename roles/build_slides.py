"""Build Person 2 role-assignment slides and a combined MedScribe deck.

Outputs:
  results/kisi2_slides.pptx      (3 Person 2 slides)
  results/medscribe_slides.pptx  (full interim deck with the Person 2 draft
                                   replaced by these 3 verified slides)

Run from the repository root::

    roles/.venv/bin/python -m roles.build_slides
"""

from __future__ import annotations

import os
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

from notes.build_slides import (
    BG,
    BODY_FONT,
    INK,
    MINT,
    MUTED,
    SOFT,
    TEAL,
    TEAL2,
    TITLE_FONT,
    WHITE,
    MSO_ANCHOR,
    PP_ALIGN,
    audit,
    check_overlaps,
    para,
    rect,
    textbox,
)


ROOT = Path(__file__).resolve().parents[1]
INTERIM_DECK = ROOT / "results" / "medscribe_interim.pptx"
PERSON2_DECK = ROOT / "results" / "kisi2_slides.pptx"
COMBINED_DECK = ROOT / "results" / "medscribe_slides.pptx"


def _base(prs, eyebrow, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, fill=BG)
    rect(slide, 0, 0, 0.13, 7.5, fill=TEAL)

    tb = textbox(slide, 0.55, 0.40, 8.5, 0.3)
    para(tb.text_frame, True, [(eyebrow, BODY_FONT, 11, True, TEAL)])
    tb = textbox(slide, 0.55, 0.70, 12.1, 0.72)
    para(tb.text_frame, True, [(title, TITLE_FONT, 30, True, INK)], line_spacing=0.95)
    tb = textbox(slide, 0.55, 1.42, 12.0, 0.38)
    para(tb.text_frame, True, [(subtitle, BODY_FONT, 11.5, False, MUTED)])
    return slide


def _footer(slide, text):
    tb = textbox(slide, 0.55, 7.10, 11.8, 0.22)
    para(tb.text_frame, True, [(text, BODY_FONT, 8.5, False, MUTED)])


def slide_method(prs):
    slide = _base(
        prs,
        "PERSON 2  ·  ROLE ASSIGNMENT",
        "Who is the doctor — without trusting A/B?",
        "Speaker-level TF–IDF + balanced Logistic Regression · English clinical dialogue",
    )

    steps = [
        ("01", "Group", "Join every utterance from the same speaker."),
        ("02", "Vectorise", "Word 1–2 grams + character 3–5 grams."),
        ("03", "Classify", "Estimate P(Doctor) from language, not speaker ID."),
        ("04", "Constrain", "For 2 speakers, assign exactly 1 Doctor + 1 Patient."),
    ]
    y = 1.98
    for num, head, desc in steps:
        chip = rect(slide, 0.55, y, 0.36, 0.36, fill=TEAL, radius=0.5)
        chip.text_frame.margin_left = chip.text_frame.margin_right = 0
        chip.text_frame.margin_top = chip.text_frame.margin_bottom = 0
        chip.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        para(
            chip.text_frame,
            True,
            [(num, BODY_FONT, 9.5, True, WHITE)],
            align=PP_ALIGN.CENTER,
        )
        tb = textbox(slide, 1.08, y - 0.07, 5.75, 0.68)
        para(
            tb.text_frame,
            True,
            [
                (head + "   ", BODY_FONT, 13.2, True, INK),
                (desc, BODY_FONT, 10.8, False, MUTED),
            ],
            line_spacing=1.05,
        )
        y += 0.86

    rect(slide, 7.22, 1.95, 5.55, 3.88, fill=WHITE, line=SOFT, radius=0.05, line_w=1.25)
    tb = textbox(slide, 7.48, 2.16, 4.95, 0.28)
    para(tb.text_frame, True, [("TRAINING DATA & FEATURES", BODY_FONT, 10.5, True, TEAL2)])

    facts = [
        ("67", "ACI-Bench encounters"),
        ("134", "speaker documents · 67 Doctor + 67 Patient"),
        ("9,782", "word TF–IDF features"),
        ("16,751", "character TF–IDF features"),
        ("26,533", "total sparse features"),
    ]
    fy = 2.56
    for number, label in facts:
        tb = textbox(slide, 7.52, fy, 4.75, 0.47)
        para(
            tb.text_frame,
            True,
            [
                (number.rjust(6) + "   ", "Courier New", 14, True, TEAL),
                (label, BODY_FONT, 10.7, False, INK),
            ],
        )
        fy += 0.56

    rect(slide, 7.48, 5.40, 4.96, 0.23, fill=SOFT)
    tb = textbox(slide, 7.56, 5.40, 4.78, 0.22, anchor=MSO_ANCHOR.MIDDLE)
    para(tb.text_frame, True, [("0 speaker-name features · 0 GPU required", BODY_FONT, 9.2, True, MUTED)])

    stats = [
        ("2", "roles"),
        ("1.11 MiB", "model"),
        ("2.15 ms", "median inference"),
        ("2,000", "max iterations"),
    ]
    x = 0.55
    for number, label in stats:
        tb = textbox(slide, x, 6.24, 2.95, 0.78)
        para(
            tb.text_frame,
            True,
            [
                (number + "  ", TITLE_FONT, 19, True, TEAL),
                (label, BODY_FONT, 9.2, False, MUTED),
            ],
        )
        x += 3.10

    slide.notes_slide.notes_text_frame.text = (
        "SPEAKER NOTES — Person 2 method (~60 s)\n"
        "1) We never use A/B or SPEAKER_00 as a feature; diarization labels are arbitrary.\n"
        "2) We concatenate all turns from one speaker, yielding 134 documents from 67 encounters.\n"
        "3) The representation has 9,782 word and 16,751 character TF-IDF features: 26,533 total.\n"
        "4) Balanced logistic regression outputs P(Doctor). For two speakers, odds are normalised so exactly one Doctor and one Patient are produced.\n"
        "5) The final model is 1.11 MiB and needs no GPU."
    )
    _footer(slide, "Person 2 · assign_roles(dialogue) → role + P(Doctor) · MedScribe")


def slide_evaluation(prs):
    slide = _base(
        prs,
        "PERSON 2  ·  EVALUATION",
        "One split says 100%; five folds say 92.53%",
        "Encounter-grouped evaluation: no consultation appears in both train and test",
    )

    rect(slide, 0.55, 1.95, 7.15, 4.70, fill=WHITE, line=SOFT, radius=0.05, line_w=1.25)
    tb = textbox(slide, 0.82, 2.15, 6.55, 0.3)
    para(tb.text_frame, True, [("5-FOLD GROUPED ACCURACY", BODY_FONT, 10.5, True, TEAL2)])

    scores = [92.86, 92.86, 100.00, 84.62, 92.31]
    base_y = 5.92
    chart_h = 3.05
    start_x = 1.05
    for idx, score in enumerate(scores, 1):
        x = start_x + (idx - 1) * 1.23
        height = chart_h * score / 100
        rect(slide, x, base_y - height, 0.68, height, fill=TEAL if idx != 3 else MINT, radius=0.04)
        tb = textbox(slide, x - 0.13, base_y - height - 0.32, 0.95, 0.25)
        para(tb.text_frame, True, [(f"{score:.2f}%", BODY_FONT, 9, True, INK)], align=PP_ALIGN.CENTER)
        tb = textbox(slide, x, 6.00, 0.68, 0.24)
        para(tb.text_frame, True, [(f"F{idx}", BODY_FONT, 9, True, MUTED)], align=PP_ALIGN.CENTER)

    rect(slide, 0.90, 6.34, 6.42, 0.05, fill=SOFT)
    tb = textbox(slide, 0.92, 6.41, 6.25, 0.20)
    para(tb.text_frame, True, [("Fold range: 84.62%–100.00% · 67 encounters total", BODY_FONT, 8.8, False, MUTED)])

    rect(slide, 8.00, 1.95, 4.78, 2.04, fill=SOFT, line=TEAL2, radius=0.05, line_w=1.0)
    tb = textbox(slide, 8.25, 2.18, 4.28, 0.30)
    para(tb.text_frame, True, [("PRIMARY RESULT", BODY_FONT, 10, True, TEAL)])
    tb = textbox(slide, 8.25, 2.48, 4.25, 0.75)
    para(tb.text_frame, True, [("92.53%", TITLE_FONT, 31, True, INK), ("  ± 4.87 pp", BODY_FONT, 12, True, MUTED)])
    tb = textbox(slide, 8.25, 3.23, 4.10, 0.42)
    para(tb.text_frame, True, [("Accuracy = Macro-F1 · speaker level", BODY_FONT, 10.5, False, MUTED)])

    rect(slide, 8.00, 4.22, 4.78, 2.43, fill=WHITE, line=SOFT, radius=0.05, line_w=1.25)
    tb = textbox(slide, 8.25, 4.42, 4.15, 0.30)
    para(tb.text_frame, True, [("20% HOLDOUT — SECONDARY", BODY_FONT, 10.2, True, TEAL2)])
    tb = textbox(slide, 8.25, 4.78, 4.20, 0.52)
    para(tb.text_frame, True, [("28/28 correct", TITLE_FONT, 22, True, INK), ("  · 100%", BODY_FONT, 11, True, TEAL)])
    tb = textbox(slide, 8.25, 5.35, 4.15, 0.36)
    para(tb.text_frame, True, [("14 Doctor → Doctor · 14 Patient → Patient", BODY_FONT, 9.8, False, INK)])
    tb = textbox(slide, 8.25, 5.76, 4.15, 0.60)
    para(
        tb.text_frame,
        True,
        [("Why not headline 100%?", BODY_FONT, 9.5, True, MUTED)],
    )
    para(
        tb.text_frame,
        False,
        [("Only 14 test encounters; one favourable split can overstate performance.", BODY_FONT, 9.3, False, MUTED)],
        space_before=2,
    )

    slide.notes_slide.notes_text_frame.text = (
        "SPEAKER NOTES — Person 2 evaluation (~60 s)\n"
        "1) Splitting is by encounter ID, not utterance, so the same consultation cannot leak into two folds.\n"
        "2) Fold accuracies are 92.86, 92.86, 100.00, 84.62 and 92.31 percent.\n"
        "3) The main result is therefore 92.53 percent with a population standard deviation of 4.87 percentage points. Macro-F1 is identical because the classes are balanced.\n"
        "4) A separate 20 percent holdout produced 28 of 28 correct: 14 doctors and 14 patients.\n"
        "5) We do not headline 100 percent because that test contains only 14 encounters; five folds are the more stable estimate."
    )
    _footer(slide, "Source: results/kisi2_role_metrics.json · split unit: encounter_id · evaluation unit: speaker")


def slide_integration(prs):
    slide = _base(
        prs,
        "PERSON 2  ·  ASR INTEGRATION",
        "From diarized ASR to 64 consistent labels",
        "Person 1 output · 175.06 s consultation · arbitrary SPEAKER_00 / SPEAKER_01 IDs",
    )

    stages = [
        ("ASR JSON", "64 segments\n2 speakers · 175.06 s"),
        ("AGGREGATE", "35 + 29 turns\n1 document / speaker"),
        ("CLASSIFY", "2.15 ms median\n2.46 ms p95"),
        ("WRITE BACK", "64/64 segments\nrole-consistent"),
    ]
    x = 0.55
    for idx, (head, body) in enumerate(stages):
        rect(slide, x, 2.02, 2.62, 1.48, fill=WHITE, line=SOFT, radius=0.05, line_w=1.25)
        tb = textbox(slide, x + 0.17, 2.22, 2.25, 0.26)
        para(tb.text_frame, True, [(head, BODY_FONT, 10, True, TEAL2)])
        tb = textbox(slide, x + 0.17, 2.58, 2.25, 0.62)
        lines = body.split("\n")
        para(tb.text_frame, True, [(lines[0], TITLE_FONT, 16, True, INK)])
        para(tb.text_frame, False, [(lines[1], BODY_FONT, 9.5, False, MUTED)], space_before=2)
        if idx < len(stages) - 1:
            tb = textbox(slide, x + 2.67, 2.40, 0.35, 0.65, anchor=MSO_ANCHOR.MIDDLE)
            para(tb.text_frame, True, [("→", BODY_FONT, 17, True, TEAL)], align=PP_ALIGN.CENTER)
        x += 3.08

    rect(slide, 0.55, 3.90, 7.22, 2.55, fill=WHITE, line=SOFT, radius=0.05, line_w=1.25)
    tb = textbox(slide, 0.80, 4.12, 6.75, 0.30)
    para(tb.text_frame, True, [("PERSON 1 ASR EXAMPLE — EXPECTED MAPPING RECOVERED", BODY_FONT, 10.2, True, TEAL2)])

    rows = [
        ("SPEAKER_00", "35 segments", "P(Doctor) 69.97%", "Doctor", TEAL),
        ("SPEAKER_01", "29 segments", "P(Doctor) 30.03%", "Patient", MUTED),
    ]
    ry = 4.58
    for speaker, count, prob, role, color in rows:
        rect(slide, 0.82, ry, 6.62, 0.66, fill=SOFT if role == "Doctor" else BG)
        tb = textbox(slide, 1.00, ry + 0.16, 6.05, 0.30)
        para(
            tb.text_frame,
            True,
            [
                (speaker + "   ", "Courier New", 10.5, True, INK),
                (count + "   ", BODY_FONT, 10, False, MUTED),
                (prob + "   ", BODY_FONT, 10, False, MUTED),
                ("→ " + role, BODY_FONT, 10.5, True, color),
            ],
        )
        ry += 0.78

    rect(slide, 8.05, 3.90, 4.73, 2.55, fill=SOFT, line=TEAL2, radius=0.05, line_w=1.0)
    tb = textbox(slide, 8.30, 4.14, 4.22, 0.30)
    para(tb.text_frame, True, [("WHAT COUNTS AS EVIDENCE?", BODY_FONT, 10.2, True, TEAL)])
    tb = textbox(slide, 8.30, 4.58, 4.05, 1.58)
    para(tb.text_frame, True, [("5-fold 92.53%", BODY_FONT, 15, True, INK), ("  → primary estimate", BODY_FONT, 9.5, False, MUTED)])
    para(tb.text_frame, False, [("ASR 2/2 speakers", BODY_FONT, 13, True, INK), ("  → integration check", BODY_FONT, 9.5, False, MUTED)], space_before=8)
    para(tb.text_frame, False, [("ACI examples 76/76", BODY_FONT, 13, True, INK), ("  → sanity only", BODY_FONT, 9.5, False, MUTED)], space_before=8)
    para(tb.text_frame, False, [("Those 76 segments were seen in final refit; they are not an independent accuracy score.", BODY_FONT, 8.8, False, MUTED)], space_before=5)

    slide.notes_slide.notes_text_frame.text = (
        "SPEAKER NOTES — Person 2 integration (~60 s)\n"
        "1) Person 1's ASR example contains 64 segments across 175.06 seconds: 35 from SPEAKER_00 and 29 from SPEAKER_01.\n"
        "2) The role module aggregates by speaker, predicts once per speaker, and writes one consistent role back to all 64 segments.\n"
        "3) It recovered the documented mapping: SPEAKER_00 is Doctor at 69.97 percent P(Doctor), and SPEAKER_01 is Patient at 30.03 percent.\n"
        "4) On 100 warm runs, median inference was 2.15 milliseconds and p95 was 2.46 milliseconds on this Mac, excluding model load.\n"
        "5) The 76 of 76 ACI project segments are only a sanity check because the final refit saw them. The honest headline remains grouped five-fold accuracy."
    )
    _footer(slide, "Benchmark: 100 warm CPU runs · Python 3.12 · excludes model load · no GPU")


def add_person2_slides(prs):
    slide_method(prs)
    slide_evaluation(prs)
    slide_integration(prs)


def _remove_slide(prs, index):
    """Remove one slide and its presentation relationship."""
    slide_id = prs.slides._sldIdLst[index]
    relationship_id = slide_id.rId
    prs.slides._sldIdLst.remove(slide_id)
    prs.part.drop_rel(relationship_id)


def _move_last_slides_to_index(prs, count, index):
    """Place newly appended slides at a zero-based position."""
    slide_ids = prs.slides._sldIdLst
    current = list(slide_ids)
    existing, appended = current[:-count], current[-count:]
    reordered = existing[:index] + appended + existing[index:]
    for slide_id in current:
        slide_ids.remove(slide_id)
    for slide_id in reordered:
        slide_ids.append(slide_id)


def _new_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def _save_and_report(prs, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)
    issues = audit(prs)
    overlaps = check_overlaps(prs)
    print(f"-> {path} ({os.path.getsize(path) / 1024:.0f} KB, {len(prs.slides)} slides)")
    print(f"   overflow audit: {len(issues)} · overlap audit: {len(overlaps)}")
    for issue in issues:
        print("   !", issue)
    for issue in sorted(set(overlaps)):
        print("   !", issue)


def main():
    person2 = _new_deck()
    add_person2_slides(person2)
    _save_and_report(person2, PERSON2_DECK)

    combined = Presentation(INTERIM_DECK)
    # Append first so python-pptx allocates slide12–14 without colliding with
    # the existing slide11 part, then remove/reorder the draft.
    add_person2_slides(combined)
    _remove_slide(combined, 5)  # Replace the single draft Person 2 slide.
    _move_last_slides_to_index(combined, 3, 5)
    _save_and_report(combined, COMBINED_DECK)


if __name__ == "__main__":
    main()
