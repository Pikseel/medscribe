# MedScribe

Doktor–hasta konuşmasından konuşmacı rolü tespiti ve otomatik SOAP notu (CSE 484 NLP dersi projesi).

**Araştırma sorusu:** Doctor/Patient konuşmacı etiketleri, bir LLM'in transkriptten yazdığı SOAP notunu iyileştiriyor mu?
**Ara sunum:** [`results/MedScribe_MidProject.pdf`](results/MedScribe_MidProject.pdf) (10 slayt + 4 slayt Project Card).

## Klasörler
| Klasör | Modül | İçerik |
|---|---|---|
| `asr/` | 1 · Ses → metin | `transcribe()` (WhisperX + pyannote), deney notebook'u, örnek çıktı |
| `roles/` | 2 · Rol ataması | `assign_roles()` (TF-IDF + LR), eğitim, testler |
| `notes/` | 3 · SOAP notu | `generate_note()` (Qwen2.5-7B, dondurulmuş istem), 3×2 deney, bulgular |
| `app/` | 4 · Demo | Gradio arayüzü, Colab demo notebook'u, sunum üretici |
| `eval/` | Değerlendirme | ACI-Bench dondurulmuş test seti üzerinde rol değerlendirmesi |
| `common/` | Ortak | JSON format kontrolü, örnek diyalog, sahte (mock) fonksiyonlar |
| `results/` | Sonuçlar | Metrik tabloları, hata listesi, ara sunum |

Kurallar: herkes kendi modül klasörüne yazar; push etmeden önce `git pull`. Modeller ve ses kayıtları repoya girmez (`.gitignore`).

## Fonksiyon imzaları
```python
transcribe(audio_path)              -> dialogue   # asr/transcribe.py
assign_roles(dialogue)              -> dialogue   # roles/assign_roles.py
generate_note(dialogue, role_field) -> note       # notes/generate_note.py  role_field: "role" | "gold_role" | None
```
Ortak JSON formatı `common/format.py` içinde tanımlı; her dosya `python -m common.format dosya.json` ile kontrol edilir.

## Sonuçları yeniden üretme (repo kökünden)
```bash
pip install scikit-learn joblib python-pptx rouge-score
python -m roles.train_roles      # rol modeli -> roles/models/ (~10 sn)
python -m eval.role_eval         # dondurulmuş test: results/kisi4_role_eval.json, kisi4_utterance_errors.csv
python -m app.build_deck         # ara sunum: results/medscribe_midproject.pptx
```
SOAP notları GPU ister: `notes/colab_soap.ipynb` (Colab, T4) veya `python -m notes.generate_note --experiment`.

## Demo
Colab'da `app/demo_colab.ipynb` → Runtime: T4 GPU → Run all. Son hücre bir `gradio.live` linki verir.
Yerelde, LLM olmadan: `pip install gradio && python -m app.pipeline`.
Gerçek modüller yoksa demo otomatik olarak `common/mocks.py`'ye düşer; arayüzün üstünde hangisinin çalıştığı yazar.

## Veri
- ACI-Bench (CC BY 4.0): train 67 / dev 20 / test 40 görüşme (`clinicalnlp_taskB_test1`, dondurulmuş). `eval/` ve `roles/` ilk çalıştırmada indirir.
- PriMock57 (CC BY 4.0): 20 görüşme, sadece konuşmacı ayırma ölçümü için.
