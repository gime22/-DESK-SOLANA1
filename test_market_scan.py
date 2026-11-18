import unittest
import market_scan

class MarketScanTests(unittest.TestCase):
    def test_missing_source_is_safe(self):
        def offline(_):
            raise OSError("offline")
        result = market_scan.scan(offline)
        self.assertEqual(result["candidates"], [])
        self.assertTrue(result["warnings"])

    def test_candidate_is_not_approved_from_market_data_alone(self):
        def fake(path):
            if "profiles" in path:
                return [{"chainId": "solana", "tokenAddress": "ExampleMint"}]
            return [{"chainId": "solana", "pairAddress": "Pair", "liquidity": {"usd": 20000}, "volume": {"h24": 120000}, "priceUsd": "0.01"}]
        result = market_scan.scan(fake)
        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(result["candidates"][0]["decision"], "SKIP")
        self.assertEqual(result["candidates"][0]["liquidity_usd"], 20000)

if __name__ == "__main__":
    unittest.main()
