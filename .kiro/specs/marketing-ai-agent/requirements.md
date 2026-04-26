# Dokumen Persyaratan: Marketing AI Agent

## Pendahuluan

Marketing AI Agent adalah sistem multi-agen AI otonom yang dirancang untuk mengotomatisasi seluruh pipeline pemasaran digital CryptoMentor — mulai dari riset pasar, pembuatan konten berkonversi tinggi, distribusi otomatis, penangkapan lead, hingga closing penjualan.

Sistem ini terdiri dari enam agen spesialis yang bekerja dalam loop otomatis: Strategist Agent (analisa market & kampanye), Content Agent (generate konten berkonversi), Designer Agent (visual & branding), Distribution Agent (posting & A/B testing), Sales Agent (DM automation & closing), dan Analyst Agent (evaluasi performa & optimasi).

Agen ini memiliki pengetahuan penuh tentang ekosistem CryptoMentor — termasuk fitur AutoTrade, StackMentor, Scalping Mode, Sideways Micro-Scalping, multi-exchange (BingX, Binance, Bybit, Bitunix), sistem whitelabel, dan konten edukasi trading kripto — sehingga setiap konten yang dihasilkan relevan, akurat, dan selaras dengan produk.

---

## Glosarium

- **Marketing_Agent**: Sistem agen AI utama yang mengorkestrasikan seluruh pipeline pemasaran
- **Research_Engine**: Sub-agen yang bertanggung jawab melakukan riset topik dan tren
- **Content_Generator**: Sub-agen yang menghasilkan konten feed dan reels
- **Social_Publisher**: Sub-agen yang memposting konten ke platform media sosial
- **Feed_Content**: Konten statis berupa gambar + teks untuk feed Instagram/Facebook/TikTok
- **Reels_Content**: Konten video pendek (15–60 detik) untuk Instagram Reels, Facebook Reels, dan TikTok
- **Content_Calendar**: Jadwal konten yang direncanakan dan dikelola oleh agen
- **Brand_Context**: Kumpulan informasi produk CryptoMentor yang digunakan sebagai referensi pembuatan konten
- **Platform_Connector**: Modul integrasi dengan API media sosial (Instagram Graph API, Facebook Graph API, TikTok API)
- **AI_Provider**: Layanan AI yang digunakan (OpenAI, DeepSeek, Cerebras)
- **Approval_Queue**: Antrian konten yang menunggu persetujuan manusia sebelum dipublikasikan
- **Poster_Template**: Template HTML yang sudah ada di `marketing/templates/` untuk menghasilkan gambar konten
- **Strategist_Agent**: Agen yang menganalisa market sentiment, menentukan angle kampanye, dan target audiens
- **Content_Agent**: Agen yang menghasilkan skrip, caption, hook, dan konten berkonversi tinggi
- **Designer_Agent**: Agen opsional yang menghasilkan visual carousel, thumbnail, dan branding
- **Distribution_Agent**: Agen yang mengelola posting, penjadwalan, dan A/B testing konten
- **Sales_Agent**: Agen yang menangani DM automation, edukasi prospek, objection handling, dan closing
- **Analyst_Agent**: Agen yang mengevaluasi performa konten dan memberikan insight untuk optimasi
- **Audience_Segment**: Klasifikasi audiens berdasarkan tingkat kesiapan beli: Cold, Warm, atau Hot
- **Audience_Persona**: Profil audiens target berdasarkan psikografi: Beginner, Intermediate_Trader, Fear_Driven, atau Greed_Driven
- **PAS_Framework**: Struktur konten Problem → Agitate → Solution → CTA untuk konten berkonversi tinggi
- **Hook**: Kalimat pembuka konten yang dirancang untuk menghentikan scroll dan menarik perhatian
- **Lead**: Prospek yang telah menunjukkan ketertarikan dan masuk ke dalam funnel pemasaran
- **Funnel**: Alur perjalanan prospek dari awareness hingga konversi menjadi pengguna aktif
- **Landing_Page**: Halaman web yang dirancang khusus untuk mengkonversi pengunjung menjadi lead
- **Free_Value**: Konten atau layanan gratis (sinyal, insight, trial) yang digunakan sebagai lead magnet
- **Objection**: Keberatan prospek yang menghalangi keputusan pembelian (takut scam, takut rugi, dll.)
- **AB_Test**: Pengujian dua varian konten (Hook A vs Hook B) untuk menentukan mana yang lebih efektif
- **CTR**: Click-Through Rate — persentase orang yang mengklik dari total yang melihat konten
- **CAC**: Customer Acquisition Cost — biaya rata-rata untuk mendapatkan satu pengguna baru
- **Conversion_Rate**: Persentase lead yang berhasil dikonversi menjadi pengguna aktif
- **Scale_Decision**: Keputusan untuk meningkatkan distribusi konten yang performanya di atas threshold
- **Kill_Decision**: Keputusan untuk menghentikan distribusi konten yang performanya di bawah threshold

---

## Persyaratan

### Persyaratan 1: Manajemen Brand Context

**User Story:** Sebagai tim marketing CryptoMentor, saya ingin agen memiliki pengetahuan lengkap tentang semua fitur produk, sehingga konten yang dihasilkan selalu relevan dan akurat.

#### Kriteria Penerimaan

1. THE Marketing_Agent SHALL memuat Brand_Context dari file konfigurasi yang berisi deskripsi lengkap fitur CryptoMentor (AutoTrade, StackMentor, Scalping Mode, Sideways Micro-Scalping, multi-exchange, whitelabel, edukasi trading)
2. THE Marketing_Agent SHALL memuat data dari `marketing/content_calendar.json` sebagai referensi tema dan gaya konten yang sudah ada
3. THE Marketing_Agent SHALL memuat template dari `marketing/templates/` sebagai dasar pembuatan visual konten
4. WHEN Brand_Context diperbarui, THE Marketing_Agent SHALL memuat ulang konteks tersebut tanpa memerlukan restart sistem
5. IF file Brand_Context tidak ditemukan atau tidak dapat dibaca, THEN THE Marketing_Agent SHALL menampilkan pesan error yang deskriptif dan menghentikan proses pembuatan konten

---

### Persyaratan 2: Riset Topik Otomatis

**User Story:** Sebagai tim marketing, saya ingin agen secara otomatis menemukan topik yang relevan dan trending, sehingga konten yang dibuat selalu segar dan menarik audiens target.

#### Kriteria Penerimaan

1. WHEN Research_Engine dijalankan, THE Research_Engine SHALL menganalisis tren kripto terkini dari sumber berita dan data pasar yang tersedia
2. THE Research_Engine SHALL menghasilkan daftar minimal 5 topik konten yang relevan dengan produk CryptoMentor untuk setiap sesi riset
3. WHEN topik dihasilkan, THE Research_Engine SHALL mengklasifikasikan setiap topik ke dalam kategori: `product_highlight`, `crypto_education`, `trading_psychology`, `market_update`, atau `community`
4. THE Research_Engine SHALL memprioritaskan topik berdasarkan relevansi dengan fitur aktif CryptoMentor (AutoTrade, StackMentor, dll.)
5. IF Research_Engine tidak dapat mengakses sumber data eksternal, THEN THE Research_Engine SHALL menggunakan topik fallback dari Brand_Context yang sudah ada
6. THE Research_Engine SHALL menyimpan hasil riset ke database Supabase dengan timestamp untuk menghindari duplikasi topik dalam 7 hari terakhir

---

### Persyaratan 3: Pembuatan Konten Feed

**User Story:** Sebagai tim marketing, saya ingin agen menghasilkan konten feed berkualitas tinggi (gambar + caption) secara otomatis, sehingga saya tidak perlu membuat konten secara manual setiap hari.

#### Kriteria Penerimaan

1. WHEN topik feed dipilih, THE Content_Generator SHALL menghasilkan caption teks dalam Bahasa Indonesia dengan panjang 150–300 karakter untuk feed Instagram/Facebook/TikTok
2. THE Content_Generator SHALL menghasilkan gambar feed berukuran 1080×1080 piksel (format square) menggunakan Poster_Template yang sudah ada
3. THE Content_Generator SHALL menghasilkan gambar feed berukuran 1080×1350 piksel (format portrait) untuk konten edukasi
4. WHEN menghasilkan konten, THE Content_Generator SHALL memilih template yang sesuai: `product.html` untuk konten produk dan `education.html` untuk konten edukasi
5. THE Content_Generator SHALL mengisi variabel template (headline, subtext, eyebrow, pillars/points, cta) menggunakan AI_Provider berdasarkan topik dan Brand_Context
6. THE Content_Generator SHALL menghasilkan minimal 3–5 hashtag relevan untuk setiap konten feed
7. IF konten yang dihasilkan mengandung klaim finansial yang tidak dapat diverifikasi, THEN THE Content_Generator SHALL menambahkan disclaimer: "Bukan saran keuangan. Trading mengandung risiko."
8. THE Content_Generator SHALL menyimpan file gambar hasil render ke direktori `marketing/output/feeds/` dengan nama file berformat `{tanggal}_{tema}_{platform}.png`

---

### Persyaratan 4: Pembuatan Konten Reels

**User Story:** Sebagai tim marketing, saya ingin agen menghasilkan skrip dan aset video reels secara otomatis, sehingga konten video dapat diproduksi dengan cepat dan konsisten.

#### Kriteria Penerimaan

1. WHEN topik reels dipilih, THE Content_Generator SHALL menghasilkan skrip video dengan durasi target 15–60 detik dalam Bahasa Indonesia
2. THE Content_Generator SHALL membagi skrip menjadi segmen: hook (3–5 detik), konten utama (10–45 detik), dan call-to-action (3–5 detik)
3. THE Content_Generator SHALL menghasilkan narasi teks untuk setiap segmen yang dapat digunakan sebagai voice-over atau teks overlay
4. THE Content_Generator SHALL menghasilkan deskripsi visual untuk setiap segmen (instruksi untuk editor atau tool video AI)
5. THE Content_Generator SHALL menghasilkan caption reels dalam Bahasa Indonesia dengan panjang 100–200 karakter beserta hashtag
6. THE Content_Generator SHALL menyimpan skrip reels ke direktori `marketing/output/reels/` dalam format JSON dengan struktur: `{segments, caption, hashtags, duration_target, topic, created_at}`
7. WHERE fitur text-to-video AI tersedia, THE Content_Generator SHALL menghasilkan video reels secara otomatis menggunakan layanan tersebut
8. IF durasi skrip yang dihasilkan melebihi 60 detik, THEN THE Content_Generator SHALL memotong konten dan memprioritaskan hook dan call-to-action

---

### Persyaratan 5: Antrian Persetujuan Konten

**User Story:** Sebagai manajer marketing, saya ingin mereview konten sebelum dipublikasikan, sehingga saya dapat memastikan kualitas dan kesesuaian konten dengan strategi brand.

#### Kriteria Penerimaan

1. WHEN konten feed atau reels selesai dibuat, THE Marketing_Agent SHALL menempatkan konten tersebut ke Approval_Queue sebelum dipublikasikan
2. THE Marketing_Agent SHALL mengirimkan notifikasi ke Telegram admin dengan preview konten dan tombol Approve/Reject
3. WHEN admin menekan tombol Approve, THE Marketing_Agent SHALL memindahkan konten ke antrian publikasi
4. WHEN admin menekan tombol Reject, THE Marketing_Agent SHALL menandai konten sebagai ditolak dan mencatat alasan penolakan jika diberikan
5. WHILE konten berada di Approval_Queue lebih dari 24 jam tanpa tindakan, THE Marketing_Agent SHALL mengirimkan pengingat notifikasi ke admin
6. WHERE mode auto-publish diaktifkan oleh admin, THE Marketing_Agent SHALL mempublikasikan konten tanpa menunggu persetujuan manual
7. THE Marketing_Agent SHALL menyimpan status setiap konten (draft, pending_approval, approved, rejected, published) di database Supabase

---

### Persyaratan 6: Publikasi Otomatis ke Instagram

**User Story:** Sebagai tim marketing, saya ingin konten dipublikasikan otomatis ke Instagram, sehingga tidak perlu login manual setiap hari.

#### Kriteria Penerimaan

1. WHEN konten feed disetujui untuk Instagram, THE Social_Publisher SHALL mempublikasikan gambar beserta caption menggunakan Instagram Graph API
2. WHEN konten reels disetujui untuk Instagram, THE Social_Publisher SHALL mengunggah video dan mempublikasikannya sebagai Instagram Reels
3. THE Social_Publisher SHALL mendukung penjadwalan publikasi pada waktu yang ditentukan (format: ISO 8601)
4. IF Instagram Graph API mengembalikan error rate limit, THEN THE Social_Publisher SHALL menunda publikasi selama 15 menit dan mencoba ulang maksimal 3 kali
5. IF publikasi ke Instagram gagal setelah 3 percobaan, THEN THE Social_Publisher SHALL mengirimkan notifikasi error ke admin Telegram beserta detail error
6. THE Social_Publisher SHALL menyimpan Instagram post ID dan URL konten yang berhasil dipublikasikan ke database Supabase

---

### Persyaratan 7: Publikasi Otomatis ke Facebook

**User Story:** Sebagai tim marketing, saya ingin konten dipublikasikan otomatis ke Facebook Page CryptoMentor, sehingga jangkauan audiens lebih luas.

#### Kriteria Penerimaan

1. WHEN konten feed disetujui untuk Facebook, THE Social_Publisher SHALL mempublikasikan gambar beserta caption ke Facebook Page menggunakan Facebook Graph API
2. WHEN konten reels disetujui untuk Facebook, THE Social_Publisher SHALL mengunggah video dan mempublikasikannya sebagai Facebook Reels
3. THE Social_Publisher SHALL mendukung penjadwalan publikasi pada waktu yang ditentukan
4. IF Facebook Graph API mengembalikan error token expired, THEN THE Social_Publisher SHALL mengirimkan notifikasi ke admin untuk memperbarui access token
5. IF publikasi ke Facebook gagal setelah 3 percobaan, THEN THE Social_Publisher SHALL mengirimkan notifikasi error ke admin Telegram beserta detail error
6. THE Social_Publisher SHALL menyimpan Facebook post ID dan URL konten yang berhasil dipublikasikan ke database Supabase

---

### Persyaratan 8: Publikasi Otomatis ke TikTok

**User Story:** Sebagai tim marketing, saya ingin konten reels dipublikasikan otomatis ke TikTok, sehingga dapat menjangkau audiens yang lebih muda dan lebih luas.

#### Kriteria Penerimaan

1. WHEN konten reels disetujui untuk TikTok, THE Social_Publisher SHALL mengunggah video menggunakan TikTok Content Posting API
2. WHEN konten feed disetujui untuk TikTok, THE Social_Publisher SHALL mempublikasikan gambar sebagai TikTok photo post
3. THE Social_Publisher SHALL menyertakan caption dan hashtag yang sudah disesuaikan untuk algoritma TikTok
4. IF TikTok API mengembalikan error, THEN THE Social_Publisher SHALL mencatat error tersebut dan mencoba ulang maksimal 3 kali dengan interval 10 menit
5. IF publikasi ke TikTok gagal setelah 3 percobaan, THEN THE Social_Publisher SHALL mengirimkan notifikasi error ke admin Telegram beserta detail error
6. THE Social_Publisher SHALL menyimpan TikTok video ID dan URL konten yang berhasil dipublikasikan ke database Supabase

---

### Persyaratan 9: Penjadwalan Konten Otomatis

**User Story:** Sebagai tim marketing, saya ingin agen mengelola jadwal posting secara otomatis berdasarkan waktu optimal, sehingga konten mendapatkan engagement maksimal.

#### Kriteria Penerimaan

1. THE Marketing_Agent SHALL menghasilkan Content_Calendar mingguan secara otomatis dengan minimal 7 konten per minggu (campuran feed dan reels)
2. THE Marketing_Agent SHALL menjadwalkan posting pada waktu optimal: 07.00–09.00 WIB, 12.00–13.00 WIB, dan 19.00–21.00 WIB
3. THE Marketing_Agent SHALL mendistribusikan tipe konten secara seimbang: minimal 40% konten edukasi, minimal 30% konten produk, dan sisanya konten komunitas/psikologi trading
4. WHEN Content_Calendar dihasilkan, THE Marketing_Agent SHALL menyimpannya ke file `marketing/content_calendar.json` dan database Supabase
5. THE Marketing_Agent SHALL menghindari posting topik yang sama dalam rentang 7 hari pada platform yang sama
6. WHERE hari libur nasional Indonesia terdeteksi, THE Marketing_Agent SHALL menyesuaikan jadwal dan tema konten agar relevan dengan momen tersebut

---

### Persyaratan 10: Monitoring dan Pelaporan Performa

**User Story:** Sebagai tim marketing, saya ingin melihat laporan performa konten secara berkala, sehingga saya dapat mengoptimalkan strategi konten berdasarkan data.

#### Kriteria Penerimaan

1. THE Marketing_Agent SHALL mengumpulkan metrik performa konten (likes, comments, shares, reach, impressions) dari setiap platform setiap 24 jam
2. THE Marketing_Agent SHALL menghasilkan laporan mingguan yang mencakup: total konten dipublikasikan, total reach, konten dengan performa terbaik, dan rekomendasi topik untuk minggu berikutnya
3. THE Marketing_Agent SHALL mengirimkan laporan mingguan ke admin melalui Telegram setiap hari Senin pukul 08.00 WIB
4. IF metrik engagement suatu konten berada di bawah rata-rata 20%, THEN THE Marketing_Agent SHALL menandai tipe konten tersebut sebagai perlu dioptimasi
5. THE Marketing_Agent SHALL menyimpan semua data metrik ke tabel `marketing_analytics` di database Supabase
6. THE Marketing_Agent SHALL menggunakan data historis performa untuk meningkatkan relevansi topik riset pada sesi berikutnya

---

### Persyaratan 11: Konfigurasi dan Manajemen Kredensial

**User Story:** Sebagai developer, saya ingin semua kredensial API media sosial dikelola dengan aman, sehingga tidak ada risiko kebocoran data.

#### Kriteria Penerimaan

1. THE Marketing_Agent SHALL membaca semua kredensial API (Instagram, Facebook, TikTok, AI Provider) dari environment variables atau file `.env`
2. THE Marketing_Agent SHALL memvalidasi ketersediaan semua kredensial yang diperlukan saat startup
3. IF kredensial yang diperlukan tidak ditemukan saat startup, THEN THE Marketing_Agent SHALL menampilkan daftar environment variable yang hilang dan menghentikan proses
4. THE Marketing_Agent SHALL mendukung konfigurasi per-platform sehingga setiap platform dapat diaktifkan atau dinonaktifkan secara independen melalui environment variable `ENABLE_INSTAGRAM`, `ENABLE_FACEBOOK`, `ENABLE_TIKTOK`
5. THE Marketing_Agent SHALL merotasi penggunaan AI_Provider (OpenAI, DeepSeek, Cerebras) berdasarkan ketersediaan dan batas rate limit masing-masing provider
6. THE Marketing_Agent SHALL mencatat semua aktivitas publikasi ke log file dengan format yang dapat diaudit

---

### Persyaratan 12: Integrasi dengan Sistem CryptoMentor yang Ada

**User Story:** Sebagai developer, saya ingin Marketing Agent terintegrasi dengan infrastruktur CryptoMentor yang sudah ada, sehingga tidak perlu membangun infrastruktur baru dari nol.

#### Kriteria Penerimaan

1. THE Marketing_Agent SHALL menggunakan koneksi Supabase yang sudah ada (dari `website-backend/app/db/supabase.py`) untuk menyimpan data konten dan analitik
2. THE Marketing_Agent SHALL dapat dijalankan sebagai modul Python independen di direktori `marketing/agent/`
3. THE Marketing_Agent SHALL menggunakan AI provider yang sudah dikonfigurasi di sistem (OpenAI, DeepSeek, Cerebras) melalui pola yang konsisten dengan `Bismillah/app/providers/`
4. WHERE Telegram admin bot tersedia, THE Marketing_Agent SHALL mengirimkan notifikasi dan laporan melalui bot Telegram yang sudah ada
5. THE Marketing_Agent SHALL menggunakan file `marketing/content_calendar.json` yang sudah ada sebagai seed data awal untuk Content_Calendar
6. THE Marketing_Agent SHALL menggunakan template HTML yang sudah ada di `marketing/templates/` dan `marketing/generate.js` untuk rendering gambar konten

---

### Persyaratan 13: Audience Intelligence Engine

**User Story:** Sebagai tim marketing CryptoMentor, saya ingin agen menganalisa dan mensegmentasi target audiens kripto secara otomatis, sehingga setiap konten dan pesan dapat disesuaikan dengan psikografi dan tingkat kesiapan beli audiens.

#### Kriteria Penerimaan

1. THE Strategist_Agent SHALL mengklasifikasikan setiap audiens ke dalam salah satu dari empat Audience_Persona: `Beginner` (belum pernah trading), `Intermediate_Trader` (sudah trading tapi belum konsisten profit), `Fear_Driven` (takut rugi/loss), atau `Greed_Driven` (FOMO, ingin cepat kaya)
2. THE Strategist_Agent SHALL mensegmentasi audiens ke dalam tiga Audience_Segment berdasarkan tingkat kesiapan beli: `Cold` (belum kenal produk), `Warm` (sudah tahu tapi belum yakin), atau `Hot` (siap mendaftar/membeli)
3. WHEN Strategist_Agent menganalisa audiens, THE Strategist_Agent SHALL menghasilkan profil persona yang mencakup: pain point utama, trigger emosi dominan (fear atau greed), dan pesan yang paling relevan untuk persona tersebut
4. THE Strategist_Agent SHALL memetakan pain point spesifik untuk setiap persona: `Beginner` → bingung cara entry; `Intermediate_Trader` → sering loss karena emosi; `Fear_Driven` → takut scam dan kehilangan modal; `Greed_Driven` → takut ketinggalan peluang profit
5. WHEN kampanye baru dibuat, THE Strategist_Agent SHALL menentukan trigger emosi yang digunakan: `fear` (takut rugi, takut ketinggalan), `greed` (potensi profit, FOMO), atau `security` (aman, terpercaya, terbukti)
6. THE Strategist_Agent SHALL menyimpan profil Audience_Persona dan Audience_Segment ke database Supabase untuk digunakan oleh Content_Agent dan Sales_Agent
7. IF data engagement historis tersedia, THEN THE Strategist_Agent SHALL memperbarui profil persona berdasarkan pola interaksi audiens yang sudah ada

---

### Persyaratan 14: High-Conversion Content Engine

**User Story:** Sebagai tim marketing, saya ingin agen menghasilkan konten yang tidak hanya informatif tetapi juga dirancang untuk mengkonversi audiens menjadi lead dan pengguna aktif, sehingga setiap konten yang dipublikasikan berkontribusi langsung pada pertumbuhan pengguna.

#### Kriteria Penerimaan

1. WHEN Content_Agent menghasilkan konten, THE Content_Agent SHALL menggunakan PAS_Framework sebagai struktur wajib: Problem (identifikasi masalah audiens) → Agitate (perkuat rasa sakit/urgensi) → Solution (tawarkan solusi CryptoMentor) → CTA (ajakan bertindak yang spesifik)
2. THE Content_Agent SHALL menghasilkan Hook untuk setiap konten yang memenuhi kriteria scroll-stopping: mengandung angka spesifik, pertanyaan provokatif, atau pernyataan kontraintuitif (contoh: "90% trader rugi karena ini…", "AI ini bantu kamu entry tanpa nebak")
3. THE Content_Agent SHALL menghasilkan minimal 10 konten per siklus kampanye dengan distribusi: 3 konten fear-based, 3 konten greed-based, dan 4 konten edukasi
4. THE Content_Agent SHALL mendukung format konten: Hook viral (1 kalimat pembuka), Carousel edukatif (5–10 slide), Short video script untuk Reels/TikTok (15–60 detik), Threads storytelling (5–10 tweet/post berantai), dan CTA standalone
5. WHEN menghasilkan konten untuk Audience_Persona `Fear_Driven`, THE Content_Agent SHALL menggunakan framing keamanan dan bukti sosial sebagai elemen utama
6. WHEN menghasilkan konten untuk Audience_Persona `Greed_Driven`, THE Content_Agent SHALL menggunakan framing peluang profit dan urgensi sebagai elemen utama
7. THE Content_Agent SHALL menghasilkan minimal 3 varian Hook untuk setiap topik konten agar dapat digunakan dalam AB_Test
8. IF konten yang dihasilkan tidak mengandung CTA yang eksplisit, THEN THE Content_Agent SHALL menambahkan CTA default yang sesuai dengan Audience_Segment target
9. THE Content_Agent SHALL menyimpan semua konten yang dihasilkan beserta metadata persona target ke database Supabase

---

### Persyaratan 15: Arsitektur Multi-Agen

**User Story:** Sebagai developer, saya ingin sistem marketing dibangun sebagai arsitektur multi-agen yang terkoordinasi, sehingga setiap agen dapat bekerja secara spesialis dan loop otomatis dapat berjalan tanpa intervensi manual.

#### Kriteria Penerimaan

1. THE Marketing_Agent SHALL mengorkestrasikan enam agen spesialis dalam loop otomatis: Strategist_Agent, Content_Agent, Designer_Agent (opsional), Distribution_Agent, Sales_Agent, dan Analyst_Agent
2. THE Strategist_Agent SHALL menjalankan langkah pertama setiap siklus: menganalisa market sentiment kripto terkini, menentukan angle kampanye, dan menetapkan target Audience_Persona untuk siklus tersebut
3. WHEN Strategist_Agent selesai, THE Content_Agent SHALL menghasilkan 10 konten sesuai distribusi yang ditetapkan (3 fear-based, 3 greed-based, 4 edukasi) berdasarkan angle dan persona yang ditentukan Strategist_Agent
4. WHEN konten selesai dibuat, THE Distribution_Agent SHALL mendistribusikan konten ke platform yang ditentukan dan menjalankan AB_Test secara otomatis
5. WHEN lead masuk ke funnel, THE Sales_Agent SHALL menangani follow-up, edukasi, dan proses closing secara otomatis
6. WHEN siklus distribusi selesai, THE Analyst_Agent SHALL mengevaluasi performa semua konten dan menghasilkan insight untuk siklus berikutnya
7. WHEN Analyst_Agent selesai, THE Strategist_Agent SHALL menerima feedback dari Analyst_Agent dan menyesuaikan strategi untuk siklus berikutnya (loop kembali ke langkah 2)
8. THE Marketing_Agent SHALL menyimpan status setiap agen dan hasil setiap langkah ke database Supabase untuk keperluan audit dan debugging
9. IF salah satu agen mengalami error, THEN THE Marketing_Agent SHALL mencatat error tersebut, mengirimkan notifikasi ke admin Telegram, dan melanjutkan loop dengan agen berikutnya tanpa menghentikan seluruh sistem

---

### Persyaratan 16: A/B Testing Framework

**User Story:** Sebagai tim marketing, saya ingin sistem secara otomatis menguji berbagai varian konten dan menentukan mana yang paling efektif, sehingga keputusan optimasi konten didasarkan pada data bukan asumsi.

#### Kriteria Penerimaan

1. THE Distribution_Agent SHALL menjalankan AB_Test untuk setiap batch konten baru dengan membandingkan minimal dua varian: Hook A vs Hook B, atau format edukasi vs format storytelling
2. WHEN AB_Test dijalankan, THE Distribution_Agent SHALL mendistribusikan varian secara merata ke audiens yang setara dan mencatat waktu posting, platform, dan Audience_Segment yang ditarget
3. THE Distribution_Agent SHALL mengumpulkan metrik AB_Test selama minimal 24 jam sebelum menentukan pemenang: varian dengan CTR lebih tinggi dinyatakan sebagai pemenang
4. WHEN pemenang AB_Test ditentukan, THE Analyst_Agent SHALL mencatat pola konten pemenang (tipe hook, format, trigger emosi) ke database Supabase sebagai referensi untuk Content_Agent pada siklus berikutnya
5. THE Distribution_Agent SHALL mendukung AB_Test untuk variabel: tipe Hook (fear vs greed), format konten (carousel vs video script), waktu posting (pagi vs malam), dan panjang caption (pendek vs panjang)
6. IF salah satu varian AB_Test mendapatkan CTR di bawah 1% setelah 48 jam, THEN THE Analyst_Agent SHALL menandai varian tersebut sebagai Kill_Decision dan menghentikan distribusinya
7. THE Marketing_Agent SHALL menghasilkan laporan AB_Test mingguan yang mencakup semua pengujian yang berjalan, hasil, dan rekomendasi untuk Content_Agent

---

### Persyaratan 17: Lead Capture System

**User Story:** Sebagai tim marketing, saya ingin sistem secara otomatis mengkonversi penonton konten menjadi lead yang masuk ke funnel, sehingga ada alur yang jelas dari awareness hingga konversi pengguna aktif.

#### Kriteria Penerimaan

1. THE Marketing_Agent SHALL menghasilkan Free_Value sebagai lead magnet untuk setiap kampanye: sinyal trading gratis, insight market gratis, atau akses trial fitur premium
2. THE Content_Agent SHALL menyertakan CTA yang mengarahkan audiens ke Funnel melalui link in bio, DM, atau Telegram channel untuk setiap konten yang dipublikasikan
3. THE Marketing_Agent SHALL menghasilkan konten Landing_Page menggunakan AI_Provider dengan struktur: headline yang menarik, deskripsi Free_Value, social proof, dan form pendaftaran
4. WHEN pengunjung mengakses Landing_Page, THE Marketing_Agent SHALL mencatat data lead (platform asal, konten yang diklik, timestamp) ke database Supabase
5. THE Content_Agent SHALL menghasilkan copywriting Landing_Page menggunakan PAS_Framework yang disesuaikan dengan Audience_Persona target kampanye
6. WHEN lead baru masuk ke Funnel, THE Sales_Agent SHALL menerima notifikasi dan memulai alur follow-up dalam waktu maksimal 1 jam
7. THE Marketing_Agent SHALL melacak Conversion_Rate dari setiap sumber lead (Instagram, TikTok, Threads) dan menyimpan data tersebut ke tabel `marketing_leads` di database Supabase
8. IF Conversion_Rate dari suatu platform turun di bawah 2% selama 7 hari berturut-turut, THEN THE Analyst_Agent SHALL menandai platform tersebut untuk direview dan mengirimkan rekomendasi perbaikan ke admin

---

### Persyaratan 18: Conversion Agent (Sales Brain)

**User Story:** Sebagai tim marketing, saya ingin agen AI menangani proses follow-up dan closing secara otomatis dengan pendekatan natural (bukan hard selling), sehingga lead dapat dikonversi menjadi pengguna aktif tanpa memerlukan tim sales manusia untuk setiap interaksi.

#### Kriteria Penerimaan

1. THE Sales_Agent SHALL mengirimkan pesan follow-up pertama ke lead baru dalam waktu maksimal 1 jam setelah lead masuk ke Funnel melalui DM Instagram, WhatsApp, atau Telegram
2. THE Sales_Agent SHALL menggunakan pendekatan conversational (bukan hard selling): memulai dengan pertanyaan untuk memahami kebutuhan lead, memberikan edukasi relevan, dan menawarkan solusi secara natural
3. THE Sales_Agent SHALL menangani minimal lima objection umum dengan respons yang sudah dikurasi: "Takut scam" → bukti sosial + transparansi; "Bisa rugi?" → edukasi risk management + fitur stop loss; "Worth it gak?" → perbandingan nilai + testimoni; "Ribet gak setupnya?" → panduan 5 menit + demo; "Gratis beneran?" → konfirmasi + penjelasan model bisnis
4. WHEN Sales_Agent mendeteksi sinyal kesiapan beli dari lead (pertanyaan tentang cara daftar, harga, atau fitur spesifik), THE Sales_Agent SHALL beralih ke mode closing dengan menawarkan langkah konkret berikutnya
5. THE Sales_Agent SHALL mengklasifikasikan setiap lead ke dalam Audience_Segment yang sesuai (Cold/Warm/Hot) berdasarkan respons dan interaksi, dan memperbarui klasifikasi tersebut di database Supabase
6. WHEN lead tidak merespons dalam 48 jam, THE Sales_Agent SHALL mengirimkan satu pesan follow-up lanjutan dengan Free_Value baru sebagai re-engagement
7. IF lead secara eksplisit menyatakan tidak tertarik, THEN THE Sales_Agent SHALL menghentikan follow-up dan menandai lead sebagai `opted_out` di database Supabase
8. THE Sales_Agent SHALL mencatat semua interaksi dengan lead (pesan terkirim, respons diterima, status konversi) ke tabel `marketing_leads` di database Supabase
9. THE Sales_Agent SHALL menghasilkan laporan konversi harian yang mencakup: jumlah lead baru, jumlah follow-up terkirim, jumlah closing berhasil, dan Conversion_Rate per Audience_Persona

---

### Persyaratan 19: Distribution Automation dengan Optimasi Waktu

**User Story:** Sebagai tim marketing, saya ingin konten didistribusikan secara otomatis ke semua platform pada waktu optimal berdasarkan data engagement historis, sehingga setiap konten mendapatkan jangkauan maksimal.

#### Kriteria Penerimaan

1. THE Distribution_Agent SHALL memposting konten secara otomatis ke Instagram, Threads, dan TikTok sesuai jadwal yang ditentukan oleh Strategist_Agent
2. THE Distribution_Agent SHALL menentukan waktu posting optimal berdasarkan data engagement historis per platform: jika data belum tersedia, gunakan default 07.00–09.00 WIB, 12.00–13.00 WIB, dan 19.00–21.00 WIB
3. WHEN data engagement historis tersedia untuk minimal 30 konten per platform, THE Distribution_Agent SHALL memperbarui jadwal posting optimal secara otomatis berdasarkan analisa Analyst_Agent
4. THE Distribution_Agent SHALL mendukung posting konten yang sama ke beberapa platform secara bersamaan dengan caption yang disesuaikan per platform (Instagram, Threads, TikTok memiliki gaya caption berbeda)
5. THE Distribution_Agent SHALL menjalankan AB_Test posting secara otomatis: Hook A diposting pada batch pertama, Hook B diposting 2 jam kemudian ke segmen audiens yang setara
6. IF Distribution_Agent gagal memposting ke suatu platform setelah 3 percobaan, THEN THE Distribution_Agent SHALL menandai konten tersebut sebagai `failed` dan mengirimkan notifikasi ke admin Telegram
7. THE Distribution_Agent SHALL menyimpan log semua aktivitas posting (platform, waktu, status, post ID) ke database Supabase

---

### Persyaratan 20: Analytics & Optimization Brain

**User Story:** Sebagai tim marketing, saya ingin sistem secara otomatis menganalisa performa semua konten dan membuat keputusan scale/kill berdasarkan data, sehingga anggaran dan upaya marketing selalu dialokasikan ke konten yang terbukti efektif.

#### Kriteria Penerimaan

1. THE Analyst_Agent SHALL melacak metrik utama untuk setiap konten yang dipublikasikan: CTR, Conversion_Rate, CAC, reach, impressions, engagement rate, dan jumlah lead yang dihasilkan
2. THE Analyst_Agent SHALL membuat Scale_Decision untuk konten yang memenuhi kriteria: CTR di atas 3% ATAU Conversion_Rate di atas 5% — konten tersebut akan didistribusikan ulang dengan frekuensi lebih tinggi
3. THE Analyst_Agent SHALL membuat Kill_Decision untuk konten yang tidak memenuhi kriteria: CTR di bawah 1% setelah 48 jam DAN engagement rate di bawah rata-rata 20% — konten tersebut dihentikan distribusinya
4. WHEN Analyst_Agent menyelesaikan evaluasi siklus, THE Analyst_Agent SHALL menghasilkan insight terstruktur untuk Strategist_Agent: tipe konten mana yang paling efektif, Audience_Persona mana yang paling responsif, dan angle kampanye mana yang harus diprioritaskan
5. THE Analyst_Agent SHALL menghitung CAC per platform dan per Audience_Persona setiap minggu, dan menyimpan data tersebut ke tabel `marketing_analytics` di database Supabase
6. THE Analyst_Agent SHALL menghasilkan laporan performa mingguan yang mencakup: total reach, total lead, Conversion_Rate per platform, CAC, konten dengan Scale_Decision, konten dengan Kill_Decision, dan rekomendasi strategi untuk minggu berikutnya
7. THE Marketing_Agent SHALL mengirimkan laporan performa mingguan ke admin melalui Telegram setiap hari Senin pukul 08.00 WIB
8. WHEN Analyst_Agent mendeteksi penurunan Conversion_Rate lebih dari 30% dibandingkan minggu sebelumnya, THE Analyst_Agent SHALL mengirimkan alert ke admin Telegram dan meminta Strategist_Agent untuk menjalankan analisa ulang segera
9. THE Analyst_Agent SHALL menggunakan data performa historis untuk melatih preferensi konten: pola hook yang berhasil, format yang efektif per Audience_Persona, dan waktu posting optimal per platform — data ini digunakan sebagai input untuk Content_Agent pada siklus berikutnya
