# Setup After Clone

## 1. Copy .env files
Buat file .env di setiap folder berdasarkan .env.example:
- Bismillah/.env
- license_server/.env
- website-backend/.env
- Whitelabel #1/.env
- marketing/agent/.env

## 2. Install dependencies
\\\ash
# Bot utama
cd Bismillah && pip install -r requirements.txt

# License server
cd license_server && pip install -r requirements.txt

# Website backend
cd website-backend && pip install -r requirements.txt

# Website frontend
cd website-frontend && npm install

# Marketing
cd marketing && npm install
\\\

## 3. Setup Database
Jalankan SQL migrations di Supabase (urutan penting):
1. db/setup_supabase.sql
2. db/user_api_keys.sql
3. db/user_skills.sql
4. db/autotrade_trades.sql
5. db/add_*.sql (semua file add_ secara berurutan)
6. license_server/db/setup.sql
7. Whitelabel #1/db/setup.sql

## 4. Credentials yang perlu di-generate ulang
- [ ] Telegram Bot Token baru (via @BotFather)
- [ ] Supabase project baru atau reset service key
- [ ] API keys exchange (BingX, Binance, Bybit, Bitunix)
- [ ] OpenAI / Cerebras API key
- [ ] License server secret key baru
