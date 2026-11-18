"""Read-only Solana candidate scan. Market observations are NOT safety approval."""
import datetime
import json
import pathlib
import urllib.request
from risk_verify import evaluate

BASE = "https://api.dexscreener.com"
OUTPUT = pathlib.Path("reports/solana-scan.json")
MAX_TOKENS = 12

def get_json(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "DESK-paper-research/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.load(response)

def scan(fetch=get_json):
    report = {"mode": "PAPER_RESEARCH_ONLY", "time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "source": "DexScreener public API", "candidates": [], "warnings": []}
    try:
        profiles = fetch("/token-profiles/latest/v1")
        if not isinstance(profiles, list):
            raise ValueError("Invalid token profiles response")
    except Exception as exc:
        report["warnings"].append("DexScreener token profiles unavailable: " + type(exc).__name__)
        return report
    seen = set()
    for profile in profiles:
        if not isinstance(profile, dict) or profile.get("chainId") != "solana":
            continue
        mint = profile.get("tokenAddress")
        if not isinstance(mint, str) or not mint or mint in seen:
            continue
        seen.add(mint)
        if len(seen) > MAX_TOKENS:
            break
        entry = {"mint": mint, "decision": "SKIP", "reason": "Verification incomplete; holder distribution, contract safety, and smart-money not verified"}
        try:
            data = fetch("/token-pairs/v1/solana/" + mint)
            pairs = [p for p in data if isinstance(p, dict) and p.get("chainId") == "solana"] if isinstance(data, list) else []
            pairs = [p for p in pairs if isinstance(p.get("liquidity"), dict) and isinstance(p["liquidity"].get("usd"), (int, float))]
            if not pairs:
                entry["reason"] = "No usable Solana liquidity data"
            else:
                pair = max(pairs, key=lambda p: p["liquidity"]["usd"])
                entry["pair_address"] = pair.get("pairAddress")
                entry["dex"] = pair.get("dexId")
                entry["liquidity_usd"] = pair["liquidity"]["usd"]
                entry["volume_24h_usd"] = (pair.get("volume") or {}).get("h24")
                entry["price_usd"] = pair.get("priceUsd")
                entry["created_at_ms"] = pair.get("pairCreatedAt")
                entry["reason"] = "SKIP final: holder distribution, contract safety and smart-money data unavailable from this source"
        except Exception as exc:
            entry["reason"] = "DexScreener pair endpoint unavailable: " + type(exc).__name__
        gate = evaluate(entry)
        entry["risk_checks"] = gate["reasons"]
        entry["decision"] = gate["decision"]
        report["candidates"].append(entry)
    if not report["candidates"]:
        report["warnings"].append("No Solana profiles in latest feed; no tokens approved")
    return report

def main():
    result = scan()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print("Scanned", len(result["candidates"]), "candidates; 0 approved; no trades.")
    for warning in result["warnings"]:
        print("WARNING:", warning)

if __name__ == "__main__":
    main()
