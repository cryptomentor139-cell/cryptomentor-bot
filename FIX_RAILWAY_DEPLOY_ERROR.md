# 🔧 Fix Railway Deploy Error

## Error yang Terjadi

```
ERROR: failed to solve: process "/bin/bash -ol pipefail -c ..."
Error: Docker build failed
```

## Penyebab

Railway gagal build karena:
1. nixpacks.toml format tidak kompatibel
2. Build commands terlalu kompleks
3. Dependencies conflict

## Solusi yang Diterapkan

### 1. Simplified railway.json
Kembali ke config simple, biarkan Railway auto-detect

### 2. Updated start_combined.sh
- Check jika automaton/dist sudah ada
- Build on-demand jika belum ada
- Lebih robust error handling

### 3. Created railway.toml (alternatif)
Format yang lebih Railway-friendly

## Cara Deploy Ulang

```bash
cd Bismillah
git add .
git commit -m "fix: railway deploy error - simplified build"
git push origin main
```

Railway akan auto-redeploy dengan config baru.

## Monitoring

Cek Railway logs untuk:
```
[1/4] Checking Python...
[2/4] Checking Automaton build...
[3/4] Starting Telegram Bot...
✓ Bot started (PID: xxxx)
[4/4] Starting Automaton...
✓ Automaton started (PID: xxxx)
```

## Jika Masih Error

### Opsi A: Rollback ke Bot-Only
```bash
echo "web: python main.py" > Procfile
git add Procfile
git commit -m "rollback: bot only temporarily"
git push
```

### Opsi B: Deploy Automaton Terpisah
Gunakan Opsi 2 (2 services terpisah)

## Troubleshooting

### Build Error: npm ci failed
- Cek automaton/package-lock.json ada
- Cek Node.js version di Railway (harus 20+)

### Build Error: tsc not found
- Cek automaton/package.json devDependencies
- Pastikan typescript installed

### Runtime Error: dist/ not found
- Build phase gagal
- Cek build logs di Railway

## Alternative: Manual Build

Jika auto-build gagal, build manual:

```bash
# Local
cd automaton
npm ci
npm run build
cd ..

# Commit dist/
git add automaton/dist
git commit -m "chore: add pre-built automaton"
git push
```

Lalu update start_combined.sh untuk skip build.

## Status

✅ railway.json - SIMPLIFIED
✅ railway.toml - CREATED (alternative)
✅ start_combined.sh - UPDATED (more robust)
✅ .railwayignore - UPDATED

Ready untuk redeploy!
