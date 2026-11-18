#!/usr/bin/env python3
"""Read-only Solana token market snapshot from DexScreener. No trades."""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE = "https://api.dexscreener.com/latest/dex/tokens/"
def main():
    token = os.getenv("DESK_TOKEN_ADDRESS", "").strip()
    if not token:
        print("SKIP: DESK_TOKEN_ADDRESS belum diatur; tidak ada token yang dianalisis.")
        return 0
    if not (32 <= len(token) <= 44 and all(c.isalnum() for c in token)):
        print("SKIP: alamat token Solana tidak valid.")
        return 0
    try:
        req = urllib.request.Request(BASE + token, headers={"User-Agent":"DESK-paper-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.load(response)
        pairs = [p for p in (data.get("pairs") or []) if p.get("chainId") == "solana" and p.get("baseToken", {}).get("address") == token]
        if not pairs:
            print("SKIP: tidak ada pair Solana yang cocok pada DexScreener.")
            return 0
        pairs.sort(key=lambda p: float((p.get("liquidity") or {}).get("usd") or 0), reverse=True)
        p = pairs[0]
        required = {"priceUsd":p.get("priceUsd"),"liquidityUsd":(p.get("liquidity") or {}).get("usd"),"volume24hUsd":(p.get("volume") or {}).get("h24")}
        if any(v is None for v in required.values()):
            print("SKIP: data harga, likuiditas, atau volume tidak lengkap.")
            return 0
        result = {"time_utc":datetime.now(timezone.utc).isoformat(),"mode":"READ_ONLY","source":"DexScreener","token":token,"pair":p.get("pairAddress"),**required,"status":"RESEARCH_ONLY","warning":"Holder, keamanan kontrak, smart money, dan kelayakan trade belum diverifikasi. Tidak boleh otomatis BUY."}
        print(json.dumps(result, indent=2))
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as e:
        print("SKIP: DexScreener tidak tersedia atau data tidak valid ("+type(e).__name__+").")
    return 0
if __name__ == "__main__":
    sys.exit(main())
