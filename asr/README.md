# asr/ — Ses → metin modülü (Kişi 1)

Bir ses dosyasını konuşmacı etiketli, zaman damgalı transkripte çevirir ve
ortak JSON formatında döndürür.

```python
from asr.transcribe import transcribe
d = transcribe("kayit.wav", language="en", num_speakers=2)
```

Çıktıdaki `role`, `gold_role` ve `role_prob` alanları `None` kalır. Doktor/hasta
eşlemesini `roles/assign_roles.py` yapar.

## Dosyalar
- `transcribe.py`: modül.
- `asr_deneyleri.ipynb`: deney kaydı (kurulum, örnek üretimi, değerlendirme).
- `asr_001.json`: PriMock57 day1_consultation01'in ilk 3 dakikasından üretilmiş örnek çıktı. `SPEAKER_00` doktor.

## Nasıl çalıştırılır
- Colab, T4 GPU. `pip install whisperx`, sonra Restart session.
- Colab Secrets'a `HF_TOKEN` ekle; notebook'ta "Notebook access" açık olmalı.
- Hugging Face'te `pyannote/speaker-diarization-community-1` sayfasında kullanım şartlarını kabul et.
- Notebook: Runtime → Run all.

## Kullanılan bileşenler
Hazır modeller, eğitim yok: WhisperX (Whisper `small` + hizalama) ve pyannote
(`speaker-diarization-community-1`).

## Plandan sapmalar
- Kendi kaydımız yerine PriMock57 (Korfiatis ve ark., ACL 2022) kullanıldı. Doktor ve hasta kanalları birleştirilerek tek kanallı kayıt üretildi.
- Diarization modeli planda yazılan 3.1 yerine güncel `community-1`.
- Ana model `medium` yerine `small`; medium karşılaştırması yapıldı, konuşmacı doğruluğunu anlamlı değiştirmedi.

## Sonuçlar (PriMock57, 20 muayene, ilk 5 dakika)
- Konuşmacı doğruluğu: %93,8 (2050 cümlenin 1923'ü).
- Kısa cümleler (< 1 sn): %87,8; uzun cümleler: %96,7.
- small vs medium (ilk 10 muayene): %96,0 vs %96,5.
- Gold etiket kanal enerjisinden üretildi (yaklaşık).

## Bilinen sınırlılıklar
- Kısa parçalarda (< 1 sn) ve araya girmelerde konuşmacı etiketi hatalı olabiliyor.
- Tek kişinin iki rol okuduğu kayıtta diarization tek konuşmacı buldu; iki konuşmacıya zorlanınca bölme keyfi oldu.
- Klinik terimlerde ve kısa ifadelerde ASR hatası görüldü ("start" → "stop", "cough syrup").
- Sonuçlar temiz kayıtlarda ölçüldü; telefonla alınmış gürültülü kayıtlarda düşmesi beklenir.
- `SPEAKER_00` / `SPEAKER_01` etiketleri rastgele sıralanır.
