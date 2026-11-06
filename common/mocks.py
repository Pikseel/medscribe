"""Sahte fonksiyonlar. Gerçek modül hazır olana kadar demo ve testler bunlarla çalışır."""


def assign_roles(d):  # SAHTE: A / SPEAKER_00 = doktor
    for s in d["segments"]:
        doc = s["speaker"] in ("A", "SPEAKER_00")
        s["role"] = "Doctor" if doc else "Patient"
        s["role_prob"] = 1.0 if doc else 0.0
    return d


def generate_note(d, role_field="role"):  # SAHTE: sabit not döner
    return {"dialogue_id": d["dialogue_id"],
            "condition": role_field or "rolsuz", "model": "mock",
            "S": "Patient reports cough for one week, mild fever.",
            "O": "Not examined yet.", "A": "Possible upper respiratory infection.",
            "P": "Lung examination; consider chest X-ray."}
