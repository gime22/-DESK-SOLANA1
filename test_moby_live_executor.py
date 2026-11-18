import unittest
from moby_live_executor import validate

MINT = "So11111111111111111111111111111111111111112"

class LiveGateTests(unittest.TestCase):
    def test_buy_requires_attestation(self):
        with self.assertRaisesRegex(ValueError, "attestation"):
            validate("BUY", MINT, "5", "100", 50, "APPROVE BUY "+MINT+" 5", False)
    def test_sell_requires_attestation(self):
        with self.assertRaisesRegex(ValueError, "attestation"):
            validate("SELL", MINT, "5", "50", 50, "APPROVE SELL "+MINT+" 50", False)
    def test_wrong_approval(self):
        with self.assertRaisesRegex(ValueError, "approval"):
            validate("BUY", MINT, "5", "100", 50, "YES", False)
    def test_buy_cap(self):
        with self.assertRaisesRegex(ValueError, "cap"):
            validate("BUY", MINT, "11", "100", 50, "APPROVE BUY "+MINT+" 11", False)
    def test_slippage_cap(self):
        with self.assertRaisesRegex(ValueError, "Slippage"):
            validate("BUY", MINT, "5", "100", 101, "APPROVE BUY "+MINT+" 5", False)
    def test_sell_cap(self):
        with self.assertRaisesRegex(ValueError, "exceeds"):
            validate("SELL", MINT, "5", "101", 50, "APPROVE SELL "+MINT+" 101", False)
if __name__ == "__main__":
    unittest.main()
