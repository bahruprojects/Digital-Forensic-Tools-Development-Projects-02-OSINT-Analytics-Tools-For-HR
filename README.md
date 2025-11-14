# Digital-Forensic-Tools-Development-Projects-02-OSINT-Analytics-Tools-For-Talent-Acquisition (LinkedIn Profile Scraper Pro 🔍)

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)]()

Sebuah tool Python yang powerful untuk melakukan scraping data profil LinkedIn secara komprehensif. Tool ini dapat mengekstrak informasi profil, aktivitas, koneksi, interests, dan media dari profil LinkedIn.

## ⚠️ Disclaimer Penting

**PERINGATAN**: Penggunaan scraper ini mungkin melanggar [Terms of Service LinkedIn](https://www.linkedin.com/legal/user-agreement). Tool ini dibuat untuk:
- Tujuan edukasi dan penelitian
- Pembelajaran web scraping
- Penggunaan yang etis dan legal

**Harap gunakan dengan bijak dan tanggung jawab. Hormati privasi dan hak orang lain.**

## ✨ Fitur Utama

### 📊 Data yang Dapat Dikumpulkan

- ✅ **Informasi Profil Dasar**
  - Nama, headline, lokasi
  - About section
  - Foto profil (download resolusi tinggi)

- ✅ **Aktivitas**
  - Posts
  - Comments
  - Reactions

- ✅ **Koneksi** (memerlukan login)
  - Connections
  - Followers
  - Following

- ✅ **Interests**
  - Top Voices
  - Companies
  - Groups
  - Newsletters
  - Schools

- ✅ **Media**
  - Download semua gambar yang diupload
  - Resolusi tinggi

- ✅ **Export Data**
  - Format JSON
  - Format CSV
  - Profile PDF/HTML
  - ZIP Archive

## 🚀 Instalasi

### Prerequisites

- Python 3.7 atau lebih baru
- Google Chrome browser
- ChromeDriver (otomatis terinstall via webdriver-manager)

### Install Dependencies

```bash
# Clone repository
git clone https://github.com/yourusername/linkedin-scraper-pro.git
cd linkedin-scraper-pro

# Install required packages
pip install -r requirements.txt
```

### Requirements.txt

```
selenium>=4.0.0
webdriver-manager>=3.8.0
requests>=2.28.0
pdfkit>=1.0.0
Pillow>=9.0.0
```

### Optional: Install wkhtmltopdf (untuk PDF export)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install wkhtmltopdf
```

**macOS:**
```bash
brew install wkhtmltopdf
```

**Windows:**
Download dari [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)

## 📖 Cara Penggunaan

### Mode Interaktif

Jalankan script langsung untuk mode interaktif:

```bash
python linkedin_scraper.py
```

Anda akan diminta untuk memasukkan:
1. URL profil LinkedIn target
2. Kredensial login (opsional, untuk akses koneksi)
3. Pilihan headless mode

### Mode Programmatic

```python
from linkedin_scraper import LinkedInScraperPro

# Tanpa login (data publik saja)
scraper = LinkedInScraperPro(
    profile_url="https://www.linkedin.com/in/username/",
    headless=False,
    max_scrolls=15
)

# Dengan login (akses data lengkap)
scraper = LinkedInScraperPro(
    profile_url="https://www.linkedin.com/in/username/",
    email="your-email@example.com",
    password="your-password",
    headless=True,
    max_scrolls=15
)

# Jalankan scraping lengkap
scraper.scrape_all()
```

### Scraping Selektif

Anda juga dapat menjalankan fungsi scraping secara terpisah:

```python
scraper = LinkedInScraperPro(profile_url="https://www.linkedin.com/in/username/")
scraper.start_driver()

# Scrape hanya profil dasar
profile_info = scraper.scrape_basic_profile_info()

# Scrape hanya posts
posts = scraper.scrape_activity("posts")

# Scrape hanya connections (memerlukan login)
connections = scraper.scrape_connections("connections")

# Download hanya foto profil
scraper.download_profile_image()

# Tutup browser
scraper.driver.quit()
```

## 📁 Struktur Output

Setelah scraping selesai, data akan tersimpan dalam folder `linkedin_data/`:

```
linkedin_data/
├── profile.pdf                 # Profile dalam format PDF
├── profile.html               # Profile dalam format HTML (fallback)
├── profile_picture.jpg        # Foto profil
├── profile_info.json          # Informasi profil
├── posts.csv                  # Posts dalam CSV
├── posts.json                 # Posts dalam JSON
├── comments.csv               # Comments
├── comments.json
├── reactions.csv              # Reactions
├── reactions.json
├── connections.csv            # Connections (jika login)
├── connections.json
├── followers.csv
├── followers.json
├── following.csv
├── following.json
├── top-voices.csv             # Interests
├── top-voices.json
├── companies.csv
├── companies.json
├── groups.csv
├── groups.json
├── newsletters.csv
├── newsletters.json
├── schools.csv
├── schools.json
├── media/                     # Folder untuk media downloads
│   ├── media_1.jpg
│   ├── media_2.jpg
│   └── ...
├── scraping_summary.json      # Summary report
└── scraper.log                # Log file

linkedin_data_archive.zip      # ZIP archive dari semua data
```

## ⚙️ Konfigurasi

### Parameters

| Parameter | Tipe | Default | Deskripsi |
|-----------|------|---------|-----------|
| `profile_url` | str | **Required** | URL profil LinkedIn target |
| `email` | str | None | Email untuk login LinkedIn |
| `password` | str | None | Password untuk login LinkedIn |
| `headless` | bool | False | Jalankan browser tanpa GUI |
| `max_scrolls` | int | 15 | Maksimal scroll untuk load konten |

### Logging

Log disimpan di `linkedin_data/scraper.log` dengan format:

```
2025-11-14 10:30:15 - INFO - WebDriver initialized successfully
2025-11-14 10:30:20 - INFO - Login successful!
2025-11-14 10:30:25 - INFO - Collecting basic profile info...
```

## 🛡️ Anti-Detection Features

Scraper ini dilengkapi dengan berbagai fitur anti-detection:

- ✅ Random delays antar request
- ✅ User-agent yang natural
- ✅ Stealth mode (menyembunyikan webdriver)
- ✅ Retry mechanism dengan backoff
- ✅ Human-like scrolling behavior
- ✅ Automatic CAPTCHA detection

## ⚡ Tips & Best Practices

### Untuk Hasil Optimal

1. **Gunakan akun LinkedIn real** untuk login (bukan akun bot)
2. **Jangan scrape terlalu banyak profil** dalam waktu singkat
3. **Tambahkan delay** antara scraping berbeda profil
4. **Gunakan headless=False** untuk monitoring pertama kali
5. **Check logs** untuk mendeteksi error atau CAPTCHA

### Menghindari Blokir

```python
import time

profiles = [
    "https://www.linkedin.com/in/profile1/",
    "https://www.linkedin.com/in/profile2/",
    "https://www.linkedin.com/in/profile3/"
]

for profile_url in profiles:
    scraper = LinkedInScraperPro(profile_url, headless=True)
    scraper.scrape_all()
    
    # Delay antar profil
    time.sleep(random.uniform(300, 600))  # 5-10 menit
```

## 🐛 Troubleshooting

### ChromeDriver Error

**Problem:** `SessionNotCreatedException: session not created`

**Solution:**
```bash
pip install --upgrade webdriver-manager
```

### CAPTCHA Detected

**Problem:** LinkedIn meminta CAPTCHA

**Solution:**
- Jalankan dengan `headless=False`
- Selesaikan CAPTCHA manual
- Script akan otomatis lanjut setelah CAPTCHA selesai

### Login Failed

**Problem:** Login selalu gagal

**Solution:**
- Pastikan kredensial benar
- Gunakan browser biasa untuk login manual dulu
- LinkedIn mungkin memerlukan verifikasi tambahan
- Coba dengan akun yang jarang digunakan untuk automation

### Element Not Found

**Problem:** `NoSuchElementException`

**Solution:**
- LinkedIn sering update UI mereka
- Check XPATH selector di kode
- Increase `max_scrolls` parameter
- Tambahkan lebih banyak timeout

## 🔒 Keamanan & Privacy

### Credentials Safety

⚠️ **JANGAN** hardcode credentials dalam kode:

```python
# ❌ BAD
scraper = LinkedInScraperPro(
    profile_url="...",
    email="myemail@gmail.com",  # Jangan!
    password="mypassword123"     # Jangan!
)

# ✅ GOOD - Gunakan environment variables
import os

scraper = LinkedInScraperPro(
    profile_url="...",
    email=os.getenv('LINKEDIN_EMAIL'),
    password=os.getenv('LINKEDIN_PASSWORD')
)
```

### Data Protection

- Jangan share data scraping ke publik
- Enkripsi data sensitif
- Hapus data setelah selesai digunakan
- Ikuti GDPR dan regulasi data privacy

## 📝 Legal Notice

Tool ini dibuat untuk keperluan:
- ✅ Edukasi dan pembelajaran
- ✅ Penelitian akademis
- ✅ Personal data backup
- ❌ Commercial purposes
- ❌ Data harvesting massal
- ❌ Spam atau harassment

**Pengguna bertanggung jawab penuh** atas penggunaan tool ini.

## 🤝 Contributing

Contributions, issues, dan feature requests sangat diterima!

1. Fork project ini
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

Project ini dibuat untuk **tujuan edukasi**. Gunakan dengan bijak dan tanggung jawab.

## 👨‍💻 Author

Dibuat dengan ❤️ untuk komunitas Python & Web Scraping

## 🙏 Acknowledgments

- [Selenium](https://www.selenium.dev/) - Web automation framework
- [Webdriver Manager](https://github.com/SergeyPirogov/webdriver_manager) - Automatic ChromeDriver management
- Komunitas Python Indonesia

---

**⭐ Jika tool ini berguna, jangan lupa beri star di GitHub!**

**📧 Questions?** Silakan buka issue atau contact maintainer.

**⚖️ Disclaimer:** Tool ini tidak berafiliasi dengan LinkedIn Corporation. Gunakan sesuai dengan Terms of Service LinkedIn dan hukum yang berlaku.
