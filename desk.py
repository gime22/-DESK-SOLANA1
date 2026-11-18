#!/usr/bin/env python3
"""DESK: Solana memecoin paper-only desk. Standard library only."""
import argparse, json, pathlib, datetime, math
from decimal import Decimal, InvalidOperation

ROOT = pathlib.Path(__file__).resolve().parent
DB = ROOT / "paper_trades.json"
STAGES = ("SCAN", "VERIFY", "EXECUTE", "EXIT")
CAPITAL = Decimal("0.5")

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def load():
    if not DB.exists():
        return {"starting_sol": str(CAPITAL), "trades": {}}
    return json.loads(DB.read_text())

def save(db):
    tmp = DB.with_suffix(".tmp")
    tmp.write_text(json.dumps(db, indent=2, ensure_ascii=False))
    tmp.replace(DB)

def number(value, name, positive=True):
    try:
        n = Decimal(str(value))
        if not n.is_finite() or (positive and n <= 0) or (not positive and n < 0):
            raise ValueError()
        return n
    except (InvalidOperation, ValueError):
        raise ValueError(name + " harus angka valid" + (" > 0" if positive else " >= 0"))

def available(db):
    reserved = sum((Decimal(t["size_sol"]) for t in db["trades"].values() if t["stage"] == "EXECUTE"), Decimal(0))
    pnl = sum((Decimal(t.get("pnl_sol", "0")) for t in db["trades"].values() if t["stage"] == "EXIT"), Decimal(0))
    return CAPITAL + pnl - reserved

def run(args):
    db = load()
    trades = db["trades"]
    if args.command == "status":
        print(json.dumps({"mode": "PAPER ONLY", "available_sol": str(available(db)), "trades": trades}, indent=2))
        return
    token = args.token.strip()
    if not token:
        raise ValueError("Token wajib diisi")
    if args.command == "scan":
        if token in trades:
            raise ValueError("Token sudah pernah diproses. Tidak boleh mengulang SCAN termasuk token SKIP.")
        # No market data is fabricated. A source must be explicitly documented.
        source = args.source.strip()
        if not source or source.lower() in ("down", "unavailable", "none"):
            trades[token] = {"stage": "SKIP", "reason": "Sumber data tidak tersedia: " + (source or "tidak disebutkan"), "time": now()}
        else:
            trades[token] = {"stage": "SCAN", "source": source, "time": now()}
        save(db)
    elif args.command == "verify":
        t = trades.get(token)
        if not t or t["stage"] != "SCAN":
            raise ValueError("VERIFY hanya sesudah SCAN. SKIP bersifat final.")
        if args.safe != "yes":
            t.update(stage="SKIP", reason=args.reason or "Verifikasi risiko gagal", time=now())
        else:
            required = {"volume_usd": args.volume, "liquidity_usd": args.liquidity, "holders": args.holders, "contract_check": args.contract, "smart_money": args.smart_money}
            if any(v is None or str(v).strip() == "" for v in required.values()):
                t.update(stage="SKIP", reason="Data verifikasi tidak lengkap", time=now())
            else:
                volume = number(args.volume, "volume")
                liquidity = number(args.liquidity, "liquidity")
                holders = number(args.holders, "holders")
                if holders != holders.to_integral_value():
                    raise ValueError("holders harus bilangan bulat")
                t.update(stage="VERIFY", metrics={**required, "volume_usd": str(volume), "liquidity_usd": str(liquidity), "holders": str(holders)}, time=now())
        save(db)
    elif args.command == "execute":
        t = trades.get(token)
        if not t or t["stage"] != "VERIFY":
            raise ValueError("EXECUTE hanya sesudah VERIFY")
        entry, stop, take, size = (number(getattr(args, k), k) for k in ("entry", "stop", "take", "size"))
        if not stop < entry < take:
            raise ValueError("Untuk posisi long: stop < entry < take")
        if size > available(db):
            raise ValueError("Modal simulasi tidak cukup")
        t.update(stage="EXECUTE", entry=str(entry), stop=str(stop), take=str(take), size_sol=str(size), rationale=args.reason, time=now())
        save(db)
    elif args.command == "exit":
        t = trades.get(token)
        if not t or t["stage"] != "EXECUTE":
            raise ValueError("EXIT hanya sesudah EXECUTE")
        exit_price = number(args.price, "price")
        pnl = Decimal(t["size_sol"]) * (exit_price / Decimal(t["entry"]) - 1)
        t.update(stage="EXIT", exit_price=str(exit_price), pnl_sol=str(pnl), time=now())
        save(db)
    print(json.dumps(trades[token], indent=2, ensure_ascii=False))

def main():
    p = argparse.ArgumentParser(description="DESK paper-only. No wallet, signing or swaps.")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    s = sub.add_parser("scan"); s.add_argument("token"); s.add_argument("--source", default="")
    v = sub.add_parser("verify"); v.add_argument("token"); v.add_argument("--safe", choices=["yes", "no"], required=True)
    for field in ("volume", "liquidity", "holders", "contract", "smart_money", "reason"):
        v.add_argument("--" + field.replace("_", "-"), dest=field)
    e = sub.add_parser("execute"); e.add_argument("token")
    for field in ("entry", "stop", "take", "size"):
        e.add_argument("--" + field, required=True)
    e.add_argument("--reason", default="")
    x = sub.add_parser("exit"); x.add_argument("token"); x.add_argument("--price", required=True)
    args = p.parse_args()
    try:
        run(args)
    except (ValueError, KeyError) as exc:
        p.error(str(exc))

if __name__ == "__main__":
    main()
