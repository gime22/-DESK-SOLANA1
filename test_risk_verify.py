import unittest
from risk_verify import evaluate

class RiskVerificationTests(unittest.TestCase):
    def test_empty_is_skip(self):
        x=evaluate({},now_ms=2000000000000)
        self.assertEqual(x["decision"],"SKIP")
        self.assertFalse(x["live_trading_allowed"])
    def test_market_metrics_alone_are_insufficient(self):
        x=evaluate({"created_at_ms":1999990000000,"liquidity_usd":100000,"volume_24h_usd":200000},now_ms=2000000000000)
        self.assertEqual(x["decision"],"SKIP")
    def test_complete_evidence_is_watchlist_not_trade(self):
        x=evaluate({"created_at_ms":1999990000000,"liquidity_usd":100000,"volume_24h_usd":200000,"holders":250,"top10_holder_pct":20,"mint_authority_disabled":True,"freeze_authority_disabled":True,"sellable":True,"smart_money_verified":True,"verification_sources":{"holders":"source1","contract":"source2","smart_money":"source3","market":"source4"}},now_ms=2000000000000)
        self.assertEqual(x["decision"],"WATCHLIST_MANUAL_REVIEW")
        self.assertFalse(x["live_trading_allowed"])
    def test_old_launch_is_skip(self):
        x=evaluate({"created_at_ms":1900000000000},now_ms=2000000000000)
        self.assertEqual(x["decision"],"SKIP")
if __name__=="__main__":
    unittest.main()
