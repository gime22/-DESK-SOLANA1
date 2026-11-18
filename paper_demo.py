"""Synthetic demonstration only; no live prices or wallet operations."""
import json, pathlib, tempfile
from argparse import Namespace
from unittest.mock import patch
import desk

def main():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(desk, "DB", pathlib.Path(tmp) / "trades.json"):
            desk.run(Namespace(command="scan", token="SYNTHETIC_DEMO", source="synthetic demo, NOT LIVE"))
            desk.run(Namespace(command="verify", token="SYNTHETIC_DEMO", safe="yes", volume="10000", liquidity="5000", holders="150", contract="synthetic only", smart_money="synthetic only", reason=""))
            desk.run(Namespace(command="execute", token="SYNTHETIC_DEMO", entry="1", stop="0.9", take="1.2", size="0.02", reason="test only"))
            desk.run(Namespace(command="exit", token="SYNTHETIC_DEMO", price="1.1"))
            result=desk.load()
    pathlib.Path("reports").mkdir(exist_ok=True)
    pathlib.Path("reports/paper-demo.json").write_text(json.dumps({"disclaimer":"SYNTHETIC PAPER DATA ONLY; NOT LIVE",**result},indent=2))
    print("Synthetic report generated; no real trading.")

if __name__=="__main__":
    main()
