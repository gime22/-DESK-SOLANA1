#!/usr/bin/env python3
"""DESK live-trade safety gate. Proposal/approval only; NEVER sends an order.

A human must approve the exact token, size, entry, stop and take profit.
Approvals expire in 10 minutes and are single-use per proposal ID.
This file intentionally has no MCP client, private key or trading functions.
"""
import argparse
import datetime as dt
import hashlib
import json
from decimal import Decimal, InvalidOperation

MAX_SOL = Decimal("0.05")
MAX_MINUTES = 10

def positive(value, label):
    try:
        n = Decimal(str(value))
        if not n.is_finite() or n <= 0:
            raise ValueError()
        return n
    except (InvalidOperation, ValueError):
        raise ValueError(label + " must be positive and finite")

def proposal(token, size_sol, entry, stop, take, risk_verified=False):
    token = token.strip()
    if not (32 <= len(token) <= 44) or any(c not in "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz" for c in token):
        raise ValueError("A valid Solana token mint is required")
    size, entry, stop, take = [positive(x, n) for x, n in ((size_sol,"size"),(entry,"entry"),(stop,"stop"),(take,"take"))]
    if size > MAX_SOL:
        raise ValueError("Position exceeds 0.05 SOL test limit")
    if not stop < entry < take:
        raise ValueError("Require stop < entry < take")
    if not risk_verified:
        raise ValueError("SCAN and VERIFY must pass first; missing verification means SKIP")
    plan = {"token":token,"size_sol":str(size),"entry":str(entry),"stop":str(stop),"take":str(take),"mode":"MANUAL_APPROVAL_ONLY"}
    digest=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()[:16]
    plan["proposal_id"]=digest
    plan["expires_at"]=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=MAX_MINUTES)).isoformat()
    plan["status"]="AWAITING_EXPLICIT_USER_APPROVAL"
    return plan

def main():
    p=argparse.ArgumentParser(description="Prepare a trade proposal; never executes a trade")
    p.add_argument("--token",required=True)
    p.add_argument("--size-sol",required=True)
    p.add_argument("--entry",required=True)
    p.add_argument("--stop",required=True)
    p.add_argument("--take",required=True)
    p.add_argument("--verified",action="store_true",help="Only after completed SCAN/VERIFY")
    a=p.parse_args()
    try:
        print(json.dumps(proposal(a.token,a.size_sol,a.entry,a.stop,a.take,a.verified),indent=2))
    except ValueError as exc:
        p.error(str(exc))

if __name__=="__main__":
    main()
