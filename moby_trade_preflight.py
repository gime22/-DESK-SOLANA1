#!/usr/bin/env python3
"""Moby trading readiness: discover order schemas, check account, NO execution.

This deliberately never calls quick_buy, quick_sell, execute_swap, or create_order.
Output contains only availability flags, never balances, credentials or order data.
"""
import json
import os
from moby_readonly import call, VERSION

REQUIRED = ("get_my_guardrails", "get_my_balances", "get_swap_quote", "quick_buy", "quick_sell")

def main():
    if not os.environ.get("MOBY_MCP_URL", "").startswith("https://"):
        raise SystemExit("Missing private MOBY_MCP_URL secret")
    init, session = call("initialize", {"protocolVersion": VERSION, "capabilities": {},
        "clientInfo": {"name": "DESK-preflight", "version": "0.3"}}, 1)
    if init.get("error"):
        raise SystemExit("MCP initialization failed")
    response, session = call("tools/list", {}, 2, session)
    if response.get("error"):
        raise SystemExit("MCP tool discovery failed")
    tools = {t.get("name"): t for t in response.get("result", {}).get("tools", [])}
    missing = [name for name in REQUIRED if name not in tools]
    for name in REQUIRED:
        print(name + ": " + ("available" if name in tools else "MISSING"))
    if missing:
        raise SystemExit("Missing required tools; live trading BLOCKED")
    # Validate that required tool schemas exist before building a future executor.
    for name in ("get_swap_quote", "quick_buy", "quick_sell"):
        if not isinstance(tools[name].get("inputSchema"), dict):
            raise SystemExit(name + " has no input schema; live trading BLOCKED")
    for ident, name in enumerate(("get_my_guardrails", "get_my_balances"), 3):
        result, session = call("tools/call", {"name": name, "arguments": {}}, ident, session)
        if result.get("error") or result.get("result", {}).get("isError"):
            raise SystemExit(name + " failed; live trading BLOCKED")
        print(name + ": read-only response received (private)")
    print("PREFLIGHT PASS: tool discovery and account reads succeeded.")
    print("LIVE TRADING REMAINS DISABLED. No quote or order submitted.")

if __name__ == "__main__":
    main()
