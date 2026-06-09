# ThermalSim Designer

ThermalSim Designer; 2D geometri tabanlı, parça düğümlerinden oluşan termal direnç ağı ile çalışan, taşınım katsayısı tahmini yapabilen ve sonuçları tablo/grafik olarak gösteren Python masaüstü mühendislik yazılımıdır.

## Kurulum

Windows için önerilen adımlar:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS için:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
python main.py
```

İlk açılışta `data/materials_100.json`, `data/fluids_20.json` ve `data/default_project.json` yoksa otomatik oluşturulur.

## Örnek Proje Açma

Üst menüden `File > Open Project` seçin ve `examples/` klasöründeki dosyalardan birini açın:

- `electronics_cooling.json`
- `multilayer_wall.json`
- `pipe_wall_convection.json`

## Solver Mantığı

İlk MVP sürümünde her parça tek bir termal node olarak modellenir. Solver `G * T = Q` lineer sistemini kurar ve NumPy ile çözer. Isı kaynakları Q vektörüne eklenir; sabit sıcaklık ve taşınım sınır şartları node ile çevre arasında referans bağlantısı oluşturur; interface kayıtları iki node arasında termal direnç olarak eklenir.

## Taşınım Katsayısı Predictor Mantığı

`ConvectionPredictor` üç temel korelasyonu destekler:

1. Zorlanmış dış düz plaka akışı
2. Doğal dikey plaka taşınımı
3. Boru içi akış

Sonuç olarak h, Re, Pr, Nu, Ra, Gr, korelasyon adı, geçerlilik mesajı ve güven seviyesi döndürülür.

## Sık Hatalar ve Çözümleri

- **Solver singular matrix uyarısı:** En az bir `fixed_temperature` veya `convection` boundary ekleyin.
- **Invalid h value:** Convection boundary için h değerini 0'dan büyük girin.
- **Invalid geometry:** Genişlik, yükseklik, yarıçap ve kalınlığın pozitif olduğundan emin olun.
- **Import/PySide6 hatası:** Sanal ortamı etkinleştirip `pip install -r requirements.txt` komutunu tekrar çalıştırın.
- **Sonuç grafiği açılmıyor:** Önce `Solve > Run Thermal Resistance Solver` komutunu çalıştırın.
