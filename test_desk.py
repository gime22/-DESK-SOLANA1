import tempfile
import pathlib
import unittest
from argparse import Namespace
from unittest.mock import patch
import desk

class DeskTests(unittest.TestCase):
    def test_full_paper_flow_and_no_rescan(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(desk, "DB", pathlib.Path(tmp) / "trades.json"):
                desk.run(Namespace(command="scan", token="TEST", source="manual sample"))
                desk.run(Namespace(command="verify", token="TEST", safe="yes", volume="1000", liquidity="500", holders="25", contract="reviewed", smart_money="unknown", reason=""))
                desk.run(Namespace(command="execute", token="TEST", entry="1", stop="0.8", take="1.5", size="0.1", reason="test"))
                self.assertEqual(desk.available(desk.load()), desk.Decimal("0.4"))
                desk.run(Namespace(command="exit", token="TEST", price="1.5"))
                self.assertEqual(desk.load()["trades"]["TEST"]["pnl_sol"], "0.05")
                with self.assertRaises(ValueError):
                    desk.run(Namespace(command="scan", token="TEST", source="again"))
    def test_source_down_skip_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(desk, "DB", pathlib.Path(tmp) / "trades.json"):
                desk.run(Namespace(command="scan", token="DOWN", source="down"))
                self.assertEqual(desk.load()["trades"]["DOWN"]["stage"], "SKIP")
                with self.assertRaises(ValueError):
                    desk.run(Namespace(command="scan", token="DOWN", source="new"))

if __name__ == "__main__":
    unittest.main()
