# Canlı Portföy Takip

Bu repo, `transactions.json`'a girdiğin işlemlerden BIST/TEFAS/altın-gümüş
pozisyonlarını hesaplar, `borsapy` ile güncel fiyatları çeker ve
arkadaşlarınla paylaşabileceğin bir canlı dashboard'a (GitHub Pages) yansıtır.

## Kurulum (bir kere yapılacak)

1. **GitHub'da yeni bir public repo oluştur** (örn. `bist-portfolio-takip`).
2. Bu klasördeki tüm dosyaları o repoya yükle:
   - Web arayüzünden: repo sayfasında **Add file > Upload files**, tüm
     dosya ve klasörleri sürükle-bırak, commit et.
   - Ya da terminalden:
     ```
     git init
     git add .
     git commit -m "ilk kurulum"
     git branch -M main
     git remote add origin https://github.com/KULLANICI_ADIN/REPO_ADIN.git
     git push -u origin main
     ```
3. **Actions'a yazma izni ver** (çok önemli, yoksa otomatik commit başarısız olur):
   Repo **Settings > Actions > General > Workflow permissions** →
   **"Read and write permissions"** seçip Save'e bas.
4. **GitHub Pages'i aç**: Repo **Settings > Pages** →
   Source: **Deploy from a branch**, Branch: **main**, klasör: **/ (root)** → Save.
   Birkaç dakika sonra sana bir link verecek: `https://KULLANICI_ADIN.github.io/REPO_ADIN/`
   — arkadaşlarına bu linki atacaksın.
5. **İlk veriyi çektirmek için**: repo **Actions** sekmesi → soldan
   "Portföyü Güncelle" workflow'u → **Run workflow** butonuyla elle tetikle.
   Birkaç dakika içinde `portfolio.json` güncellenip commit'lenecek.

Bundan sonra Action otomatik olarak ~15 dakikada bir çalışıp fiyatları
güncelleyecek — hiçbir şey yapmana gerek yok.

## Yeni işlem eklemek

Alım/satım yaptığında `transactions.json` dosyasını aç (GitHub web
arayüzünde kalem ikonuyla düzenlenebilir) ve listeye yeni bir satır ekle:

```json
{
  "date": "2026-07-21",
  "symbol": "THYAO",
  "asset_type": "stock",
  "action": "Alış",
  "shares": 50,
  "price": 295.00
}
```

`asset_type` seçenekleri:
- `stock` → BIST hissesi (sembol: `GARAN`, `THYAO`, `ASELS` gibi)
- `fund` → TEFAS fonu (sembol: fon kodu, örn. `YAY`, `AAK`)
- `fx` → döviz/altın/gümüş (örn. `gram-altin`, `USD`, `gram-gumus`)
- `crypto` → kripto (örn. `BTCTRY`)

`action`: `"Alış"` veya `"Satış"`.

Dosyayı kaydedip commit ettiğinde workflow otomatik tetiklenir (push
trigger tanımlı), birkaç dakika içinde site güncellenir.

## Dosyalar

- `transactions.json` — elle güncellediğin işlem listesi
- `scripts/build_portfolio.py` — fiyatları çekip `portfolio.json`'u üreten script
- `portfolio.json` — otomatik üretilen, sitenin okuduğu veri dosyası
- `index.html` — arkadaşlarının göreceği dashboard
- `.github/workflows/update.yml` — zamanlanmış otomatik çalıştırma

## Notlar

- BIST/TEFAS/TradingView verileri ~15 dakika gecikmeli gelir (borsapy'nin
  ücretsiz kaynağının doğal sınırı) — arkadaş grubuna göstermek için fazlasıyla yeterli.
- `borsapy` kişisel kullanım için tasarlanmıştır, ticari amaçla kullanılamaz.
