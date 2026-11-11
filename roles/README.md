# Kişi 2 — konuşmacı rolü tespiti

Bu modül, konuşmadaki her konuşmacıyı `Doctor` veya `Patient` olarak etiketler.
`A`, `B` ya da `SPEAKER_00` gibi adları ezberlemez; aynı konuşmacının bütün
cümlelerini birleştirip metinden tahmin yapar.

## Hazır kurulum

Proje kökünden:

```bash
python3 -m venv roles/.venv
roles/.venv/bin/pip install -r roles/requirements.txt
roles/.venv/bin/python -m roles.train_roles
```

Son komut ACI-Bench eğitim CSV'sini `roles/data/_raw/` altına indirir, modeli
eğitir ve `roles/models/role_classifier.joblib` olarak kaydeder. Ham veri,
sanal ortam ve model Git'e eklenmez. Görüşme bazlı 5-fold cross-validation ve
holdout sonuçları `results/kisi2_role_metrics.json` dosyasına yazılır.

## Kullanım

Python içinden:

```python
from roles.assign_roles import assign_roles

dialogue = assign_roles(dialogue)
```

Dosya üzerinde:

```bash
roles/.venv/bin/python -m roles.assign_roles \
  common/ornek_diyalog.json -o roles/outputs/ornek_rollu.json
python -m common.format roles/outputs/ornek_rollu.json
```

Demo boru hattı:

```bash
roles/.venv/bin/python -m app.pipeline
```

`role_prob`, konuşmacının doktor olma olasılığıdır. İki konuşmacılı girdide
olasılıklar birlikte değerlendirilir; tam olarak bir doktor ve bir hasta
atanır. Bir konuşmacının tüm segmentleri aynı rolü alır.

## Notebook

```bash
roles/.venv/bin/jupyter lab roles/role_egitim.ipynb
```

Notebook veri indirme, eğitim, değerlendirme ve örnek tahmin adımlarını sırayla
çalıştırır. Eğitim/test ayrımı görüşme kimliğine göre yapılır; aynı görüşmenin
metni iki tarafa sızmaz. Ana rapor değeri, tek bir şanslı bölünmeye bağlı
kalmamak için 5-fold ortalama accuracy ve macro-F1 değerleridir.

## Sunum

```bash
roles/.venv/bin/python -m roles.build_slides
```

Komut aynı tasarım dilinde üç Kişi 2 slaydı üretir:

- yöntem ve sayısal model özellikleri,
- 5-fold cross-validation ile holdout karşılaştırması,
- Kişi 1 ASR çıktısı üzerinde uçtan uca entegrasyon.

Çıktı `results/kisi2_slides.pptx` yereldir (repoda tutulmaz). Final sunumda
yöntem slaytı `app/build_deck.py` içinden doğrudan kullanılır.
