# DESK — Solana Memecoin Paper Desk

Mode: **PAPER ONLY**, modal simulasi awal **0.5 SOL**. Tidak ada integrasi wallet, swap, transaksi, tanda tangan, atau pemindahan dana. Python 3.10+; tanpa dependensi eksternal.

## Menjalankan (terminal Replit / komputer)

```bash
python desk.py status
python desk.py scan TOKEN_CONTOH --source "riset manual dari sumber tepercaya"
python desk.py verify TOKEN_CONTOH --safe yes --volume 10000 --liquidity 5000 --holders 150 --contract "diperiksa manual" --smart-money "belum terkonfirmasi"
python desk.py execute TOKEN_CONTOH --entry 1 --stop 0.9 --take 1.2 --size 0.05 --reason "simulasi saja"
python desk.py exit TOKEN_CONTOH --price 1.1
python desk.py status
```

**Angka di atas hanyalah contoh, bukan data token nyata atau rekomendasi trading.** Harga entry/exit harus menggunakan unit yang sama. P&L adalah estimasi sederhana tanpa biaya, slippage, atau perubahan harga SOL. Simulasi mengasumsikan posisi long.

Alur wajib: SCAN → VERIFY → EXECUTE → EXIT. Sumber tidak tersedia atau verifikasi gagal → SKIP final, tidak boleh scan ulang token yang sama. VERIFY membutuhkan data yang dimasukkan pengguna, bukan feed live; opsi `--safe yes` adalah keputusan pengguna, bukan audit kontrak otomatis. Jangan menganggap sumber yang disebutkan telah diperiksa otomatis. Penyimpanan lokal `paper_trades.json` tidak aman untuk penggunaan multi-user/konkuren.

## Pengujian

```bash
python -m unittest discover -v
```

GitHub Actions menjalankan unit test pada push dan pull request. Belum ada scheduler, scanner real-time, integrasi GMGN/Moby, atau dashboard web. Jangan memasukkan seed phrase atau private key ke repository publik.
