# AGENTS.md - ThermalSim Designer Çalışma Kuralları

Bu dosya, bu depo ağacında yapılacak tüm değişiklikler için geçerlidir. Amaç, `thermal_sim_designer` projesinin çalışır, test edilebilir, bakımı kolay ve kullanıcıya eksiksiz teslim edilebilir kalmasını sağlamaktır.

## Genel proje kuralları

- Proje, Python 3.11+ ile çalışan bir masaüstü mühendislik uygulamasıdır.
- Arayüz katmanı PySide6 kullanmalıdır.
- Hesaplama ve sayısal işlemler NumPy ile yapılmalıdır.
- Grafik ve post-processing görselleştirmeleri Matplotlib ile yapılmalıdır.
- Core hesaplama modülleri PySide6 veya GUI bağımlılığı içermemelidir.
- GUI kodu hesaplama mantığını kendi içinde yeniden uygulamamalı, `core/` modüllerini çağırmalıdır.
- Veri modelleri, solver, arayüz ve post-processing sorumlulukları ayrı dosyalarda tutulmalıdır.
- Dosya yolları için `pathlib.Path` tercih edilmelidir.
- JSON dosyaları `encoding="utf-8"` ile okunmalı ve yazılmalıdır.
- Windows kullanım kolaylığı korunmalıdır; README komutları Windows kullanıcıları için açık kalmalıdır.

## Kodlama standartları

- Python kodu PEP 8'e yakın biçimde yazılmalıdır.
- Fonksiyon, sınıf, değişken ve dosya adları İngilizce olmalıdır.
- Kullanıcı arayüzü metinleri Türkçe veya İngilizce olabilir; kullanıcıya gösterilen hata mesajları anlaşılır olmalıdır.
- Fonksiyonlar gereksiz uzun olmamalı; karmaşık akışlar küçük yardımcı fonksiyonlara ayrılmalıdır.
- Her kritik işlemde hata kontrolü yapılmalıdır:
  - JSON okuma/yazma
  - proje yükleme/kaydetme
  - solver çalıştırma
  - boundary/interface ekleme
  - kullanıcı girdisi dönüştürme ve doğrulama
- Geçersiz kullanıcı girdisi uygulamayı çökertmemeli; kullanıcıya uyarı verilmelidir.
- Import ifadelerinin etrafına `try/except` koymayın. Eksik bağımlılık varsa bağımlılık veya ortam düzeltilmelidir.
- Yeni bağımlılık eklerseniz `requirements.txt` ve README kurulum açıklamaları güncellenmelidir.

## Placeholder ve eksik iş yasağı

- Çalışmayan placeholder kod bırakmayın.
- `TODO`, `FIXME`, `stub`, `dummy`, `pass` ile bırakılmış eksik özellik veya “bunu sonra ekleyin” tarzı teslimat kabul edilmez.
- Yeni eklenen menü, buton, sınıf veya fonksiyon çalışır davranışa sahip olmalıdır.
- Eksik dosya, boş modül veya yalnızca isim olsun diye eklenmiş çalışmayan yapı bırakmayın.
- Kullanıcının elle kod düzenlemesini gerektiren kurulum veya çalışma adımı bırakmayın.

## Veri ve varsayılanlar

- `data/materials_100.json`, `data/fluids_20.json` ve `data/default_project.json` ilk çalıştırmada yoksa otomatik üretilebilir olmalıdır.
- Malzeme bulunamazsa güvenli varsayılan olarak `Aluminum 6061` kullanılmalıdır.
- Akışkan bulunamazsa güvenli varsayılan olarak `Air` kullanılmalıdır.
- Termal iletkenlik, alan, kalınlık, taşınım katsayısı gibi fiziksel değerler pozitiflik açısından doğrulanmalıdır.
- Solver, boundary veya sink eksikse açık ve anlaşılır hata mesajı döndürmelidir.

## Test zorunlulukları

Kod değişikliği yaptıktan sonra mümkün olduğunda aşağıdaki kontroller çalıştırılmalıdır:

```bash
cd thermal_sim_designer
python -m compileall .
PYTHONPATH=. pytest -q
```

GUI davranışı veya import zinciri değiştiyse ayrıca headless smoke test çalıştırılmalıdır:

```bash
cd thermal_sim_designer
QT_QPA_PLATFORM=offscreen PYTHONPATH=. python - <<'PY'
import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.processEvents()
print(window.windowTitle())
window.dirty = False
window.close()
PY
```

- Test başarısızsa nedeni düzeltilmeden değişiklik teslim edilmemelidir.
- Ortam kısıtı nedeniyle bir test çalıştırılamazsa final yanıtta bu durum açıkça belirtilmelidir.
- Solver, convection predictor veya proje IO davranışı değişirse ilgili testler güncellenmeli veya yeni test eklenmelidir.

## Dokümantasyon ve teslimat

- Kullanıcıya yönelik çalıştırma adımları README içinde açık kalmalıdır.
- Yeni özellik eklenirse README veya ilgili açıklama dosyası güncellenmelidir.
- Final yanıtta çalıştırılan test komutları sonuç durumuyla birlikte belirtilmelidir.
- Değişiklikler commit edilmeden teslim edilmemelidir.
