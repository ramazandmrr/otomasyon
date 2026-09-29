# DershaneMatik

Hafta sonu matematik özel ders saatlerini online talep etmeyi sağlayan Flask + SQLite uygulaması.

## Kurulum
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py        # http://127.0.0.1:5000
```
Üretim: `gunicorn app:app`

## Ortam değişkenleri
| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `DB_PATH` | `data/dershane.db` | SQLite dosya yolu (Render/Railway'de kalıcı disk yoluna ayarlayın) |
| `PORT` | `5000` | Yerel geliştirme portu |

## API uçları
| Metot | Yol | Açıklama |
|---|---|---|
| GET | `/` | Landing page + form |
| GET | `/doluluk` | Doluluk sayfası |
| POST | `/api/talepler` | Talep oluşturur (201 / 400 / 409 / 500) |
| GET | `/api/talepler/doluluk` | 18 slotun dolu/boş durumu (öğrenci bilgisi içermez) |

## Veritabanı
`talepler(id, ad_soyad, email, hizmet, ogretmen_id, gun, saat, not_metni, olusturma_tarihi)`
`UNIQUE(ogretmen_id, gun, saat)` çakışmayı veritabanı seviyesinde engeller.

## Klasör yapısı
```
app.py  requirements.txt  README.md  AI_LOG.md
templates/ index.html doluluk.html
static/    style.css app.js
data/      dershane.db (otomatik oluşur)
```
Tüm veriler kurgusaldır.
