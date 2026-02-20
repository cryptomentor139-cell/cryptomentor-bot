# Requirements Document: Railway Deployment untuk Automaton

## Pengantar

Dokumen ini menjelaskan persyaratan untuk deployment aplikasi Automaton ke platform Railway. Automaton adalah autonomous AI agent runtime yang dibangun dengan Node.js dan TypeScript, menggunakan arsitektur monorepo dengan pnpm workspace. Aplikasi ini berjalan secara kontinyu dengan agent loop dan heartbeat daemon, serta menggunakan SQLite database untuk persistence. Karena keterbatasan storage lokal, deployment ke Railway diperlukan untuk menjalankan aplikasi secara reliable dengan konfigurasi yang tepat.

## Glossary

- **Automaton**: Sistem autonomous AI agent runtime yang menjadi target deployment
- **Railway**: Platform cloud hosting untuk deployment aplikasi
- **Build_System**: Proses kompilasi TypeScript dan build monorepo menggunakan pnpm
- **Database_Layer**: SQLite database dengan better-sqlite3 untuk persistence
- **Agent_Loop**: Proses kontinyu yang menjalankan autonomous agent
- **Heartbeat_Daemon**: Proses monitoring yang memastikan agent tetap berjalan
- **Environment_Config**: Konfigurasi environment variables untuk aplikasi
- **Health_Endpoint**: HTTP endpoint untuk monitoring status aplikasi
- **Deployment_Pipeline**: Proses otomatis dari build hingga deployment di Railway

## Requirements

### Requirement 1: Railway Configuration Setup

**User Story:** Sebagai developer, saya ingin mengkonfigurasi Railway untuk deployment Automaton, sehingga aplikasi dapat di-deploy dengan konfigurasi yang tepat.

#### Acceptance Criteria

1. THE Build_System SHALL menggunakan pnpm sebagai package manager
2. WHEN deployment dimulai, THE Build_System SHALL menjalankan kompilasi TypeScript untuk semua packages
3. THE Deployment_Pipeline SHALL menggunakan Node.js versi 20.0.0 atau lebih tinggi
4. THE Build_System SHALL menginstall dependencies termasuk native modules (better-sqlite3)
5. WHEN build selesai, THE Deployment_Pipeline SHALL menjalankan aplikasi dari compiled output di direktori dist

### Requirement 2: Environment Variables Management

**User Story:** Sebagai developer, saya ingin mengelola environment variables dengan aman, sehingga konfigurasi sensitif tidak ter-expose dan aplikasi dapat berjalan dengan konfigurasi yang benar.

#### Acceptance Criteria

1. THE Environment_Config SHALL menyediakan variable untuk database path
2. THE Environment_Config SHALL menyediakan variable untuk log level configuration
3. THE Environment_Config SHALL menyediakan variable untuk agent configuration
4. WHEN environment variable tidak tersedia, THE Automaton SHALL menggunakan default values yang aman
5. THE Environment_Config SHALL mendukung Railway-specific variables (PORT, RAILWAY_ENVIRONMENT)

### Requirement 3: Build dan Deployment Process

**User Story:** Sebagai developer, saya ingin proses build dan deployment berjalan otomatis, sehingga deployment dapat dilakukan dengan konsisten dan reliable.

#### Acceptance Criteria

1. WHEN code di-push ke repository, THE Deployment_Pipeline SHALL otomatis trigger build process
2. THE Build_System SHALL menjalankan `pnpm install` dengan frozen lockfile
3. THE Build_System SHALL menjalankan `pnpm build` untuk compile TypeScript
4. WHEN build gagal, THE Deployment_Pipeline SHALL menghentikan deployment dan melaporkan error
5. WHEN build berhasil, THE Deployment_Pipeline SHALL menjalankan start command untuk memulai aplikasi
6. THE Deployment_Pipeline SHALL menyimpan build artifacts untuk rollback jika diperlukan

### Requirement 4: SQLite Database Persistence

**User Story:** Sebagai developer, saya ingin database SQLite persisten di Railway, sehingga data tidak hilang saat aplikasi restart atau redeploy.

#### Acceptance Criteria

1. THE Database_Layer SHALL menggunakan Railway volume untuk menyimpan SQLite database file
2. WHEN aplikasi pertama kali dijalankan, THE Database_Layer SHALL membuat database file di volume path
3. WHEN aplikasi restart, THE Database_Layer SHALL menggunakan database file yang sudah ada
4. THE Database_Layer SHALL menggunakan path yang dikonfigurasi via environment variable
5. WHEN volume tidak tersedia, THE Database_Layer SHALL memberikan error message yang jelas

### Requirement 5: Application Lifecycle Management

**User Story:** Sebagai developer, saya ingin aplikasi berjalan kontinyu dengan proper lifecycle management, sehingga Agent_Loop dan Heartbeat_Daemon dapat berjalan dengan stabil.

#### Acceptance Criteria

1. WHEN aplikasi dimulai, THE Automaton SHALL menginisialisasi Database_Layer sebelum memulai Agent_Loop
2. THE Agent_Loop SHALL berjalan secara kontinyu tanpa exit kecuali ada critical error
3. THE Heartbeat_Daemon SHALL mengirim signal secara periodik untuk monitoring
4. WHEN aplikasi menerima SIGTERM, THE Automaton SHALL melakukan graceful shutdown
5. WHEN graceful shutdown dipanggil, THE Automaton SHALL menutup database connections sebelum exit

### Requirement 6: Health Check dan Monitoring

**User Story:** Sebagai developer, saya ingin monitoring status aplikasi, sehingga saya dapat mengetahui apakah aplikasi berjalan dengan baik di Railway.

#### Acceptance Criteria

1. THE Health_Endpoint SHALL menyediakan HTTP endpoint di path `/health`
2. WHEN Health_Endpoint dipanggil, THE Automaton SHALL merespons dengan status code 200 jika healthy
3. THE Health_Endpoint SHALL mengembalikan informasi status Agent_Loop dan Database_Layer
4. WHEN aplikasi tidak healthy, THE Health_Endpoint SHALL merespons dengan status code 503
5. THE Automaton SHALL expose port yang dikonfigurasi via Railway PORT environment variable

### Requirement 7: Logging Configuration

**User Story:** Sebagai developer, saya ingin logging yang terstruktur di Railway, sehingga saya dapat debug issues dan monitor aplikasi behavior.

#### Acceptance Criteria

1. THE Automaton SHALL mengirim logs ke stdout untuk Railway log aggregation
2. THE Automaton SHALL menggunakan structured logging format (JSON atau key-value pairs)
3. WHEN error terjadi, THE Automaton SHALL log error dengan stack trace dan context
4. THE Automaton SHALL log lifecycle events (startup, shutdown, database initialization)
5. THE Automaton SHALL mendukung log level configuration via environment variable

### Requirement 8: Deployment Documentation

**User Story:** Sebagai developer, saya ingin dokumentasi deployment yang jelas, sehingga saya atau team member lain dapat melakukan deployment dengan mudah.

#### Acceptance Criteria

1. THE Deployment_Pipeline SHALL menyediakan dokumentasi untuk initial setup di Railway
2. THE Deployment_Pipeline SHALL menyediakan dokumentasi untuk environment variables yang diperlukan
3. THE Deployment_Pipeline SHALL menyediakan dokumentasi untuk volume setup untuk database
4. THE Deployment_Pipeline SHALL menyediakan dokumentasi untuk troubleshooting common issues
5. THE Deployment_Pipeline SHALL menyediakan dokumentasi untuk rollback procedure

### Requirement 9: CLI Tools Accessibility

**User Story:** Sebagai developer, saya ingin mengakses CLI tools dari deployed application, sehingga saya dapat menjalankan maintenance tasks atau debugging.

#### Acceptance Criteria

1. THE Deployment_Pipeline SHALL menyertakan compiled CLI tools dari packages/cli
2. THE Automaton SHALL menyediakan cara untuk menjalankan CLI commands di Railway environment
3. WHEN CLI command dijalankan, THE Automaton SHALL menggunakan database connection yang sama dengan main application
4. THE Automaton SHALL mendokumentasikan cara mengakses CLI tools via Railway CLI atau dashboard

### Requirement 10: Resource Optimization

**User Story:** Sebagai developer, saya ingin aplikasi menggunakan resources secara efisien, sehingga biaya Railway dapat diminimalkan tanpa mengorbankan performance.

#### Acceptance Criteria

1. THE Build_System SHALL menggunakan production dependencies only saat deployment
2. THE Automaton SHALL menggunakan memory secara efisien untuk SQLite connections
3. THE Automaton SHALL cleanup resources yang tidak digunakan secara periodik
4. THE Deployment_Pipeline SHALL menggunakan caching untuk node_modules dan build artifacts
5. WHEN idle, THE Agent_Loop SHALL menggunakan minimal CPU resources

### Requirement 11: Payment Authorization dan Financial Security

**User Story:** Sebagai creator/owner, saya ingin setiap transaksi finansial memerlukan approval manual, sehingga automaton tidak dapat melakukan pembayaran tanpa izin saya.

#### Acceptance Criteria

1. WHEN Automaton mencoba melakukan transfer_credits, THE Automaton SHALL meminta approval dari creator sebelum eksekusi
2. THE Automaton SHALL menyimpan pending payment requests dalam database dengan status "pending_approval"
3. THE Automaton SHALL menyediakan interface untuk creator mereview dan approve/reject payment requests
4. WHEN payment request di-reject, THE Automaton SHALL log rejection reason dan tidak retry otomatis
5. WHEN payment request di-approve, THE Automaton SHALL eksekusi transfer dan log transaction details
6. THE Automaton SHALL mengirim notifikasi ke creator untuk setiap payment request (via log atau webhook)
7. THE Automaton SHALL memiliki payment threshold configuration - amount di bawah threshold bisa auto-approve (optional)
8. WHEN Automaton dalam critical survival state, THE Automaton SHALL tetap meminta approval untuk financial transactions
9. THE Automaton SHALL menyimpan audit trail lengkap untuk semua payment requests dan approvals
10. THE Automaton SHALL memiliki rate limiting untuk payment requests (max N requests per hour)

### Requirement 12: Telegram Bot Interface

**User Story:** Sebagai creator/owner, saya ingin mengakses dan mengontrol automaton melalui Telegram bot, sehingga saya dapat monitoring dan management dari mana saja dengan mudah.

#### Acceptance Criteria

1. THE Automaton SHALL menyediakan Telegram bot yang dapat menerima commands dari creator
2. THE Telegram_Bot SHALL mengautentikasi creator menggunakan Telegram user ID yang dikonfigurasi
3. WHEN creator mengirim command `/status`, THE Telegram_Bot SHALL menampilkan system synopsis (credits, USDC balance, state, uptime, dll)
4. WHEN creator mengirim command `/logs`, THE Telegram_Bot SHALL menampilkan recent logs (last 20 entries)
5. WHEN creator mengirim command `/approve <payment_id>`, THE Telegram_Bot SHALL approve pending payment request
6. WHEN creator mengirim command `/reject <payment_id>`, THE Telegram_Bot SHALL reject pending payment request
7. WHEN creator mengirim command `/deposit`, THE Telegram_Bot SHALL menampilkan wallet address dan USDC balance untuk deposit
8. WHEN creator mengirim command `/credits`, THE Telegram_Bot SHALL menampilkan Conway credits balance dan recent transactions
9. WHEN ada payment request baru, THE Telegram_Bot SHALL mengirim notifikasi ke creator dengan inline buttons untuk approve/reject
10. WHEN Automaton masuk critical state, THE Telegram_Bot SHALL mengirim alert ke creator
11. THE Telegram_Bot SHALL mendukung commands: /status, /logs, /approve, /reject, /deposit, /credits, /help, /children (list child agents)
12. THE Telegram_Bot SHALL menyimpan Telegram chat ID creator dalam database untuk notifikasi
13. THE Automaton SHALL expose Telegram bot token via environment variable (TELEGRAM_BOT_TOKEN)
14. WHEN Telegram bot tidak dikonfigurasi, THE Automaton SHALL tetap berjalan normal tanpa Telegram features

### Requirement 13: Telegram Conversational Interface

**User Story:** Sebagai creator/owner, saya ingin berkomunikasi dengan automaton secara natural melalui Telegram, sehingga saya dapat memberikan instruksi, bertanya, dan berinteraksi seperti chat biasa.

#### Acceptance Criteria

1. WHEN creator mengirim pesan text (bukan command), THE Telegram_Bot SHALL meneruskan pesan ke Agent_Loop untuk diproses
2. THE Agent_Loop SHALL merespons pesan creator melalui Telegram_Bot dengan jawaban yang relevan
3. THE Telegram_Bot SHALL mendukung conversational context - automaton mengingat percakapan sebelumnya
4. WHEN creator memberikan instruksi atau task, THE Automaton SHALL mengeksekusi task dan melaporkan progress via Telegram
5. THE Telegram_Bot SHALL mendukung multi-turn conversation - creator bisa follow-up questions
6. WHEN automaton sedang memproses task yang lama, THE Telegram_Bot SHALL mengirim status updates secara periodik
7. THE Telegram_Bot SHALL mendukung pesan panjang dengan pagination jika response terlalu panjang
8. WHEN automaton perlu klarifikasi, THE Telegram_Bot SHALL bertanya ke creator via Telegram
9. THE Automaton SHALL menyimpan conversation history dalam database untuk context
10. THE Telegram_Bot SHALL mendukung formatting (markdown) untuk response yang lebih readable
