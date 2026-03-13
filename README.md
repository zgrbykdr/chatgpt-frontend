# YouTube Müzik Yöneticisi (PySide6)

Modern arayüzlü masaüstü uygulama: YouTube linklerini kaydeder, not/favori/etiket yönetimi yapar ve kayıtlı bağlantıyı **Microsoft Edge** üzerinde mevcut profilinle yeni sekmede açar.

## Dosya Yapısı

```text
chatgpt-frontend/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ gui.py
│  ├─ database.py
│  ├─ edge_launcher.py
│  ├─ settings_manager.py
│  └─ models.py
├─ run.py
└─ requirements.txt
```

## Kurulum

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Çalıştırma

```bash
python run.py
```

## Özellikler

- Kayıt ekle / düzenle / sil
- Arama ve favori filtreleme
- İsme göre veya son açılanlara göre sıralama
- Çift tıklama ile Edge'de açma
- “Edge'de Aç ve Çal” butonu
- Link kopyalama
- JSON/CSV içe-dışa aktarma
- SQLite veritabanı yedekleme
- Ayarlar ekranı:
  - Edge exe yolu
  - Profil klasörü
  - Profil adı
  - Ek açılış parametreleri
  - Koyu / açık tema

## EXE Alma (Windows)

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name YouTubeMuzikYoneticisi run.py
```

Oluşan uygulama: `dist/YouTubeMuzikYoneticisi/YouTubeMuzikYoneticisi.exe`

## Notlar

- Uygulama YouTube'dan indirme yapmaz; sadece linkleri açar.
- Veriler varsayılan olarak kullanıcı klasöründe `~/YouTubeMuzikYoneticisi` altında saklanır.
