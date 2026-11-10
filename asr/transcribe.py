"""MedScribe ses -> metin modülü (Kişi 1).

transcribe(audio_path) -> ortak JSON formatında dialogue sözlüğü
(konuşmacı etiketli, zaman damgalı). role / gold_role / role_prob None kalır;
doktor/hasta kararını Kişi 2'nin assign_roles() modülü verir.

Gereksinimler:
  - pip install whisperx
  - ortam değişkeni HF_TOKEN (Hugging Face erişim anahtarı) ve
    pyannote/speaker-diarization-community-1 için kabul edilmiş kullanım şartları
"""
import os

import torch
import whisperx
from whisperx.diarize import DiarizationPipeline

_cache = {}


def _load(language, whisper_model, device):
    """Modelleri bir kez yükler, sonraki çağrılarda önbellekten verir."""
    key = (language, whisper_model, device)
    if key not in _cache:
        compute_type = "float16" if device == "cuda" else "int8"
        asr = whisperx.load_model(whisper_model, device,
                                  compute_type=compute_type, language=language)
        align, meta = whisperx.load_align_model(language_code=language, device=device)
        diar = DiarizationPipeline(token=os.environ["HF_TOKEN"], device=device)
        _cache[key] = (asr, align, meta, diar)
    return _cache[key]


def transcribe(audio_path, language="en", whisper_model="small",
               dialogue_id="asr_001", num_speakers=2, device=None):
    """Ses dosyasını konuşmacı etiketli transkripte çevirir.

    num_speakers: bilinen konuşmacı sayısı (muayenede 2). None verilirse
    diarization modeli sayıyı kendisi seçer.
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    asr, align, meta, diar = _load(language, whisper_model, device)
    audio = whisperx.load_audio(audio_path)

    # 1) transkripsiyon, 2) kelime hizalama, 3) konuşmacı ayırma
    result = asr.transcribe(audio, batch_size=16)
    result = whisperx.align(result["segments"], align, meta, audio, device,
                            return_char_alignments=False)
    diarize_segments = diar(audio, min_speakers=num_speakers,
                            max_speakers=num_speakers)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    segments = []
    for s in result["segments"]:
        text = s["text"].strip()
        if not text:  # check_format boş metni reddeder
            continue
        segments.append({
            "id": len(segments),
            "start": round(s["start"], 2),
            "end": round(s["end"], 2),
            "speaker": s.get("speaker", "UNKNOWN"),
            "gold_role": None,
            "role": None,
            "role_prob": None,
            "text": text,
        })
    return {"dialogue_id": dialogue_id, "source": "asr",
            "reference_note": None, "segments": segments}
