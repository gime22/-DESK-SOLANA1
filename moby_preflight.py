#!/usr/bin/env python3
"""DESK Moby execution preflight. Safe by default: NEVER submits orders."""
import argparse
import json
import os
from decimal import Decimal, InvalidOperation

def positive(value):
    try:
        d = Decimal(value)
        if not d.is_finite() or d <= 0:
            raise ValueError()
        return d
    except (InvalidOperation, ValueError):
        raise argparse.ArgumentTypeError("Jumlah harus angka positif")

def main():
    p = argparse.ArgumentParser(description="Moby order preflight; no live execution")
    p.add_argument("--side", choices=("buy", "sell"), required=True)
    p.add_argument("--token", required=True, help="Solana token mint address")
    p.add_argument("--amount", type=positive, required=True)
    p.add_argument("--unit", choices=("SOL", "USDC", "TOKEN"), required=True)
    p.add_argument("--live", action="store_true", help="Not implemented; fail closed")
    args = p.parse_args()
    if args.live:
        p.error("LIVE DISABLED: Moby transport, authorization, order confirmation and risk checks are not integrated")
    if not (32 <= len(args.token) <= 44 and all(c in "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz" for c in args.token)):
        p.error("Invalid Solana mint address")
    if args.side == "buy" and args.unit == "TOKEN":
        p.error("Buy amount must be in SOL or USDC")
    if args.side == "sell" and args.unit != "TOKEN":
        p.error("Sell amount must be in TOKEN units")
    print(json.dumps({
        "mode":"DRY_RUN_ONLY",
        "provider":"Moby (NOT CONNECTED TO THIS SCRIPT)",
        "side":args.side.upper(),
        "mint":args.token,
        "amount":str(args.amount),
        "unit":args.unit,
        "order_sent":False,
        "next":"Moby API/MCP transport and explicit authorization must be verified before live trading"
    }, indent=2))
if __name__ == "__main__":
    main()
