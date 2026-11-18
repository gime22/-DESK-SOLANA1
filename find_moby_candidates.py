"""Find fresh Solana tokens and verify each with Moby read-only tools.
No real trades. Any missing verification means SKIP final.
"""
import json
import pathlib
from datetime import datetime, timezone
from market_scan import scan
from moby_token_research import check_token

OUT = pathlib.Path("reports/moby-candidates.json")
MAX_RESEARCH = 5
MIN_LIQUIDITY_USD = 20_000
MIN_VOLUME_24H_USD = 50_000

def main():
    report = scan()
    now = int(datetime.now(timezone.utc).timestamp() * 1000)
    fresh = []
    for x in report["candidates"]:
        created = x.get("created_at_ms")
        if (isinstance(created, (int, float)) and 0 <= now-created <= 24*3600000
                and isinstance(x.get("liquidity_usd"), (int, float))
                and x["liquidity_usd"] >= MIN_LIQUIDITY_USD
                and isinstance(x.get("volume_24h_usd"), (int, float))
                and x["volume_24h_usd"] >= MIN_VOLUME_24H_USD):
            fresh.append(x)
    fresh.sort(key=lambda x: (x.get("liquidity_usd") or 0), reverse=True)
    results = []
    for candidate in fresh[:MAX_RESEARCH]:
        mint = candidate["mint"]
        try:
            research = check_token(mint)
        except Exception as exc:
            research = {"mint":mint,"decision":"SKIP","reasons":["Moby research unavailable: "+type(exc).__name__]}
        results.append({"mint":mint,"liquidity_usd":candidate.get("liquidity_usd"),
                        "volume_24h_usd":candidate.get("volume_24h_usd"),
                        "created_at_ms":candidate.get("created_at_ms"),
                        "moby":research,"decision":"SKIP"})
        print("CANDIDATE",mint,"liquidity_usd",candidate.get("liquidity_usd"),
              "volume_24h_usd",candidate.get("volume_24h_usd"),"decision SKIP",
              "Moby checks",research.get("checks",{}))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"time_utc":datetime.now(timezone.utc).isoformat(),
        "scanned":len(report["candidates"]),"fresh":len(fresh),"researched":results,
        "approved":0,"live_trading_allowed":False},indent=2))
    print("Scanned",len(report["candidates"]),"fresh",len(fresh),
          "researched",len(results),"approved 0; no trades")

if __name__=="__main__":
    main()
