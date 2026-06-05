# Dosya Yapısı

Bu proje kopyala-yapıştır mantığıyla çalışacak şekilde küçük ve anlaşılır tutuldu.

```text
chatgpt-frontend/
├── main.py                                      # Uygulamanın tam Python + Pygame kodu
├── requirements.txt                            # Kurulacak Python paketleri
├── README.md                                   # Türkçe kurulum ve kullanım özeti
├── FILE_STRUCTURE.md                           # Bu dosya: proje ağacı ve dosya görevleri
├── settings.json                               # Tema, çözünürlük ve uygulama ayarları
├── games/
│   └── Classic_Property_Trading_Game_Template.json
│       # Hazır klasik mülk-alım/satım oyunu şablonu
├── default_templates/
│   └── Classic_Property_Trading_Game_Template.json
│       # İlk açılışta tekrar üretmek için yedek varsayılan şablon
├── saves/
│   └── .gitkeep                                # Oyun içi kayıt JSON dosyaları burada oluşur
└── assets/
    └── .gitkeep                                # İsteğe bağlı PNG/JPG varlıkları buraya koyabilirsiniz
```

## Çalıştırma Sırası

1. `python -m pip install -r requirements.txt`
2. `python main.py`
3. Menüden:
   - `Add New Game` ile yeni oyun JSON'u oluşturun.
   - `Edit Existing Game` ile kare, aksiyon, timer, kart destesi ve kuralları düzenleyin.
   - `Play Game` ile kayıtlı JSON oyunlarından birini oynayın.

## Gerçekten Çalışan Sistemler

- Ana menü ve modern Pygame arayüzü
- Yeni oyun oluşturma ve `games/` klasörüne JSON kaydetme
- Var olan oyunu düzenleme
- Hazır 40 karelik klasik mülk ticareti şablonu
- Card deck ekleme/silme ve kart aksiyonu düzenleme
- Kare adı/tipi/fiyatı/kirası/renk grubu/görsel yolu/ikon/açıklama düzenleme
- Kare aksiyon tipi, hedefi, miktarı ve mesajı düzenleme
- Saniye, tur ve aynı kareye geri dönme temelli timer kayıtları
- Oyuncular arası para ve mülk ticareti popup'ı
- Oyuncular arası borç/loan popup'ı, faiz ve vade takibi
- Zar animasyonu ve kare kare oyuncu taşı ilerleme animasyonu
- Satın alma, kira, açık artırma, ev/otel, mortgage, kart, hapishane, iflas ve kazanan kontrolü
- Oyun içi `saves/` klasörüne JSON kayıt alma
