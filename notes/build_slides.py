"""Person 3 presentation slides (7 and 8) — project plan section 5.

Produces: results/kisi3_slides.pptx  (2 slides, 16:9)
It also audits every text box against real font metrics for overflow
(LibreOffice/PowerPoint automation is unavailable in this environment).

    python notes/build_slides.py
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import ImageFont

# ---------------------------------------------------------------- palette
INK = RGBColor(0x0F, 0x2A, 0x2E)
TEAL = RGBColor(0x02, 0x80, 0x90)
TEAL2 = RGBColor(0x00, 0xA8, 0x96)
MINT = RGBColor(0x02, 0xC3, 0x9A)
MUTED = RGBColor(0x5F, 0x7A, 0x7E)
BG = RGBColor(0xF6, 0xFA, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xE6, 0xF3, 0xF3)

TITLE_FONT = "Georgia"
BODY_FONT = "Arial"

FONT_FILES = {
    "Georgia": "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "Georgia-Bold": "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "Arial": "/System/Library/Fonts/Supplemental/Arial.ttf",
    "Arial-Bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
}

EMU_IN = 914400


def _font(name, size, bold=False):
    key = name + ("-Bold" if bold else "")
    path = FONT_FILES.get(key, FONT_FILES["Arial"])
    try:
        return ImageFont.truetype(path, int(size))
    except OSError:
        return ImageFont.truetype(FONT_FILES["Arial"], int(size))


def measure(text, font_name, size, bold=False):
    """Width of the text in points."""
    return _font(font_name, size, bold).getlength(text)


def wrap_lines(text, font_name, size, bold, width_pt):
    """Greedy line wrapping; returns the line count."""
    words = text.split()
    if not words:
        return 1
    lines, cur = 1, ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(trial, font_name, size, bold) <= width_pt:
            cur = trial
        else:
            lines += 1
            cur = w
    return lines


# ---------------------------------------------------------------- helpers
def rect(slide, x, y, w, h, fill=None, line=None, radius=None, line_w=1.0):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius:
        s.adjustments[0] = radius
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    return tb


def para(tf, first, runs, align=PP_ALIGN.LEFT, space_after=0, space_before=0,
         line_spacing=1.05):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    p.line_spacing = line_spacing
    for text, name, size, bold, color in runs:
        r = p.add_run()
        r.text = text
        r.font.name = name
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
    return p


# ---------------------------------------------------------------- slides
def slide_notes_generation(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=BG)
    rect(s, 0, 0, 0.13, 7.5, fill=TEAL)          # motif: left edge bar

    tb = textbox(s, 0.55, 0.42, 8.0, 0.3)
    para(tb.text_frame, True, [("PERSON 3  ·  NOTE GENERATION", BODY_FONT, 11, True, TEAL)])

    tb = textbox(s, 0.55, 0.72, 7.6, 0.92)
    para(tb.text_frame, True,
         [("SOAP notes from a transcript", TITLE_FONT, 32, True, INK)], line_spacing=0.95)

    tb = textbox(s, 0.55, 1.70, 6.9, 0.55)
    para(tb.text_frame, True,
         [("Qwen2.5-7B-Instruct · 4-bit · temperature 0 · strict JSON output",
           BODY_FONT, 12.5, False, MUTED)])

    steps = [
        ("01", "Data", "3 ACI-Bench dialogues → shared JSON; 25–26 utterances, check_format clean."),
        ("02", "Transcript", "With roles the lines read \"Doctor: … / Patient: …\"; without roles, plain text only."),
        ("03", "Prompt", "One frozen prompt; the model may use only what the transcript states."),
        ("04", "Output", "JSON keyed S / O / A / P, so each section can be checked on its own."),
    ]
    y = 2.52
    for num, head, desc in steps:
        chip = rect(s, 0.55, y, 0.36, 0.36, fill=TEAL, radius=0.5)
        ctf = chip.text_frame
        ctf.margin_left = ctf.margin_right = 0
        ctf.margin_top = ctf.margin_bottom = 0
        ctf.vertical_anchor = MSO_ANCHOR.MIDDLE
        para(ctf, True, [(num, BODY_FONT, 9.5, True, WHITE)], align=PP_ALIGN.CENTER)

        tb = textbox(s, 1.06, y - 0.07, 5.75, 0.82)
        para(tb.text_frame, True, [(head + "   ", BODY_FONT, 13.5, True, INK),
                                   (desc, BODY_FONT, 11, False, MUTED)],
             line_spacing=1.08)
        y += 0.88

    # right card: two rules from the prompt
    rect(s, 7.45, 2.32, 5.3, 3.55, fill=WHITE, line=SOFT, radius=0.06, line_w=1.25)
    tb = textbox(s, 7.65, 2.5, 4.9, 0.3)
    para(tb.text_frame, True, [("TWO RULES FROM THE FROZEN PROMPT", BODY_FONT, 10.5, True, TEAL2)])

    rules = [
        ("“Negation matters. If the patient denies a symptom, record it as "
         "denied — never as present.”", "Negation"),
        ("“Do not turn the doctor’s questions into patient complaints. "
         "A question is not a symptom.”", "Question ≠ complaint"),
    ]
    ry = 2.9
    for quote, tag in rules:
        rect(s, 7.65, ry, 0.045, 1.32, fill=MINT)
        tb = textbox(s, 7.82, ry - 0.02, 4.6, 1.3)
        para(tb.text_frame, True, [(quote, BODY_FONT, 11.5, False, INK)], line_spacing=1.1)
        para(tb.text_frame, False, [(tag, BODY_FONT, 9.5, True, MUTED)],
             space_before=4)
        ry += 1.5

    s.notes_slide.notes_text_frame.text = (
        "SPEAKER NOTES — slide 7 (~60 s)\n"
        "1) 'There is no training in note generation; we steer an off-the-shelf open model "
        "with a prompt.'\n"
        "2) 'The input is the shared JSON you just saw: a role-labelled transcript.'\n"
        "3) 'We froze a single prompt at temperature 0. The output is JSON keyed S/O/A/P, "
        "so we can inspect every section separately.'\n"
        "4) 'Two critical rules in the prompt: keep negation, and never turn the doctor's "
        "question into a patient complaint.'\n"
        "5) 'The model runs 4-bit on a T4, and the demo uses exactly this code.'\n"
        "Timing: 4 steps x ~10 s plus one closing sentence.")

    # bottom statistics
    stats = [("3", "dialogues"), ("2", "conditions"), ("6", "notes"), ("0", "training")]
    x = 0.55
    for num, label in stats:
        tb = textbox(s, x, 6.55, 2.9, 0.55)
        para(tb.text_frame, True, [(num + "  ", TITLE_FONT, 26, True, TEAL),
                                   (label, BODY_FONT, 11.5, False, MUTED)])
        x += 3.15
    return s


def slide_experiment(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=BG)
    rect(s, 0, 0, 0.13, 7.5, fill=TEAL)

    tb = textbox(s, 0.55, 0.42, 8.0, 0.3)
    para(tb.text_frame, True, [("PERSON 3  ·  FIRST EXPERIMENT", BODY_FONT, 11, True, TEAL)])

    tb = textbox(s, 0.55, 0.72, 11.5, 0.75)
    para(tb.text_frame, True, [("With roles vs without: where does it break?",
                                TITLE_FONT, 32, True, INK)])

    # two condition cards
    cards = [
        (0.55, "With roles", "labelled · gold_role · simplified", [
            "Doctor: have you noticed any rashes?",
            "Patient: on my body no not really",
            "Doctor: okay, mainly underneath the scalp",
        ], TEAL),
        (6.95, "Without roles", "no labels · text only", [
            "have you noticed any rashes?",
            "on my body no not really",
            "okay, mainly underneath the scalp",
        ], MUTED),
    ]
    for cx, head, sub, lines, color in cards:
        rect(s, cx, 1.72, 5.82, 2.62, fill=WHITE, line=SOFT, radius=0.05, line_w=1.25)
        rect(s, cx, 1.72, 0.05, 2.62, fill=color)
        tb = textbox(s, cx + 0.2, 1.85, 5.3, 0.35)
        para(tb.text_frame, True, [(head, BODY_FONT, 15, True, INK),
                                   ("   " + sub, BODY_FONT, 9.5, False, MUTED)])
        tb = textbox(s, cx + 0.2, 2.32, 5.45, 1.85)
        tf = tb.text_frame
        for i, line in enumerate(lines):
            para(tf, i == 0, [(line, "Courier New", 10.5, False, INK)],
                 line_spacing=1.25, space_after=2)

    # finding band
    rect(s, 0.55, 4.62, 12.23, 2.28, fill=WHITE, line=SOFT, radius=0.04, line_w=1.25)
    rect(s, 0.55, 4.62, 0.05, 2.28, fill=MINT)

    tb = textbox(s, 0.8, 4.76, 7.5, 0.32)
    para(tb.text_frame, True, [("EXPECTED RISK: LOST NEGATION",
                                BODY_FONT, 10.5, True, TEAL2)])

    tb = textbox(s, 0.8, 5.08, 7.6, 1.66)
    tf = tb.text_frame
    para(tf, True, [("aci_002 — the patient denies a rash; the reference note ", BODY_FONT, 11.5, False, INK),
                    ("“Skin: Denies any rashes.”", BODY_FONT, 11.5, True, INK)],
             line_spacing=1.15)
    para(tf, False, [("Once the labels are gone we expect the model to lose track of whose "
                      "“no, not really” it is and record the finding as present.",
                      BODY_FONT, 11.5, False, MUTED)], space_before=5, line_spacing=1.15)
    para(tf, False, [("compare_notes.py flags this automatically: “denies X” in the "
                      "reference → X without negation in the note.",
                      BODY_FONT, 10.5, False, MUTED)], space_before=5, line_spacing=1.15)

    # result box (filled in after the Colab run)
    rect(s, 8.72, 4.86, 3.85, 1.5, fill=SOFT, line=TEAL2, radius=0.05, line_w=1.0)
    tb = textbox(s, 8.88, 4.96, 3.55, 1.3)
    tf = tb.text_frame
    para(tf, True, [("RESULT", BODY_FONT, 9.5, True, TEAL)])
    para(tf, False, [("Fill in after the Colab run:", BODY_FONT, 9.5, False, MUTED)],
         space_before=2)
    para(tf, False, [("negation flags", BODY_FONT, 10, False, INK)],
         space_before=3)
    para(tf, False, [("rollu  __ / 3      rolsuz  __ / 3",
                      BODY_FONT, 10, True, INK)], space_before=1)
    para(tf, False, [("no difference is a finding too", BODY_FONT, 8.5, False, MUTED)],
         space_before=2)

    s.notes_slide.notes_text_frame.text = (
        "SPEAKER NOTES — slide 8 (~60 s)\n"
        "1) 'We gave the same dialogue in two conditions: with roles, meaning Doctor/Patient "
        "labels, and without roles, meaning plain unlabelled text.'\n"
        "2) 'The transcript is the only thing that changes; prompt and model stay the same. "
        "That is what makes the difference measurable.'\n"
        "3) 'In aci_002 the patient clearly denies a rash, and the reference note records "
        "'Denies any rashes'.'\n"
        "4) 'Without labels, the failure we expect is that this negation gets lost, so the "
        "note reports the rash as present.'\n"
        "5) 'We do not search for that by hand; compare_notes.py extracts denies/no patterns "
        "from the reference and flags them when they appear without a negation.'\n"
        "6) 'I paste the numbers into the result box from the Colab output.'")

    tb = textbox(s, 0.55, 7.02, 9.0, 0.3)
    para(tb.text_frame, True, [("Person 3 · SOAP notes and experiment · MedScribe",
                                BODY_FONT, 8.5, False, MUTED)])
    return s


# ---------------------------------------------------------------- audit
def audit(prs):
    """Per text box: overflow risk, and whether it leaves the slide."""
    issues = []
    for idx, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            x, y = sh.left / EMU_IN, sh.top / EMU_IN
            w, h = sh.width / EMU_IN, sh.height / EMU_IN
            if x < 0.15 or y < 0.15 or x + w > 13.33 - 0.15 or y + h > 7.5 - 0.1:
                issues.append(f"slide {idx}: box too close to the slide edge ({x:.2f},{y:.2f},"
                              f"{w:.2f}x{h:.2f})")
            need = 0.0
            for p in sh.text_frame.paragraphs:
                if not p.runs:
                    continue
                size = max((r.font.size.pt if r.font.size else 12) for r in p.runs)
                bold = any(r.font.bold for r in p.runs)
                fname = p.runs[0].font.name or "Arial"
                text = "".join(r.text for r in p.runs)
                avail = (w - 0.16) * 72
                n = wrap_lines(text, fname, size, bold, avail)
                ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
                need += n * size * 1.2 * ls
                if p.space_before:
                    need += p.space_before.pt
                if p.space_after:
                    need += p.space_after.pt
            need_in = need / 72 + 0.04
            if need_in > h + 0.02:
                issues.append(f"slide {idx}: OVERFLOW risk — box {h:.2f}\" / needs "
                              f"{need_in:.2f}\"  [{sh.text_frame.text[:52]!r}]")
    return issues


def check_overlaps(prs):
    """Text boxes overlapping each other (text inside cards included)."""
    problems = []
    for idx, slide in enumerate(prs.slides, 1):
        boxes = [(sh.left / EMU_IN, sh.top / EMU_IN, sh.width / EMU_IN, sh.height / EMU_IN,
                  sh) for sh in slide.shapes if sh.has_text_frame
                 and sh.text_frame.text.strip()]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ax, ay, aw, ah, _ = boxes[i]
                bx, by, bw, bh, _ = boxes[j]
                ox = min(ax + aw, bx + bw) - max(ax, bx)
                oy = min(ay + ah, by + bh) - max(ay, by)
                if ox > 0.05 and oy > 0.05:
                    problems.append(f"slide {idx}: text boxes overlap "
                                    f"({ox:.2f}x{oy:.2f} in)")
    return problems


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide_notes_generation(prs)
    slide_experiment(prs)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "results", "kisi3_slides.pptx")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)

    issues = audit(prs)
    overlaps = check_overlaps(prs)
    print(f"-> {out} ({os.path.getsize(out)/1024:.0f} KB, {len(prs.slides._sldIdLst)} slides)")
    print(f"overflow audit: {len(issues)} issues")
    for i in issues:
        print("  !", i)
    print(f"overlap audit: {len(overlaps)} issues")
    for o in sorted(set(overlaps)):
        print("  !", o)


if __name__ == "__main__":
    main()
