# notes/ — Kişi 3: SOAP notu ve deney

`generate_note(dialogue, role_field) -> note` — rol etiketli transkriptten LLM ile SOAP notu
üretir ve rol bilgisinin nota etkisini ölçen ilk karşılaştırmayı yapar.
Proje planı Bölüm 3 (Kişi 3) ve Bölüm 4 takvimi.

## Dosyalar

| Dosya | Ne yapar |
|---|---|
| `generate_note.py` | Teslim fonksiyonu + CLI. Arka uç otomatik: GPU varsa transformers, yoksa Ollama |
| `istem_v1.txt` | **Dondurulmuş** istem. Tek doğruluk kaynağı; kodda kopyası yok |
| `data/aci_001..003.json` | ACI-Bench'ten seçilmiş 3 diyalog, ortak formatta (`check_format` temiz) |
| `build_aci_data.py` | CSV → JSON dönüştürücü (ham CSV yoksa indirir) |
| `compare_notes.py` | Rollü/rolsüz notları yan yana + olumsuzlama bayrakları → `outputs/karsilastirma.md` |
| `colab_soap.ipynb` | Colab'da 6 notu üreten notebook (repoyu klonlar, T4) |
| `outputs/` | Üretilen 6 not + karşılaştırma raporu |

Slaytlar: `results/kisi3_slaytlar.pptx` (sunum 7–8, konuşmacı notlarıyla).
Üretici: `notes/build_slides.py`.

## Kullanım (repo kökünden)

```bash
python -m notes.generate_note --prompt-only --dialogue common/ornek_diyalog.json --role-field gold_role
python -m notes.generate_note --dialogue notes/data/aci_001.json --role-field gold_role
python -m notes.generate_note --experiment        # 3 diyalog x 2 koşul -> notes/outputs/
python -m notes.compare_notes                     # karşılaştırma raporu
```

`role_field`:
- `"role"` — Kişi 2'nin tahmin ettiği roller (demo)
- `"gold_role"` — doğru roller ("rollü" koşulu)
- `None` — konuşmacı bilgisi yok ("rolsuz" koşulu)

## Deney

3 diyalog × 2 koşul = **6 not**. Not çıktısı plan Bölüm 2.3'teki biçimde:

```json
{"dialogue_id": "aci_001", "condition": "rollu", "model": "Qwen/Qwen2.5-7B-Instruct",
 "S": "...", "O": "...", "A": "...", "P": "..."}
```

Seçilen diyaloglar (hepsi 25–26 cümle, üçünde de olumsuzlama var):

| ID | ACI-Bench | Konu |
|---|---|---|
| `aci_001` | D2N050 | böbrek taşı |
| `aci_002` | D2N053 | kaşıntılı saç derisi — referans notta "Denies any rashes" |
| `aci_003` | D2N060 | sol ayak ağrısı |

**Durum:** kod ve istem hazır; 6 not Colab'da (T4) üretilecek. Yerel makinede 7B model
indirilemedi (ağ ~300 KB/s → 4+ saat), bu yüzden Colab planın öngördüğü ortam.

### Colab

1. `notes/colab_soap.ipynb` dosyasını Colab'a yükle.
2. **Çalışma zamanı → T4 GPU**.
3. Hücreleri sırayla çalıştır (repoyu kendisi klonlar).
4. Hücre 6 örnek diyaloğu üretir — **kontrol noktası**: hastanın reddettiği göğüs ağrısı
   olumlu yazıldıysa istem zayıf demektir; `istem_v2.txt` açmadan devam etme.
5. Hücre 7 altı notu, hücre 8 karşılaştırmayı üretir. `notes/outputs/`'u commit et.

## İstem dondurma kuralı

`istem_v1.txt` deney başladıktan sonra değişmez. Değişiklik gerekirse `istem_v2.txt` açılır ve
6 not yeniden üretilir; iki sürümün notları aynı tabloda karıştırılmaz. `temperature = 0`.

## Demo entegrasyonu (Kişi 4)

```python
from notes.generate_note import generate_note   # app/pipeline.py zaten böyle bağlıyor
note = generate_note(dialogue, "role")
```

- Backend otomatik seçilir: Colab/T4'te `transformers`, aksi halde Ollama.
  Zorlamak için `SOAP_BACKEND=transformers` veya `gn.set_backend("transformers")`.
- `role` alanı boşsa o cümle etiketsiz yazılır — model çökmez, demo Kişi 2'yi beklemez.
- Model yalnızca ilk not isteğinde yüklenir (`_load_hf`), import anında değil.
- Model yoksa hata mesajı ne yapılacağını söyler (`ollama pull ...` / Colab).

## Notlar

- Ham ACI-Bench CSV'si `data/_raw/` altında, repoya girmez (`.gitignore`); `build_aci_data.py`
  yoksa indirir. Üretilen 3 JSON repoda.
- `data/*.json` içinde `start/end`, `role`, `role_prob` = `null`; bunları Kişi 2 doldurur.
- `aci_002` referans notu 1154 karakter, `aci_003` 3008 karakter — ROUGE/BERTScore'a geçilirse
  uzunluk farkı göz önünde tutulmalı.
