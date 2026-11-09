import os
import unittest

class TestTonWalletDashboard(unittest.TestCase):
    def setUp(self):
        self.dashboard_path = os.path.join(
            os.path.dirname(__file__), "..", "ton-wallet-dashboard", "index.html"
        )
        self.assertTrue(os.path.exists(self.dashboard_path))
        with open(self.dashboard_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_accessible_copy_button(self):
        self.assertIn('id="copy-btn"', self.html)
        self.assertIn('aria-label="Copy wallet address"', self.html)
        self.assertIn('onclick="copyAddress()"', self.html)
        self.assertIn('currentAddress = address', self.html)
        self.assertIn('copyBtn.style.display = address ? \'inline-block\' : \'none\'', self.html)
        self.assertIn("btn.textContent = '✓ Copied'", self.html)
        self.assertIn("btn.setAttribute('aria-label', 'Wallet address copied')", self.html)

    def test_live_region_status(self):
        self.assertIn('id="activity"', self.html)
        self.assertIn('role="status"', self.html)
        self.assertIn('aria-live="polite"', self.html)

    def test_keyboard_focus_styling(self):
        self.assertIn('button:focus-visible', self.html)
        self.assertIn('outline:', self.html)

if __name__ == "__main__":
    unittest.main()
