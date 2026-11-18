#!/usr/bin/env python3
"""DESK: inspect candidate tokens with real Moby read-only research.

No buy/sell/order/swap tools are called. The output is evidence for human review,
not proof of safety or a trade authorization. Fails closed if sources fail.
"""
import json
import os
from moby_readonly import call, VERSION
from risk_verify import evaluate

RESEARCH = ("get_token_overview", "get_token_key_holders", "get_token_smart_money")

def check_token(mint, call_rpc=call):
    init, session = call_rpc("initialize", {"protocolVersion": VERSION, "capabilities": {},
        "clientInfo": {"name": "DESK-research", "version": "0.4"}}, 1)
    if init.get("error"):
        raise RuntimeError("MCP initialization failed")
    discovered, session = call_rpc("tools/list", {}, 2, session)
    names = {x.get("name") for x in discovered.get("result", {}).get("tools", [])}
    missing = [x for x in RESEARCH if x not in names]
    if missing:
        return {"mint": mint, "decision": "SKIP", "reasons": ["Missing Moby tools: " + ", ".join(missing)]}
    checks = {}
    for i, name in enumerate(RESEARCH, 3):
        try:
            result, session = call_rpc("tools/call", {"name": name, "arguments": {"token_address": mint}}, i, session)
            checks[name] = bool(result.get("result")) and not result.get("error") and not result.get("result", {}).get("isError", False)
        except Exception:
            checks[name] = False
    # We cannot treat an API response as proof of holder concentration, sellability,
    # revoked mint/freeze authority, or smart-money quality without parsing its fields.
    assessment = evaluate({})
    reasons = ["Moby raw research not yet mapped to validated safety fields"]
    reasons += [name + " unavailable" for name, ok in checks.items() if not ok]
    return {"mint": mint, "decision": assessment["decision"], "checks": checks,
            "reasons": reasons, "live_trading_allowed": False}

def main():
    mint = os.environ.get("DESK_TOKEN_MINT", "").strip()
    if not (32 <= len(mint) <= 44) or any(c not in "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz" for c in mint):
        raise SystemExit("A valid Solana token mint is required")
    if not os.environ.get("MOBY_MCP_URL", "").startswith("https://"):
        raise SystemExit("Missing Moby secret")
    print(json.dumps(check_token(mint), indent=2))
    print("RESEARCH ONLY; no trades submitted.")

if __name__ == "__main__":
    main()
