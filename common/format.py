"""Ortak JSON formatı kontrolü. Push etmeden önce her JSON dosyası bundan geçmeli."""
import json

ROLES = {"Doctor", "Patient", None}
TOP = ["dialogue_id", "source", "reference_note", "segments"]
SEG = ["id", "start", "end", "speaker", "gold_role", "role", "role_prob", "text"]
NOTE = ["dialogue_id", "condition", "model", "S", "O", "A", "P"]


def check_format(d):
    for k in TOP:
        assert k in d, f"eksik alan: {k}"
    assert d["segments"], "segments boş olamaz"
    for i, s in enumerate(d["segments"]):
        for k in SEG:
            assert k in s, f"cümle {i}: eksik alan {k}"
        assert s["id"] == i, f"cümle {i}: id sırası bozuk"
        assert s["gold_role"] in ROLES and s["role"] in ROLES, f"cümle {i}: geçersiz rol"
        assert s["role_prob"] is None or 0 <= s["role_prob"] <= 1, f"cümle {i}: role_prob 0-1 arası olmalı"
        assert isinstance(s["text"], str) and s["text"].strip(), f"cümle {i}: boş metin"
    return True


def check_note(n):
    for k in NOTE:
        assert k in n, f"not: eksik alan {k}"
    return True


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(d, path):
    check_format(d)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":  # python -m common.format dosya1.json dosya2.json ...
    import sys
    for p in sys.argv[1:]:
        check_format(load(p))
        print("OK", p)
