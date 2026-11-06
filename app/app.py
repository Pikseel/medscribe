"""Gradio demosu. Repo kökünden çalıştır:  python -m app.app   (Colab'da share=True link verir)"""
import html, json
import gradio as gr
from app.pipeline import parse_text, run, ROLES_MODULE, NOTES_MODULE

COLORS = {"Doctor": "#dbeafe", "Patient": "#dcfce7", None: "#f3f4f6"}
LABEL = {"Doctor": "Doktor", "Patient": "Hasta", None: "?"}
ORNEK = open("app/demo_metin.txt", encoding="utf-8").read()


def render_transcript(d):
    rows = []
    for s in d["segments"]:
        p = "" if s["role_prob"] is None else f'{s["role_prob"]:.2f}'
        rows.append(
            f'<div style="background:{COLORS[s["role"]]};padding:6px 10px;margin:4px 0;border-radius:6px;color:#111">'
            f'<b>{LABEL[s["role"]]}</b> <small>({s["speaker"]}, P(doktor)={p})</small><br>{html.escape(s["text"])}</div>')
    return "".join(rows)


def render_note(n):
    names = {"S": "Subjective", "O": "Objective", "A": "Assessment", "P": "Plan"}
    return "\n\n".join(f"### {k} – {names[k]}\n{n[k]}" for k in "SOAP") + f"\n\n<small>model: {n['model']}</small>"


def predict(text):
    try:
        d, note = run(parse_text(text))
    except Exception as e:
        raise gr.Error(str(e))
    return render_transcript(d), render_note(note), json.dumps(d, ensure_ascii=False, indent=2)


with gr.Blocks(title="MedScribe") as demo:
    gr.Markdown("# MedScribe\nDoktor–hasta konuşmasından rol tespiti ve SOAP notu"
                f"\n<small>rol modülü: {ROLES_MODULE} · not modülü: {NOTES_MODULE}</small>")
    with gr.Row():
        with gr.Column():
            inp = gr.Textbox(label="Konuşma (her satır 'A: ...' veya 'B: ...')", value=ORNEK, lines=14)
            gr.Audio(label="Ses (yakında)", type="filepath", interactive=False)
            btn = gr.Button("Çalıştır", variant="primary")
        with gr.Column():
            tr = gr.HTML(label="Rollü transkript")
            note = gr.Markdown()
    with gr.Accordion("Ham JSON", open=False):
        raw = gr.Code(language="json")
    btn.click(predict, inp, [tr, note, raw])

if __name__ == "__main__":
    demo.launch(share=True)
