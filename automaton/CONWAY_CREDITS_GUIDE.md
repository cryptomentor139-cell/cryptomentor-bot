# Panduan Conway Credits untuk Automaton

## Masalah yang Dihadapi

Automaton memiliki **10.5 USDC** di wallet tapi tidak bisa memanggil GPT-4 karena Conway Inference API membutuhkan **Conway Credits**, bukan USDC.

Error yang muncul:
```
Inference error: 402: {"error":"Insufficient credits","detail":"Minimum balance of 10 cents required. Current balance: 0 cents."}
```

## Penjelasan

### Conway Credits vs USDC

1. **Conway Credits** ($USD dalam akun Conway API)
   - Digunakan untuk: Inference API (GPT-4, Claude, dll)
   - Cara dapat: Beli dengan kartu kredit di dashboard Conway
   - Dicek via: `GET /v1/credits/balance`

2. **USDC** (cryptocurrency di Base network)
   - Digunakan untuk: Conway Cloud (VMs), Conway Domains (domain names)
   - Cara dapat: Transfer USDC ke wallet automaton
   - Dicek via: Smart contract `balanceOf()`
   - Protocol: x402 payment

### Kenapa USDC Tidak Bisa Digunakan untuk Inference?

Conway Inference API **tidak support x402 payment protocol**. Hanya Conway Credits yang diterima.

## Solusi

### Opsi 1: Beli Conway Credits (RECOMMENDED)

1. Buka dashboard Conway: https://app.conway.tech
2. Login dengan akun yang memiliki API key: `cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr`
3. Cari menu "Credits" atau "Billing"
4. Beli credits dengan kartu kredit (minimal $0.10)
5. Credits akan langsung tersedia untuk API key tersebut

### Opsi 2: Transfer Credits dari API Key Lain

Jika kamu punya API key lain yang sudah punya credits, bisa transfer:

```bash
# Build CLI dulu
cd packages/cli
npm run build
cd ../..

# Transfer 10 USD credits
node packages/cli/dist/index.js fund 10
```

**CATATAN**: Command ini **BUKAN** untuk convert USDC → Credits. Ini hanya transfer credits dari API key yang sudah punya balance.

### Opsi 3: Hubungi Conway Support

Tanyakan apakah ada cara untuk convert USDC → Conway Credits secara programmatic atau manual.

## Status Saat Ini

- ✅ Wallet: `0x63116672BEf9F26FD906Cd2a57550F7A13925822`
- ✅ USDC Balance: 10.5 USDC (Base network)
- ❌ Conway Credits: $0.00
- ❌ Automaton: Tidak bisa memanggil GPT-4

## Cek Balance

### Cek USDC Balance
```bash
node check-balance.js
```

### Cek Conway Credits
```bash
node check-api-credits.js
```

## Modifikasi yang Sudah Dibuat

Saya sudah mencoba modifikasi `src/conway/inference.ts` untuk support x402 payment, tapi Conway Inference API tetap return 402 error karena memang tidak support x402 protocol.

## Next Steps

1. Beli Conway Credits minimal $0.10 dengan kartu kredit
2. Test automaton lagi: `node dist/index.js --run`
3. Automaton akan bisa memanggil GPT-4 setelah credits tersedia
