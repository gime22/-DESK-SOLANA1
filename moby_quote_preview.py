#!/usr/bin/env python3
"""Moby read-only swap quote preview. Never places an order.
The amount is a Moby quote input unit; do not infer USD without provider confirmation.
"""
import json
import os
import re
from decimal import Decimal, InvalidOperation
from moby_readonly import call, VERSION

MINT = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

def validate(mint, amount):
    if not MINT.fullmatch(mint):
        raise ValueError("Invalid Solana token mint")
    try:
        value = Decimal(amount)
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid quote amount")
    if not value.is_finite() or not Decimal("0") < value <= Decimal("10"):
        raise ValueError("Quote amount must be >0 and <=10")
    return float(value)

def main():
    mint = os.environ.get("DESK_TOKEN_MINT", "")
    amount = validate(mint, os.environ.get("DESK_QUOTE_AMOUNT", "1"))
    if not os.environ.get("MOBY_MCP_URL", "").startswith("https://"):
        raise SystemExit("Moby secret unavailable")
    init, session = call("initialize", {"protocolVersion":VERSION, "capabilities":{},
        "clientInfo":{"name":"DESK-quote-preview","version":"1.0"}}, 1)
    if init.get("error"):
        raise SystemExit("Moby initialization failed")
    tools, session = call("tools/list", {}, 2, session)
    names = {x.get("name") for x in tools.get("result",{}).get("tools",[])}
    if "get_swap_quote" not in names:
        raise SystemExit("Moby quote tool unavailable")
    # Moby's quote input_token uses its token identifier; this USDC mint is Solana native USDC.
    usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    quote, session = call("tools/call", {"name":"get_swap_quote",
        "arguments":{"input_token":usdc,"output_token":mint,"amount":amount}}, 3, session)
    if quote.get("error") or quote.get("result",{}).get("isError"):
        raise SystemExit("Quote rejected by Moby; no order")
    # Avoid leaking account/quote internals into public GitHub logs.
    print("Moby BUY quote returned successfully; response redacted.")
    print("NO ORDER EXECUTED. Manual review of quote units, fees and price is still required.")

if __name__ == "__main__":
    main()
