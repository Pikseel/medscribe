"""MedScribe — SOAP note generation (Person 3).

Project plan section 2.4 signature:
    generate_note(dialogue, role_field) -> note
        role_field = "role"      -> roles predicted by the classifier  (demo)
        role_field = "gold_role" -> gold roles                         ("rollu" condition)
        role_field = None        -> no speaker information             ("rolsuz" condition)

Prompt text: notes/istem_v1.txt (frozen). There is no copy of the prompt in code;
to change it, edit the file and bump the version name (istem_v2.txt).

The backend is selected automatically (force it with SOAP_BACKEND or --backend):
    "transformers" -> when a GPU is present: 4-bit Qwen/Qwen2.5-7B-Instruct (Colab / T4)
    "ollama"       -> otherwise: local Ollama, qwen2.5:7b-instruct-q4_K_M

Only the two functions around `_chat()` depend on the backend. Transcript building,
prompting and JSON parsing are identical on both.

CLI (from the repository root):
    python -m notes.generate_note --dialogue common/ornek_diyalog.json --role-field gold_role
    python -m notes.generate_note --prompt-only --dialogue notes/data/aci_001.json --role-field None
    python -m notes.generate_note --experiment     # 3 dialogues x 2 conditions -> notes/outputs/
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # repository root
PROMPT_PATH = os.path.join(HERE, "istem_v1.txt")
OUT_DIR = os.path.join(HERE, "outputs")

MODEL_OLLAMA = "qwen2.5:7b-instruct-q4_K_M"
MODEL_HF = "Qwen/Qwen2.5-7B-Instruct"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
TEMPERATURE = 0          # frozen: unchanged for the whole experiment
MAX_NEW_TOKENS = 1500    # aci_003 needs ~900; 700 truncated its note mid-string
RETRY_MAX_NEW_TOKENS = 2500

# Sent only when the first reply is not parseable (usually truncation).
RETRY_INSTRUCTION = (
    "Reply with JSON only, keys S, O, A, P. Keep each value under 120 words.")


def _detect_backend():
    """transformers when a GPU and the library are available, Ollama otherwise.

    The environment variable takes precedence.
    """
    if os.environ.get("SOAP_BACKEND"):
        return os.environ["SOAP_BACKEND"]
    try:
        import torch
        if torch.cuda.is_available():
            import transformers  # noqa: F401
            return "transformers"
    except Exception:
        pass
    return "ollama"


BACKEND = _detect_backend()


def set_backend(name):
    global BACKEND
    assert name in ("ollama", "transformers"), name
    BACKEND = name


def model_name():
    return MODEL_HF if BACKEND == "transformers" else MODEL_OLLAMA


def condition_name(role_field):
    """Plan section 2.3: the `condition` field of a note is 'rollu' or 'rolsuz'."""
    return "rollu" if role_field else "rolsuz"


# --------------------------------------------------------------------------
# Frozen prompt
# --------------------------------------------------------------------------

def load_prompt(path=PROMPT_PATH):
    """istem_v1.txt -> (system, user_template). The file is the single source of truth."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    parts = re.split(r"^\[(SYSTEM|USER)\]\s*$", raw, flags=re.MULTILINE)
    # ["", "SYSTEM", <system>, "USER", <user>]
    if len(parts) != 5:
        raise ValueError(f"{path}: expected [SYSTEM] and [USER] sections")
    system, user = parts[2].strip(), parts[4].strip()
    if "{transcript}" not in user:
        raise ValueError(f"{path}: USER section is missing {{transcript}}")
    return system, user


SYSTEM_PROMPT, USER_TEMPLATE = load_prompt()


# --------------------------------------------------------------------------
# Transcript building
# --------------------------------------------------------------------------

def build_transcript(dialogue, role_field):
    """'Doctor: ...' / 'Patient: ...' when role_field is set, bare text when None.

    The rolsuz condition keeps the speaker order but hides who is who. Segments
    whose role is still null (e.g. the classifier has not run yet) are written
    without a label.
    """
    lines = []
    for seg in dialogue["segments"]:
        text = seg["text"].strip()
        if not text:
            continue
        role = seg.get(role_field) if role_field else None
        lines.append(f"{role}: {text}" if role else text)
    return "\n".join(lines)


def build_messages(dialogue, role_field):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TEMPLATE.format(
            transcript=build_transcript(dialogue, role_field))},
    ]


# --------------------------------------------------------------------------
# Model call — the only backend-dependent part
# --------------------------------------------------------------------------

def _chat_ollama(messages, max_new_tokens=MAX_NEW_TOKENS, timeout=900):
    body = json.dumps({
        "model": MODEL_OLLAMA,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {"temperature": TEMPERATURE, "num_ctx": 8192,
                    "num_predict": max_new_tokens},
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))["message"]["content"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(
                f"Ollama does not have '{MODEL_OLLAMA}'. Fix: `ollama pull {MODEL_OLLAMA}`, "
                f"or use SOAP_BACKEND=transformers on Colab.") from e
        raise
    except urllib.error.URLError as e:
        raise RuntimeError(
            "Could not reach the Ollama server (http://127.0.0.1:11434). "
            "Is `ollama serve` running? On Colab use SOAP_BACKEND=transformers.") from e


_HF = {}


def _load_hf():
    """Colab/T4: 4-bit loading. Called once, then kept in memory."""
    if _HF:
        return _HF["model"], _HF["tok"]
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,   # the T4 does not support bf16
        bnb_4bit_use_double_quant=True,
    )
    tok = AutoTokenizer.from_pretrained(MODEL_HF)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_HF, quantization_config=bnb, device_map="auto")
    model.eval()
    _HF.update(model=model, tok=tok)
    return model, tok


def _chat_transformers(messages, max_new_tokens=MAX_NEW_TOKENS):
    import torch

    model, tok = _load_hf()
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,                 # temperature=0
            pad_token_id=tok.eos_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    return tok.decode(new_tokens, skip_special_tokens=True)


def _chat(messages, max_new_tokens=MAX_NEW_TOKENS):
    if BACKEND == "transformers":
        return _chat_transformers(messages, max_new_tokens=max_new_tokens)
    return _chat_ollama(messages, max_new_tokens=max_new_tokens)


# --------------------------------------------------------------------------
# Output parsing
# --------------------------------------------------------------------------

FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def parse_note(content):
    raw = FENCE.sub("", content).strip()
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            raise
        obj = json.loads(raw[start:end + 1])
    missing = [k for k in ("S", "O", "A", "P") if k not in obj]
    if missing:
        raise ValueError(f"model output is missing fields: {missing}")
    return {k: str(obj[k]).strip() for k in ("S", "O", "A", "P")}


def generate_note(dialogue, role_field="role"):
    """Main deliverable. Returns: dialogue_id, condition, model, S, O, A, P."""
    messages = build_messages(dialogue, role_field)
    try:
        soap = parse_note(_chat(messages))
    except (json.JSONDecodeError, ValueError) as first:
        # Normally truncation: the longest dialogue overran the token budget.
        retry = messages + [{"role": "user", "content": RETRY_INSTRUCTION}]
        try:
            soap = parse_note(_chat(retry, max_new_tokens=RETRY_MAX_NEW_TOKENS))
        except (json.JSONDecodeError, ValueError) as second:
            raise ValueError(
                f"{dialogue['dialogue_id']} ({condition_name(role_field)}): the model did not "
                f"return valid JSON twice. First error: {first}. If it says 'Unterminated "
                f"string', the reply was cut off by the token limit; raise MAX_NEW_TOKENS."
            ) from second

    note = {"dialogue_id": dialogue["dialogue_id"],
            "condition": condition_name(role_field),
            "model": model_name()}
    note.update(soap)
    return note


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_note(note, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(note, f, ensure_ascii=False, indent=2)


EXPERIMENT = [(os.path.join(HERE, "data", "aci_001.json"), "gold_role", "rollu"),
              (os.path.join(HERE, "data", "aci_001.json"), None, "rolsuz"),
              (os.path.join(HERE, "data", "aci_002.json"), "gold_role", "rollu"),
              (os.path.join(HERE, "data", "aci_002.json"), None, "rolsuz"),
              (os.path.join(HERE, "data", "aci_003.json"), "gold_role", "rollu"),
              (os.path.join(HERE, "data", "aci_003.json"), None, "rolsuz")]


def _role_field(value):
    return None if value in (None, "None", "none", "") else value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dialogue")
    ap.add_argument("--role-field", default="gold_role",
                    help='"role", "gold_role" or None')
    ap.add_argument("--backend", default=BACKEND, choices=["ollama", "transformers"])
    ap.add_argument("--prompt-only", action="store_true")
    ap.add_argument("--experiment", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    a = ap.parse_args()
    set_backend(a.backend)

    if a.prompt_only:
        print(f"# model: {model_name()}\n")
        for m in build_messages(load(a.dialogue), _role_field(a.role_field)):
            print(f"### {m['role'].upper()}\n{m['content']}\n")
        return

    if a.experiment:
        for path, rf, cond in EXPERIMENT:
            d = load(path)
            note = generate_note(d, rf)
            out = os.path.join(a.out, f"{d['dialogue_id']}_{cond}.json")
            save_note(note, out)
            print(f"{out}: S{len(note['S'])} O{len(note['O'])} "
                  f"A{len(note['A'])} P{len(note['P'])} chars")
        return

    d = load(a.dialogue)
    note = generate_note(d, _role_field(a.role_field))
    print(json.dumps(note, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
