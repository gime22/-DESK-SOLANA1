#!/usr/bin/env python3
"""DESK guarded Moby BUY/SELL executor.

Only callable by manual GitHub workflow_dispatch. No scheduled/push order path.
Live orders remain fail-closed until a separate, independently verified risk
attestation is supplied. This prevents an input checkbox from bypassing SCAN/VERIFY.
"""
import json
import os
import re
import sys
from decimal import Decimal, InvalidOperation
from moby_readonly import call, VERSION

MINT = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
MAX_BUY_USD = Decimal("10")
MAX_SLIPPAGE_BPS = 100
MAX_SELL_PCT = Decimal("100")

def amount(raw, label):
    try:
        value = Decimal(str(raw))
    except (InvalidOperation, ValueError):
        raise ValueError(label + " is invalid")
    if not value.is_finite() or value <= 0:
        raise ValueError(label + " must be positive")
    return value

def validate(action, mint, usd, pct, slippage, approval, verified):
    if action not in ("BUY", "SELL"):
        raise ValueError("Unsupported action")
    if not MINT.fullmatch(mint):
        raise ValueError("Invalid Solana mint")
    if not isinstance(slippage, int) or not 1 <= slippage <= MAX_SLIPPAGE_BPS:
        raise ValueError("Slippage must be 1-100 bps")
    if action == "BUY":
        qty = amount(usd, "USD buy amount")
        if qty > MAX_BUY_USD:
            raise ValueError("BUY cap is $10")
        expected = "APPROVE BUY " + mint + " " + str(qty)
    else:
        qty = amount(pct, "Sell percentage")
        if qty > MAX_SELL_PCT:
            raise ValueError("SELL percentage exceeds 100")
        expected = "APPROVE SELL " + mint + " " + str(qty)
    if approval != expected:
        raise ValueError("Exact manual approval phrase does not match")
    if verified is not True:
        raise ValueError("Independent verified SCAN/VERIFY attestation missing; order BLOCKED")
    return qty

def main():
    if os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch":
        raise SystemExit("Live orders require a manual workflow dispatch")
    action = os.environ.get("DESK_ACTION", "").upper()
    mint = os.environ.get("DESK_MINT", "")
    try:
        slippage = int(os.environ.get("DESK_SLIPPAGE_BPS", "50"))
        # Critical: never accept an unverified checkbox/CLI input as safety attestation.
        # This will only be enabled after implementing trusted evidence verification.
        qty = validate(action, mint, os.environ.get("DESK_BUY_USD", ""),
            os.environ.get("DESK_SELL_PCT", ""), slippage,
            os.environ.get("DESK_APPROVAL", ""), verified=False)
    except (ValueError, TypeError) as exc:
        print("ORDER BLOCKED:", exc)
        return 2
    # Unreachable until independent evidence validation is implemented.
    # No network or wallet calls are made from this file while blocked.
    raise RuntimeError("Executor disabled pending independent attestation")

if __name__ == "__main__":
    sys.exit(main())
