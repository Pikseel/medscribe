"""Demo boru hattı: metin -> ortak format -> assign_roles -> generate_note.
Gerçek modüller hazırsa onları, değilse common/mocks.py'yi kullanır (hangisi kullanıldığı yazdırılır)."""
import re

try:
    from roles.assign_roles import assign_roles
    ROLES_MODULE = "gerçek (roles/assign_roles.py)"
except ImportError as e:
    from common.mocks import assign_roles
    ROLES_MODULE = f"SAHTE ({e})"

try:
    from notes.generate_note import generate_note
    NOTES_MODULE = "gerçek (notes/generate_note.py)"
except ImportError as e:
    from common.mocks import generate_note
    NOTES_MODULE = f"SAHTE ({e})"

from common.format import check_format, check_note

LINE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*:\s*(.+)$")


def parse_text(text, dialogue_id="demo_001"):
    """'A: ...' / 'B: ...' satırlarını ortak formata çevirir. Etiketsiz satır bir öncekine eklenir."""
    segs = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        m = LINE.match(raw)
        if m:
            segs.append({"id": len(segs), "start": None, "end": None, "speaker": m.group(1).upper(),
                         "gold_role": None, "role": None, "role_prob": None, "text": m.group(2).strip()})
        elif segs:
            segs[-1]["text"] += " " + raw.strip()
        else:
            raise ValueError("İlk satır 'A: ...' biçiminde olmalı")
    if not segs:
        raise ValueError("Boş metin")
    d = {"dialogue_id": dialogue_id, "source": "demo", "reference_note": None, "segments": segs}
    check_format(d)
    return d


def run(dialogue):
    d = assign_roles(dialogue)
    check_format(d)
    note = generate_note(d, "role")
    check_note(note)
    return d, note


if __name__ == "__main__":
    print("rol modülü:", ROLES_MODULE, "| not modülü:", NOTES_MODULE)
    d, n = run(parse_text(open("app/demo_metin.txt", encoding="utf-8").read()))
    for s in d["segments"]:
        print(f'{s["role"]:7} {s["role_prob"]:.2f}  {s["text"]}')
    print(n)
