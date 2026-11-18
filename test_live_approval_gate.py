import unittest
from live_approval_gate import proposal

TOKEN="So11111111111111111111111111111111111111112"

class ApprovalGateTests(unittest.TestCase):
    def test_proposal_waits_for_approval(self):
        p=proposal(TOKEN,"0.01","100","90","120",True)
        self.assertEqual(p["status"],"AWAITING_EXPLICIT_USER_APPROVAL")
        self.assertEqual(p["mode"],"MANUAL_APPROVAL_ONLY")
    def test_requires_verify(self):
        with self.assertRaises(ValueError):
            proposal(TOKEN,"0.01","100","90","120",False)
    def test_rejects_oversized_trade(self):
        with self.assertRaises(ValueError):
            proposal(TOKEN,"0.5","100","90","120",True)
    def test_rejects_bad_stop(self):
        with self.assertRaises(ValueError):
            proposal(TOKEN,"0.01","100","110","120",True)
    def test_rejects_fake_token(self):
        with self.assertRaises(ValueError):
            proposal("NOT_A_MINT","0.01","100","90","120",True)

if __name__=="__main__":
    unittest.main()
