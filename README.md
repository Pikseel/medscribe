# MedScribe

Doktor–hasta konuşmasından konuşmacı rolü tespiti ve otomatik SOAP notu (CSE 484 NLP dersi projesi).

**Araştırma sorusu:** Doctor/Patient konuşmacı etiketleri, bir LLM'in transkriptten yazdığı SOAP notunu iyileştiriyor mu?
**Takım:** 17

**Ara sunum:** [`results/Team17_MidProject.pdf`](results/Team17_MidProject.pdf) (10 slayt + 4 slayt Project Card).

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

Alan 8'deki rol sonuçlarını ve commitlenmiş altı dondurulmuş GPU notundan hesaplanan ROUGE değerlerini tek komutla yeniden üretir; ardından sunum kaynağını oluşturur:

```bash
make reproduce
```

Komut izole `.repro-venv` ortamını kurar, rol modelini eğitir, dondurulmuş test değerlendirmesini çalıştırır ve `results/Team17_MidProject.pptx` dosyasını üretir. İlk çalıştırmada açık ACI-Bench CSV dosyalarını indirir. SOAP notlarının yeniden üretilmesi bu komuta dahil değildir; GPU ister ve `notes/colab_soap.ipynb` (Colab, T4) ile yapılır.

Doğrulanan CPU ortamı: Python 3.12.4; scikit-learn 1.9.1; numpy 2.5.4; scipy 1.18.1; joblib 1.6.0; python-pptx 1.0.2; rouge-score 0.1.2. Python bağımlılıkları `requirements.txt` içinde sabitlenmiştir.

## Demo
Colab'da `app/demo_colab.ipynb` → Runtime: T4 GPU → Run all. Son hücre bir `gradio.live` linki verir.
Yerelde, LLM olmadan: `pip install gradio && python -m app.pipeline`.
Gerçek modüller yoksa demo otomatik olarak `common/mocks.py`'ye düşer; arayüzün üstünde hangisinin çalıştığı yazar.

## Veri
- ACI-Bench (CC BY 4.0): train 67 / dev 20 / test 40 görüşme (`clinicalnlp_taskB_test1`, dondurulmuş). `eval/` ve `roles/` ilk çalıştırmada indirir.
- PriMock57 (CC BY 4.0; resmi `LICENSE.md` doğrulandı): 20 görüşme, sadece konuşmacı ayırma ölçümü için.

Tam kaynakça, DOI/URL'ler ve veri lisansı bağlantıları için [`REFERENCES.md`](REFERENCES.md) dosyasına bakın.
