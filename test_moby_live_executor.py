import unittest
from moby_live_executor import validate, buy_arguments, execute_verified_buy

MINT = "So11111111111111111111111111111111111111112"

class LiveGateTests(unittest.TestCase):
    def test_buy_requires_attestation(self):
        with self.assertRaisesRegex(ValueError, "attestation"):
            validate("BUY", MINT, "5", "100", 50, "APPROVE BUY "+MINT+" 5", False)
    def test_sell_exact_approval_for_exit(self):
        self.assertEqual(str(validate("SELL", MINT, "5", "50", 50, "APPROVE SELL "+MINT+" 50", False)), "50")
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
class BuyIntegrationTests(unittest.TestCase):
    def test_buy_blocked_without_verification(self):
        with self.assertRaisesRegex(ValueError, "verification"):
            buy_arguments(MINT, "5", False)
    def test_buy_request_has_real_moby_fields(self):
        self.assertEqual(buy_arguments(MINT, "5", True),
                         {"output_token": MINT, "amount_usd": 5.0})
    def test_buy_integration_mock_never_moves_money(self):
        calls = []
        def fake_call(method, params, ident, session):
            calls.append((method, params, ident))
            return {"result": {"content": [{"type": "text", "text": "mock"}]}}, session
        execute_verified_buy(MINT, "5", True, "test-session", fake_call)
        self.assertEqual(calls[0][1]["name"], "quick_buy")
        self.assertEqual(calls[0][1]["arguments"]["amount_usd"], 5.0)
if __name__ == "__main__":
    unittest.main()
