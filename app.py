import os
import re
import sqlite3
from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "data", "dershane.db"))

app = Flask(__name__)

HIZMET = "Matematik Özel Ders"
OGRETMENLER = {
    "mat1": {"ad": "Ahmet Hoca", "kisa": "Ahmet", "uzmanlik": "TYT"},
    "mat2": {"ad": "Elif Hoca", "kisa": "Elif", "uzmanlik": "AYT"},
    "mat3": {"ad": "Murat Hoca", "kisa": "Murat", "uzmanlik": "TYT + AYT"},
}
GUNLER = {"cumartesi": "Cumartesi", "pazar": "Pazar"}
SAATLER = ["09:00", "10:00", "11:00"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS talepler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_soyad TEXT NOT NULL,
                email TEXT NOT NULL,
                hizmet TEXT NOT NULL,
                ogretmen_id TEXT NOT NULL,
                gun TEXT NOT NULL,
                saat TEXT NOT NULL,
                not_metni TEXT,
                olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (ogretmen_id, gun, saat)
            )"""
        )


def hata(mesaj, kod):
    return jsonify(ok=False, hata=mesaj), kod


@app.get("/")
def index():
    return render_template("index.html", ogretmenler=OGRETMENLER,
                           gunler=GUNLER, saatler=SAATLER, hizmet=HIZMET)


@app.get("/doluluk")
def doluluk_sayfasi():
    return render_template("doluluk.html")


@app.get("/api/talepler/doluluk")
def doluluk():
    with get_db() as conn:
        rows = conn.execute("SELECT ogretmen_id, gun, saat FROM talepler").fetchall()
    dolu = {f"{r['ogretmen_id']}|{r['gun']}|{r['saat']}" for r in rows}
    slotlar = [
        {"ogretmen_id": o, "gun": g, "saat": s,
         "dolu": f"{o}|{g}|{s}" in dolu}  # öğrenci bilgisi asla dönmez
        for g in GUNLER for s in SAATLER for o in OGRETMENLER
    ]
    return jsonify(ok=True, slotlar=slotlar, dolu=len(dolu), toplam=len(slotlar))


@app.post("/api/talepler")
def talep_olustur():
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return hata("Geçersiz istek.", 400)

    def alan(k):
        v = d.get(k, "")
        return v.strip() if isinstance(v, str) else ""

    ad, email, hizmet = alan("ad_soyad"), alan("email"), alan("hizmet")
    ogr, gun, saat, notu = alan("ogretmen_id"), alan("gun"), alan("saat"), alan("not_metni")

    if not 3 <= len(ad) <= 60:
        return hata("Ad Soyad 3–60 karakter olmalı.", 400)
    if not EMAIL_RE.match(email):
        return hata("E-posta formatı geçersiz.", 400)
    if hizmet != HIZMET:
        return hata("Geçersiz hizmet seçimi.", 400)
    if ogr not in OGRETMENLER:
        return hata("Geçerli bir öğretmen seçin.", 400)
    if gun not in GUNLER:
        return hata("Gün Cumartesi veya Pazar olmalı.", 400)
    if saat not in SAATLER:
        return hata("Saat 09:00, 10:00 veya 11:00 olmalı.", 400)
    if len(notu) > 500:
        return hata("Not en fazla 500 karakter olabilir.", 400)

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO talepler (ad_soyad, email, hizmet, ogretmen_id, gun, saat, not_metni) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ad, email, hizmet, ogr, gun, saat, notu or None),
            )
    except sqlite3.IntegrityError:
        # UNIQUE (ogretmen_id, gun, saat) — yarış durumunu da veritabanı seviyesinde yakalar
        return hata("Bu saat az önce dolduruldu, lütfen başka bir saat seçin.", 409)
    except sqlite3.Error:
        return hata("Kayıt oluşturulamadı, lütfen tekrar deneyin.", 500)

    return jsonify(ok=True, mesaj=f"Talebiniz alındı. {OGRETMENLER[ogr]['ad']} en kısa sürede dönüş yapacak."), 201


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
