const OGR = { mat1: "Ahmet", mat2: "Elif", mat3: "Murat" };
const GUN_KISA = { cumartesi: "Cmt", pazar: "Paz" };
const SAATLER = ["09:00", "10:00", "11:00"];

/* ---------- Talep formu ---------- */
const form = document.getElementById("form");
if (form) {
  const sonuc = document.getElementById("sonuc");
  const btn = document.getElementById("gonder");
  const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

  // Doluluk tablosundan gelen ön seçim
  const q = new URLSearchParams(location.search);
  ["ogretmen_id", "gun", "saat"].forEach(k => { if (q.get(k)) form.elements[k].value = q.get(k); });

  const setErr = (name, msg) => {
    form.querySelector(`[data-for="${name}"]`).textContent = msg || "";
    form.elements[name].classList.toggle("bad", !!msg);
  };
  const dogrula = v => {
    const e = {};
    if (v.ad_soyad.length < 3 || v.ad_soyad.length > 60) e.ad_soyad = "Ad Soyad 3–60 karakter olmalı.";
    if (!EMAIL_RE.test(v.email)) e.email = "Geçerli bir e-posta girin.";
    if (!v.ogretmen_id) e.ogretmen_id = "Bir öğretmen seçin.";
    if (!v.gun) e.gun = "Bir gün seçin.";
    if (!v.saat) e.saat = "Bir saat seçin.";
    if (v.not_metni.length > 500) e.not_metni = "Not en fazla 500 karakter olabilir.";
    return e;
  };
  const goster = (tur, html) => { sonuc.hidden = false; sonuc.className = tur; sonuc.innerHTML = html; };

  form.addEventListener("submit", async ev => {
    ev.preventDefault();
    const v = Object.fromEntries(new FormData(form));
    Object.keys(v).forEach(k => v[k] = String(v[k]).trim());
    const errs = dogrula(v);
    ["ad_soyad", "email", "ogretmen_id", "gun", "saat", "not_metni"].forEach(k => setErr(k, errs[k]));
    sonuc.hidden = true;
    if (Object.keys(errs).length) return;

    btn.disabled = true; const eski = btn.textContent; btn.textContent = "Gönderiliyor…";
    try {
      const r = await fetch("/api/talepler", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(v)
      });
      const d = await r.json().catch(() => ({}));
      if (r.status === 201 && d.ok) {            // başarı yalnızca 201'de gösterilir
        goster("ok", d.mesaj); form.reset();
      } else if (r.status === 409) {
        goster("fail", `${d.hata} <a href="/doluluk">Boş saatleri gör</a>`);
      } else {
        goster("fail", d.hata || "Kayıt oluşturulamadı, lütfen tekrar deneyin.");
      }
    } catch {
      goster("fail", "Kayıt oluşturulamadı, lütfen tekrar deneyin.");
    } finally {
      btn.disabled = false; btn.textContent = eski;
    }
  });
}

/* ---------- Doluluk tablosu ---------- */
const tablo = document.getElementById("tablo");
if (tablo) {
  const yukle = async () => {
    try {
      const d = await (await fetch("/api/talepler/doluluk", { cache: "no-store" })).json();
      const map = {};
      d.slotlar.forEach(s => map[`${s.ogretmen_id}|${s.gun}|${s.saat}`] = s.dolu);
      const kolonlar = [];
      ["cumartesi", "pazar"].forEach(g => Object.keys(OGR).forEach(o => kolonlar.push([g, o])));
      tablo.tBodies[0].innerHTML = SAATLER.map(saat => `<tr><td class="saat">${saat}</td>` +
        kolonlar.map(([g, o]) => {
          const et = `${GUN_KISA[g]} (${OGR[o]})`;
          return map[`${o}|${g}|${saat}`]
            ? `<td class="dolu" data-label="${et}">DOLU</td>`
            : `<td class="bos"><a data-label="${et}" href="/?ogretmen_id=${o}&gun=${g}&saat=${saat}#talep-formu">BOŞ</a></td>`;
        }).join("") + "</tr>").join("");
      document.getElementById("ozet").textContent = `${d.toplam - d.dolu} boş saat kaldı (toplam ${d.toplam}).`;
    } catch {
      document.getElementById("ozet").textContent = "Veri alınamadı, yeniden denenecek.";
    }
  };
  yukle(); setInterval(yukle, 15000);
}
