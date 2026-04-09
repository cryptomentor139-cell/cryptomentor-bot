# Rencana Implementasi: Marketing AI Agent

## Ikhtisar

Implementasi sistem multi-agen AI otonom untuk mengotomatisasi pipeline pemasaran digital CryptoMentor. Sistem dibangun sebagai modul Python independen di `marketing/agent/` dengan enam agen spesialis yang bekerja dalam loop berkelanjutan.

## Tugas

- [x] 1. Setup struktur proyek dan konfigurasi dasar
  - Buat direktori `marketing/agent/` beserta semua subdirektori (`agents/`, `core/`, `publishers/`, `db/`)
  - Buat `marketing/agent/requirements.txt` dengan dependensi: `supabase`, `openai`, `httpx`, `elevenlabs`, `hypothesis`, `python-dotenv`, `apscheduler`
  - Buat `marketing/agent/config.py` yang membaca semua environment variables (Instagram, Facebook, TikTok, AI providers, Supabase, Telegram, video generation) dan memvalidasi ketersediaannya saat startup — tampilkan daftar env var yang hilang jika ada yang tidak ditemukan
    - Validasi env vars tambahan: `KLING_AI_API_KEY`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `ENABLE_VIDEO_GENERATION`
  - Buat `marketing/agent/brand_context.json` dengan data lengkap produk CryptoMentor (AutoTrade, StackMentor, Scalping Mode, Sideways Micro-Scalping, multi-exchange, whitelabel, edukasi trading)
  - _Persyaratan: 1.1, 1.2, 1.3, 11.1, 11.2, 11.3, 12.2_

- [x] 2. Implementasi database schema dan koneksi Supabase
  - [x] 2.1 Buat `marketing/agent/db/setup_marketing.sql` dengan semua tabel: `marketing_campaigns`, `marketing_content`, `marketing_publications`, `marketing_leads`, `marketing_lead_interactions`, `marketing_analytics`, `marketing_ab_tests`, `marketing_audience_personas`, `marketing_research_topics`
    - Pastikan semua constraint CHECK, foreign key, dan default value sesuai desain
    - Tabel `marketing_leads`: field `contact_type` hanya menerima nilai `telegram` (hapus `instagram_dm` dan `whatsapp`), tambahkan field `telegram_chat_id BIGINT` untuk identifikasi lead di Telegram
    - _Persyaratan: 2.6, 5.7, 6.6, 7.6, 8.6, 10.5, 13.6, 14.9, 15.8, 16.4, 17.7, 18.8, 19.7, 20.5_

  - [x]* 2.2 Tulis property test untuk round-trip status konten
    - **Properti 11: Round-Trip Status Konten**
    - **Memvalidasi: Persyaratan 5.7**

- [x] 3. Implementasi Content Engine dan Audience Intelligence (core)
  - [x] 3.1 Buat `marketing/agent/core/audience_intelligence.py` dengan class `AudienceIntelligence`
    - Implementasi `classify_persona()` — hanya boleh return salah satu dari: `Beginner`, `Intermediate_Trader`, `Fear_Driven`, `Greed_Driven`
    - Implementasi `classify_segment()` — hanya boleh return: `Cold`, `Warm`, `Hot`
    - Implementasi `get_pain_points()` dan `get_emotion_trigger()` per persona
    - _Persyaratan: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [x]* 3.2 Tulis property test untuk klasifikasi persona
    - **Properti 5: Invariant Klasifikasi Persona**
    - **Memvalidasi: Persyaratan 13.1**

  - [x]* 3.3 Tulis property test untuk klasifikasi segment
    - **Properti 6: Invariant Klasifikasi Segment**
    - **Memvalidasi: Persyaratan 13.2, 18.5**

  - [x] 3.4 Buat `marketing/agent/core/content_engine.py` dengan class `ContentEngine`
    - Implementasi rotasi AI provider: Cerebras → DeepSeek → OpenAI (fallback)
    - Implementasi `generate_with_pas()` menggunakan prompt template PAS Framework
    - Implementasi `generate_hook()` dengan tiga tipe: angka spesifik, pertanyaan provokatif, pernyataan kontraintuitif
    - Implementasi `validate_caption_length()` — enforce 150–300 karakter
    - Implementasi `add_disclaimer_if_needed()` — deteksi kata kunci finansial dan tambahkan disclaimer
    - _Persyaratan: 3.1, 3.7, 11.5, 14.1, 14.2_

  - [x]* 3.5 Tulis property test untuk panjang caption
    - **Properti 1: Invariant Panjang Caption**
    - **Memvalidasi: Persyaratan 3.1**

  - [x]* 3.6 Tulis property test untuk struktur PAS
    - **Properti 2: Invariant Struktur PAS**
    - **Memvalidasi: Persyaratan 14.1**

  - [x]* 3.7 Tulis property test untuk kualitas hook
    - **Properti 3: Invariant Kualitas Hook**
    - **Memvalidasi: Persyaratan 14.2**

  - [x]* 3.8 Tulis property test untuk jumlah varian hook
    - **Properti 4: Invariant Jumlah Hook Varian**
    - **Memvalidasi: Persyaratan 14.7**

  - [x]* 3.9 Tulis property test untuk disclaimer klaim finansial
    - **Properti 7: Invariant Disclaimer Klaim Finansial**
    - **Memvalidasi: Persyaratan 3.7**

- [ ] 4. Checkpoint — Pastikan semua test core lulus
  - Pastikan semua test lulus, tanyakan ke user jika ada pertanyaan.

- [x] 5. Implementasi Strategist Agent
  - [x] 5.1 Buat `marketing/agent/agents/strategist_agent.py` dengan class `StrategistAgent`
    - Implementasi `analyze_market_sentiment()` — analisa tren kripto terkini, fallback ke Brand_Context jika data eksternal tidak tersedia
    - Implementasi `determine_campaign_angle()` — tentukan angle berdasarkan sentiment dan feedback Analyst
    - Implementasi `select_target_persona()` — pilih persona target untuk siklus kampanye
    - Implementasi `save_campaign_plan()` — simpan ke tabel `marketing_campaigns` di Supabase
    - Gunakan `AudienceIntelligence` dari core untuk klasifikasi persona
    - _Persyaratan: 2.1, 2.2, 2.3, 2.4, 2.5, 13.1, 13.2, 13.5, 15.2_

  - [x]* 5.2 Tulis property test untuk kategori topik riset
    - **Properti 9: Invariant Kategori Topik**
    - **Memvalidasi: Persyaratan 2.3**

  - [x]* 5.3 Tulis property test untuk jumlah topik riset
    - **Properti 13: Invariant Jumlah Topik Riset**
    - **Memvalidasi: Persyaratan 2.2**

- [x] 6. Implementasi Content Agent
  - [x] 6.1 Buat `marketing/agent/agents/content_agent.py` dengan class `ContentAgent`
    - Implementasi `generate_batch()` — hasilkan 10 konten per siklus: 3 fear-based, 3 greed-based, 4 edukasi
    - Implementasi `generate_feed_content()` — konten feed dengan caption 150–300 karakter, 3–5 hashtag
    - Implementasi `generate_reels_script()` — skrip dengan segmen hook (3–5 detik), main content (10–45 detik), CTA (3–5 detik), max 60 detik total
    - Implementasi `generate_hooks()` — minimal 3 varian hook per topik untuk A/B testing
    - Implementasi `apply_pas_framework()` — gunakan `ContentEngine` untuk generate konten berstruktur PAS
    - Tambahkan CTA default jika konten tidak mengandung CTA eksplisit
    - Simpan semua konten ke tabel `marketing_content` dengan metadata persona target
    - _Persyaratan: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.8, 14.1, 14.2, 14.3, 14.4, 14.7, 14.8, 14.9, 15.3_

  - [x]* 6.2 Tulis property test untuk distribusi tipe konten
    - **Properti 8: Invariant Distribusi Tipe Konten**
    - **Memvalidasi: Persyaratan 9.3**

  - [x]* 6.3 Tulis property test untuk durasi skrip reels
    - **Properti 10: Invariant Durasi Skrip Reels**
    - **Memvalidasi: Persyaratan 4.2, 4.8**

- [x] 7. Implementasi Designer Agent
  - Buat `marketing/agent/agents/designer_agent.py` dengan class `DesignerAgent`
  - Implementasi `select_template()` — pilih `product.html` untuk konten produk, `education.html` untuk konten edukasi
  - Implementasi `render_via_puppeteer()` — panggil `marketing/generate.js` via subprocess dengan data JSON, timeout 30 detik, retry 2x jika gagal
  - Implementasi `render_feed_image()` — output ke `marketing/output/feeds/{tanggal}_{tema}_{platform}.png`
  - Isi variabel template (headline, subtext, eyebrow, pillars/points, cta) dari data konten yang dihasilkan Content Agent
  - Implementasi `generate_reels_video()` — panggil `VideoGenerator.create_reels_video()` dengan skrip dari Content Agent; hanya dijalankan jika `ENABLE_VIDEO_GENERATION=true`; output MP4 disimpan ke `marketing/output/reels/{tanggal}_{tema}.mp4`
  - _Persyaratan: 3.2, 3.3, 3.4, 3.5, 3.8, 12.6_

- [x] 7.1 Buat `marketing/agent/core/video_generator.py`
  - Implementasi class `ElevenLabsClient`:
    - Method `synthesize(text, voice_id)` — POST ke `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}` dengan model `eleven_multilingual_v2`, kembalikan bytes audio MP3
    - Header autentikasi: `xi-api-key: {ELEVENLABS_API_KEY}`
  - Implementasi class `KlingAIClient`:
    - Method `generate(prompt, audio_url, duration)` — POST ke `https://api.klingai.com/v1/videos/text2video`, kembalikan `task_id`
    - Method `poll_status(task_id)` — GET setiap 10 detik hingga `status == "completed"`, timeout 5 menit
    - Method `download_video(video_url, output_path)` — download MP4 ke path yang ditentukan
    - Header autentikasi: `Authorization: Bearer {KLING_AI_API_KEY}`
  - Implementasi class `VideoGenerator`:
    - Method `generate_voiceover(narration, voice_id)` — panggil `ElevenLabsClient.synthesize()`, simpan ke `/tmp/voiceover_{content_id}.mp3`
    - Method `generate_video(prompt, audio_path)` — upload audio, panggil `KlingAIClient.generate()` + `poll_status()` + `download_video()`
    - Method `create_reels_video(script)` — orkestrasi pipeline penuh: narasi → ElevenLabs (MP3) → Kling AI (MP4) → simpan ke `marketing/output/reels/{tanggal}_{tema}.mp4`
    - Fallback: jika ElevenLabs atau Kling AI gagal setelah 2x retry, simpan skrip sebagai JSON saja dan kirim notifikasi admin via Telegram
  - _Persyaratan: 3.2, 3.8_

- [x] 8. Implementasi Publishers (4 platform)
  - [x] 8.1 Buat `marketing/agent/publishers/instagram_publisher.py`
    - Implementasi `publish_feed()` — upload media container lalu publish, simpan `media_id` ke `marketing_publications`
    - Implementasi `publish_reels()` — upload dan publish video sebagai Instagram Reels
    - Implementasi `get_post_metrics()` — ambil likes, comments, reach, impressions via Insights API
    - Implementasi retry logic: jika rate limit (error code 4 atau 32), delay 15 menit, retry maksimal 3x; kirim notifikasi Telegram setelah 3x gagal
    - _Persyaratan: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 8.2 Buat `marketing/agent/publishers/facebook_publisher.py`
    - Implementasi `publish_feed()` dan `publish_reels()` ke Facebook Page via Graph API
    - Implementasi deteksi `OAuthException` code 190 (token expired) — kirim notifikasi ke admin untuk refresh token
    - Implementasi retry logic: 3x percobaan, notifikasi admin jika semua gagal
    - _Persyaratan: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 8.3 Buat `marketing/agent/publishers/tiktok_publisher.py`
    - Implementasi upload video chunked: `init` → `upload` → `complete`
    - Implementasi `publish_feed()` untuk TikTok photo post
    - Implementasi retry logic: 3x percobaan dengan interval 10 menit
    - _Persyaratan: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [x] 8.4 Buat `marketing/agent/publishers/threads_publisher.py`
    - Implementasi publish ke Threads menggunakan Instagram Graph API credentials (Meta ecosystem)
    - Implementasi `publish_feed()` dan `get_post_metrics()`
    - _Persyaratan: 19.1, 19.4_

- [x] 9. Implementasi A/B Testing dan Lead Capture (core)
  - [x] 9.1 Buat `marketing/agent/core/ab_testing.py` dengan class `ABTestManager`
    - Implementasi `create_test()` — buat sesi A/B test dengan dua varian konten
    - Implementasi `evaluate_winner()` — bandingkan CTR setelah minimal 24 jam; jika keduanya CTR < 1% setelah 48 jam, buat Kill_Decision
    - Implementasi `record_pattern()` — catat pola pemenang ke `marketing_ab_tests` untuk digunakan Content Agent di siklus berikutnya
    - Dukung variabel test: `hook_type`, `content_format`, `post_time`, `caption_length`
    - _Persyaratan: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_

  - [x]* 9.2 Tulis property test untuk keputusan Scale/Kill
    - **Properti 12: Keputusan Scale/Kill yang Konsisten**
    - **Memvalidasi: Persyaratan 16.6, 20.2, 20.3**

  - [x] 9.3 Buat `marketing/agent/core/lead_capture.py` dengan class `LeadCaptureManager`
    - Implementasi `record_lead()` — simpan data lead baru ke `marketing_leads` dengan source platform dan content_id
    - Implementasi `update_segment()` — perbarui klasifikasi Cold/Warm/Hot berdasarkan interaksi
    - Implementasi `track_conversion()` — catat konversi dan hitung Conversion_Rate per platform
    - Alert ke admin jika Conversion_Rate platform turun di bawah 2% selama 7 hari berturut-turut
    - _Persyaratan: 17.4, 17.7, 17.8_

- [x] 10. Implementasi Distribution Agent
  - Buat `marketing/agent/agents/distribution_agent.py` dengan class `DistributionAgent`
  - Implementasi `distribute_content()` — posting ke platform yang diaktifkan (`ENABLE_INSTAGRAM`, `ENABLE_FACEBOOK`, `ENABLE_TIKTOK`) dengan caption yang disesuaikan per platform
  - Implementasi `schedule_post()` — jadwalkan posting pada waktu optimal (default: 07.00–09.00, 12.00–13.00, 19.00–21.00 WIB)
  - Implementasi `run_ab_test()` — posting Hook A ke batch pertama, Hook B 2 jam kemudian ke segmen setara
  - Implementasi `retry_failed_post()` — retry 3x, tandai `failed` dan notifikasi admin jika semua gagal
  - Simpan log semua aktivitas posting ke `marketing_publications`
  - _Persyaratan: 9.1, 9.2, 9.5, 11.4, 15.4, 16.1, 16.2, 16.5, 19.1, 19.2, 19.4, 19.5, 19.6, 19.7_

- [x] 11. Implementasi Sales Agent
  - Buat `marketing/agent/agents/sales_agent.py` dengan class `SalesAgent`
  - Implementasi `process_new_lead()` — kirim followup pertama dalam maksimal 1 jam setelah lead masuk
  - Implementasi `send_followup()` — pendekatan conversational (bukan hard selling): tanya kebutuhan → edukasi → tawarkan solusi
  - Implementasi `handle_objection()` — tangani 5 objection: takut scam, bisa rugi, worth it, ribet setup, gratis beneran
  - Implementasi `classify_lead_segment()` — gunakan `AudienceIntelligence` untuk update Cold/Warm/Hot di Supabase
  - Implementasi `attempt_closing()` — beralih ke mode closing saat lead menunjukkan sinyal kesiapan beli
  - Implementasi `handle_telegram_message(telegram_chat_id, text)` — handler untuk pesan masuk dari lead di Telegram; daftarkan ke `Bismillah/bot.py` sebagai message handler; lead diidentifikasi via `telegram_chat_id` yang tersimpan di tabel `marketing_leads`
  - Sales Agent **hanya berjalan di Telegram** — terintegrasi dengan `Bismillah/bot.py` yang sudah ada; tidak ada integrasi Instagram DM atau WhatsApp
  - Semua CTA di konten yang dihasilkan Content Agent menyertakan link `t.me/...` untuk mengarahkan lead ke Telegram bot
  - Re-engagement: kirim Free_Value baru jika lead tidak respons dalam 48 jam
  - Tandai `opted_out` dan hentikan followup jika lead eksplisit tidak tertarik
  - Catat semua interaksi ke `marketing_lead_interactions`
  - _Persyaratan: 17.6, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9_

- [x] 12. Implementasi Analyst Agent
  - Buat `marketing/agent/agents/analyst_agent.py` dengan class `AnalystAgent`
  - Implementasi `collect_metrics()` — kumpulkan CTR, CVR, CAC, reach, impressions, engagement rate dari semua platform setiap 24 jam
  - Implementasi `make_scale_decision()` — Scale jika CTR > 3% ATAU Conversion_Rate > 5%
  - Implementasi `make_kill_decision()` — Kill jika CTR < 1% DAN engagement < 80% rata-rata DAN sudah > 48 jam
  - Implementasi `generate_weekly_report()` — total reach, total lead, CVR per platform, CAC, Scale/Kill decisions, rekomendasi strategi
  - Implementasi `generate_feedback()` — insight terstruktur untuk Strategist Agent (tipe konten efektif, persona responsif, angle prioritas)
  - Alert ke admin jika Conversion_Rate turun > 30% dibanding minggu sebelumnya
  - Simpan semua data ke `marketing_analytics`
  - _Persyaratan: 10.1, 10.2, 10.4, 10.5, 10.6, 15.6, 16.3, 16.4, 16.6, 16.7, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.8, 20.9_

- [ ] 13. Checkpoint — Pastikan semua agen berjalan dengan benar
  - Pastikan semua test lulus, tanyakan ke user jika ada pertanyaan.

- [x] 14. Implementasi Approval Queue dan notifikasi Telegram
  - Tambahkan logika Approval_Queue ke alur Designer Agent → Distribution Agent
  - Implementasi notifikasi Telegram ke admin dengan preview konten dan tombol Approve/Reject
  - Implementasi pengingat otomatis jika konten di queue lebih dari 24 jam tanpa tindakan
  - Implementasi mode `auto-publish` yang dapat diaktifkan via environment variable
  - Update status konten di `marketing_content` (draft → pending_approval → approved/rejected → published)
  - _Persyaratan: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 12.4_

- [x] 15. Implementasi Content Calendar dan penjadwalan otomatis
  - Tambahkan logika pembuatan Content_Calendar mingguan ke Orchestrator: minimal 7 konten per minggu, distribusi 40% edukasi / 30% produk / 30% komunitas+psikologi
  - Implementasi pengecekan duplikasi topik dalam 7 hari terakhir per platform
  - Simpan Content_Calendar ke `marketing/content_calendar.json` dan Supabase
  - Implementasi penjadwalan laporan mingguan setiap Senin pukul 08.00 WIB via Telegram
  - _Persyaratan: 9.1, 9.2, 9.3, 9.4, 9.5, 10.3, 20.7_

- [x] 16. Implementasi Brand Context reload dan Orchestrator utama
  - [x] 16.1 Buat `marketing/agent/main.py` dengan class `MarketingOrchestrator`
    - Implementasi `run_cycle()` — jalankan 7 langkah loop: Strategist → Content → Designer → Distribution → Sales → Analyst → feedback ke Strategist
    - Implementasi `run_continuous()` — loop berkelanjutan dengan interval yang dapat dikonfigurasi
    - Implementasi `handle_agent_error()` — log error, kirim notifikasi Telegram, lanjutkan ke agen berikutnya tanpa menghentikan sistem
    - Implementasi graceful degradation per agen (lihat desain)
    - Simpan status setiap agen dan hasil setiap langkah ke Supabase
    - _Persyaratan: 15.1, 15.7, 15.8, 15.9_

  - [x] 16.2 Implementasi Brand Context reload tanpa restart
    - Tambahkan mekanisme file watcher atau reload-on-demand ke `config.py`
    - Pastikan Marketing Agent membaca data terbaru dari `brand_context.json` setelah trigger reload
    - _Persyaratan: 1.4, 1.5_

  - [x]* 16.3 Tulis property test untuk Brand Context reload
    - **Properti 14: Round-Trip Brand Context Reload**
    - **Memvalidasi: Persyaratan 1.4**

- [ ] 17. Checkpoint akhir — Integrasi dan smoke test
  - Pastikan semua test lulus, tanyakan ke user jika ada pertanyaan.
  - Verifikasi smoke test: semua env vars tersedia, `brand_context.json` dapat dibaca, koneksi Supabase berhasil, minimal satu AI provider tersedia
  - _Persyaratan: 11.2, 11.3, 12.1_

## Catatan

- Tugas bertanda `*` bersifat opsional dan dapat dilewati untuk MVP yang lebih cepat
- Setiap tugas mereferensikan persyaratan spesifik untuk keterlacakan
- Semua file implementasi ditempatkan di `marketing/agent/` sesuai struktur yang ditentukan
- Property tests menggunakan library `hypothesis` dengan minimal 100 iterasi per properti
- Rotasi AI provider: Cerebras (utama) → DeepSeek (fallback) → OpenAI (fallback terakhir)
