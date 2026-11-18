#!/usr/bin/env python3
"""Inspect Moby order argument schemas privately, without sending any orders.

Prints field names/types/required only. No API keys, balances, or descriptions.
This is necessary to avoid guessing buy/sell parameters.
"""
import os
from moby_readonly import call, VERSION

def main():
    if not os.environ.get("MOBY_MCP_URL", "").startswith("https://"):
        raise SystemExit("MOBY_MCP_URL is not configured")
    init, session = call("initialize", {"protocolVersion": VERSION, "capabilities": {},
        "clientInfo": {"name": "DESK-schema-inspector", "version": "1.0"}}, 1)
    if init.get("error"):
        raise SystemExit("MCP initialization failed")
    response, session = call("tools/list", {}, 2, session)
    if response.get("error"):
        raise SystemExit("MCP tool listing failed")
    tools = {x.get("name"): x for x in response.get("result", {}).get("tools", [])}
    for name in ("get_swap_quote", "quick_buy", "quick_sell", "get_token_overview", "get_token_key_holders", "get_token_smart_money"):
        schema = (tools.get(name) or {}).get("inputSchema") or {}
        fields = schema.get("properties") or {}
        required = set(schema.get("required") or [])
        print(name + ":")
        if not fields:
            print("  SCHEMA_UNAVAILABLE")
            continue
        for key, meta in fields.items():
            if not isinstance(meta, dict):
                continue
            field_type = meta.get("type", "unspecified")
            if not isinstance(field_type, str):
                field_type = "complex"
            print("  " + str(key) + ": " + field_type + (" REQUIRED" if key in required else " optional"))
    print("INSPECTION ONLY. NO BUY OR SELL WAS SUBMITTED.")

if __name__ == "__main__":
    main()
