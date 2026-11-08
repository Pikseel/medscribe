"""Kişi 3 sunum slaytları (7 ve 8) — Proje Planı Bölüm 5 slayt planı.

Üretir: notes/kisi3_slaytlar.pptx  (2 slayt, 16:9)
Ayrıca her metin kutusu için gerçek font metrikleriyle taşma denetimi yapar
(LibreOffice/PowerPoint otomasyonu bu ortamda kapalı olduğu için).

    python notes/build_slides.py
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import ImageFont

# ---------------------------------------------------------------- palet
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
    """Metnin genişliği (punto)."""
    return _font(font_name, size, bold).getlength(text)


def wrap_lines(text, font_name, size, bold, width_pt):
    """Açgözlü satır sarma; kaç satır ettiğini döndürür."""
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


# ---------------------------------------------------------------- yardımcılar
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


# ---------------------------------------------------------------- slaytlar
def slide_notes_generation(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=BG)
    rect(s, 0, 0, 0.13, 7.5, fill=TEAL)          # motif: sol kenar şeridi

    tb = textbox(s, 0.55, 0.42, 8.0, 0.3)
    para(tb.text_frame, True, [("KİŞİ 3  ·  NOT ÜRETİMİ", BODY_FONT, 11, True, TEAL)])

    tb = textbox(s, 0.55, 0.72, 7.6, 0.92)
    para(tb.text_frame, True,
         [("Transkriptten SOAP notu", TITLE_FONT, 32, True, INK)], line_spacing=0.95)

    tb = textbox(s, 0.55, 1.70, 6.9, 0.55)
    para(tb.text_frame, True,
         [("Qwen2.5-7B-Instruct · 4-bit · temperature 0 · çıktı katı JSON",
           BODY_FONT, 12.5, False, MUTED)])

    steps = [
        ("01", "Veri", "ACI-Bench'ten 3 diyalog → ortak JSON; 25–26 cümle, check_format temiz."),
        ("02", "Transkript", "Rollü koşulda \"Doctor: … / Patient: …\", rolsüz koşulda yalnız cümle metni."),
        ("03", "İstem", "Tek ve donmuş istem; modele yalnız transkriptteki bilgiyi kullanması söylenir."),
        ("04", "Çıktı", "S / O / A / P anahtarlı JSON; her alan tek tek denetlenebilir."),
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

    # sağ kart: istemden iki kural
    card = rect(s, 7.45, 2.32, 5.3, 3.55, fill=WHITE, line=SOFT, radius=0.06, line_w=1.25)
    tb = textbox(s, 7.65, 2.5, 4.9, 0.3)
    para(tb.text_frame, True, [("DONMUŞ İSTEMDEN İKİ KURAL", BODY_FONT, 10.5, True, TEAL2)])

    rules = [
        ("“Negation matters. If the patient denies a symptom, record it as "
         "denied — never as present.”", "Olumsuzlama"),
        ("“Do not turn the doctor’s questions into patient complaints. "
         "A question is not a symptom.”", "Soru ≠ şikâyet"),
    ]
    ry = 2.9
    for quote, tag in rules:
        bar = rect(s, 7.65, ry, 0.045, 1.32, fill=MINT)
        tb = textbox(s, 7.82, ry - 0.02, 4.6, 1.3)
        para(tb.text_frame, True, [(quote, BODY_FONT, 11.5, False, INK)], line_spacing=1.1)
        para(tb.text_frame, False, [(tag, BODY_FONT, 9.5, True, MUTED)],
             space_before=4)
        ry += 1.5

    s.notes_slide.notes_text_frame.text = (
        "KONUŞMACI NOTU — slayt 7 (~60 sn)\n"
        "1) 'Not üretiminde eğitim yok; hazır bir açık modeli istemle yönlendiriyoruz.'\n"
        "2) 'Girdi, az önce gördüğünüz ortak JSON: rol etiketli transkript.'\n"
        "3) 'Tek bir istem dondurduk, temperature 0. Çıktı S/O/A/P anahtarlı JSON; "
        "böylece her alanı ayrı ayrı denetleyebiliyoruz.'\n"
        "4) 'İstemdeki iki kritik kural: olumsuzlamayı koru, doktorun sorusunu "
        "hastanın şikâyeti gibi yazma.'\n"
        "5) 'Model 4-bit, T4'te çalışıyor; demoda aynı kod kullanılıyor.'\n"
        "Süre: 4 adım x ~10 sn + 1 cümle kapanış.")

    # alt istatistikler
    stats = [("3", "diyalog"), ("2", "koşul"), ("6", "not"), ("0", "eğitim")]
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
    para(tb.text_frame, True, [("KİŞİ 3  ·  İLK DENEY", BODY_FONT, 11, True, TEAL)])

    tb = textbox(s, 0.55, 0.72, 9.5, 0.75)
    para(tb.text_frame, True, [("Rollü vs rolsüz: fark nerede?", TITLE_FONT, 32, True, INK)])

    # iki koşul kartı
    cards = [
        (0.55, "Rollü", "etiketli · gold_role · sadeleştirilmiş", [
            "Doctor: have you noticed any rashes?",
            "Patient: on my body no not really",
            "Doctor: okay, mainly underneath the scalp",
        ], TEAL),
        (6.95, "Rolsüz", "etiket yok · yalnız cümle metni", [
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

    # bulgu bandı
    rect(s, 0.55, 4.62, 12.23, 2.28, fill=WHITE, line=SOFT, radius=0.04, line_w=1.25)
    rect(s, 0.55, 4.62, 0.05, 2.28, fill=MINT)

    tb = textbox(s, 0.8, 4.76, 7.5, 0.32)
    para(tb.text_frame, True, [("BEKLENEN RİSK: OLUMSUZLAMANIN KAYBI",
                                BODY_FONT, 10.5, True, TEAL2)])

    tb = textbox(s, 0.8, 5.08, 7.6, 1.66)
    tf = tb.text_frame
    para(tf, True, [("aci_002 — hasta döküntüyü reddediyor; referans not ", BODY_FONT, 11.5, False, INK),
                    ("“Skin: Denies any rashes.”", BODY_FONT, 11.5, True, INK),
                    (" diyor.", BODY_FONT, 11.5, False, INK)], line_spacing=1.15)
    para(tf, False, [("Etiket kalkınca modelin “no, not really” ifadesini kime ait "
                      "olduğunu kestirememesi ve bulguyu olumlu yazması beklenir.",
                      BODY_FONT, 11.5, False, MUTED)], space_before=5, line_spacing=1.15)
    para(tf, False, [("compare_notes.py bunu otomatik bayraklıyor: referansta "
                      "“denies X” → notta olumsuzlamasız X.",
                      BODY_FONT, 10.5, False, MUTED)], space_before=5, line_spacing=1.15)

    # sonuç kutusu (Colab çıktısıyla doldurulacak)
    box = rect(s, 8.72, 4.86, 3.85, 1.5, fill=SOFT, line=TEAL2, radius=0.05, line_w=1.0)
    tb = textbox(s, 8.88, 4.96, 3.55, 1.3)
    tf = tb.text_frame
    para(tf, True, [("SONUÇ", BODY_FONT, 9.5, True, TEAL)])
    para(tf, False, [("Colab çalışınca doldur:", BODY_FONT, 9.5, False, MUTED)],
         space_before=2)
    para(tf, False, [("olumsuzlama bayrağı", BODY_FONT, 10, False, INK)],
         space_before=3)
    para(tf, False, [("rollü  __ / 3      rolsüz  __ / 3",
                      BODY_FONT, 10, True, INK)], space_before=1)
    para(tf, False, [("fark yoksa bu da bulgu", BODY_FONT, 8.5, False, MUTED)],
         space_before=2)

    s.notes_slide.notes_text_frame.text = (
        "KONUŞMACI NOTU — slayt 8 (~60 sn)\n"
        "1) 'Aynı diyaloğu iki koşulda verdik: rollü, yani Doctor/Patient etiketli; "
        "ve rolsüz, yani etiketsiz düz metin.'\n"
        "2) 'Tek değişen şey transkript; istem ve model aynı. Farkı ölçülebilir kılan bu.'\n"
        "3) 'aci_002'de hasta döküntüyü açıkça reddediyor; referans not bunu "
        "'Denies any rashes' diye yazmış.'\n"
        "4) 'Rolsüz koşulda beklediğimiz hata: bu olumsuzlamanın kaybolması, yani "
        "notta döküntünün olumlu görünmesi.'\n"
        "5) 'Bunu elle aramıyoruz; compare_notes.py referanstaki denies/no kalıplarını "
        "çıkarıp notta olumsuzlamasız geçenleri bayraklıyor.'\n"
        "6) 'Sonuç kutusundaki sayıları Colab çıktısından yapıştırıyorum.'")

    tb = textbox(s, 0.55, 7.02, 9.0, 0.3)
    para(tb.text_frame, True, [("Kişi 3 · SOAP notu ve deney · MedScribe",
                                BODY_FONT, 8.5, False, MUTED)])
    return s


# ---------------------------------------------------------------- denetim
def audit(prs):
    """Her metin kutusu için taşma / taşma riski / slayt dışına çıkma denetimi."""
    issues = []
    for idx, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            x, y = sh.left / EMU_IN, sh.top / EMU_IN
            w, h = sh.width / EMU_IN, sh.height / EMU_IN
            if x < 0.15 or y < 0.15 or x + w > 13.33 - 0.15 or y + h > 7.5 - 0.1:
                issues.append(f"slayt {idx}: kutu slayt dışına yakın ({x:.2f},{y:.2f},"
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
                issues.append(f"slayt {idx}: TAŞMA riski — kutu {h:.2f}\" / gereken "
                              f"{need_in:.2f}\"  [{sh.text_frame.text[:52]!r}]")
    return issues


def check_overlaps(prs):
    """Metin kutularının birbirinin üstüne binmesi (kart içi metinler hariç)."""
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
                    problems.append(f"slayt {idx}: metin kutuları çakışıyor "
                                    f"({ox:.2f}x{oy:.2f} inç)")
    return problems


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide_notes_generation(prs)
    slide_experiment(prs)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "results", "kisi3_slaytlar.pptx")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    prs.save(out)

    issues = audit(prs)
    overlaps = check_overlaps(prs)
    print(f"-> {out} ({os.path.getsize(out)/1024:.0f} KB, {len(prs.slides.__iter__.__self__._sldIdLst)} slayt)")
    print(f"taşma denetimi: {len(issues)} sorun")
    for i in issues:
        print("  !", i)
    print(f"çakışma denetimi: {len(overlaps)} sorun")
    for o in sorted(set(overlaps)):
        print("  !", o)


if __name__ == "__main__":
    main()
