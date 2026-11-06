# MedScribe

Doktor–hasta konuşmasından konuşmacı rolü tespiti ve otomatik SOAP notu (NLP dersi projesi).

## Klasörler (herkes sadece kendi klasörüne yazar)
| Klasör | Sahibi | İçerik |
|---|---|---|
| `common/` | Kişi 4 | `format.py` (check_format), `ornek_diyalog.json`, `mocks.py` |
| `asr/` | Kişi 1 | `transcribe.py`, notebook, `asr_*.json` |
| `roles/` | Kişi 2 | `assign_roles.py`, eğitim notebook'u |
| `notes/` | Kişi 3 | `generate_note.py`, `istem_v1.txt`, `data/`, `outputs/` |
| `app/` | Kişi 4 | Gradio demosu |
| `results/` | herkes | tablolar, ekran görüntüleri (`kisiN_` ön ekiyle) |

Kurallar: push etmeden önce `git pull`. Doğrudan `main`. Başkasının dosyası değişecekse sahibine yaz.
Modeller ve ses kayıtları **Drive'da** (`MedScribe_Drive/`), repoya girmez (`.gitignore`).

## Fonksiyon imzaları
```python
transcribe(audio_path)              -> dialogue   # asr/transcribe.py
assign_roles(dialogue)              -> dialogue   # roles/assign_roles.py
generate_note(dialogue, role_field) -> note       # notes/generate_note.py  role_field: "role" | "gold_role" | None
```
Format ayrıntıları: proje planı Bölüm 2.3. Rol değerleri sadece `"Doctor"`, `"Patient"`, `null`.

## Format kontrolü
```bash
python -m common.format asr/asr_001.json notes/data/aci_001.json
```
Notebook içinde:
```python
import sys; sys.path.append("/content/medscribe")
from common.format import check_format, save, load
save(dialogue, "roles/test.json")   # kaydetmeden önce otomatik kontrol eder
```

## Demo
`app/pipeline.py`, `roles/assign_roles.py` ve `notes/generate_note.py` varsa **otomatik olarak gerçeklerini**,
yoksa `common/mocks.py`'yi kullanır. Arayüzün üstünde hangisinin çalıştığı yazar. Kimse import satırı değiştirmez.

Yerelde (sahte modüllerle):
```bash
pip install gradio
python -m app.pipeline      # konsolda hızlı test
python -m app.app           # arayüz
```
Colab'da (T4 GPU):
```python
!git clone https://github.com/<KULLANICI>/medscribe.git
%cd medscribe
!pip install -q gradio
from google.colab import drive; drive.mount("/content/drive")   # modeller Drive'dan
!python -m app.app          # share linki çıktıda
```
