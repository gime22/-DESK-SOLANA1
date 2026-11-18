#!/usr/bin/env python3
"""DESK BUY/SELL dry-run smoke test. No wallet access or network calls."""
from decimal import Decimal
import json
from live_approval_gate import proposal

TOKEN="So11111111111111111111111111111111111111112"
ENTRY=Decimal("100")
STOP=Decimal("95")
TAKE=Decimal("110")
SIZE=Decimal("0.01")

def main():
    p=proposal(TOKEN,str(SIZE),str(ENTRY),str(STOP),str(TAKE),True)
    assert p["status"]=="AWAITING_EXPLICIT_USER_APPROVAL"
    print(json.dumps({"stage":"BUY","mode":"DRY_RUN","size_sol":str(SIZE),"status":"SIMULATED_ONLY","proposal_id":p["proposal_id"]}))
    exit_price=TAKE
    pnl=SIZE*(exit_price/ENTRY-Decimal("1"))
    print(json.dumps({"stage":"SELL","mode":"DRY_RUN","exit_price":str(exit_price),"pnl_sol":str(pnl),"status":"SIMULATED_ONLY"}))
    print("PASS: BUY and SELL simulation complete. No real orders submitted.")

if __name__=="__main__":
    main()
