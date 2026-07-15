import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.collectors.massive import MassiveConnector


class MassiveConnectorTests(unittest.TestCase):
    def test_builds_request_with_api_key_and_ticker(self):
        connector = MassiveConnector(api_key="demo-key")
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2)

        url, headers, params = connector._build_request("AAPL", "1h", start, end)

        self.assertIn("https://api.massive.com/v2/aggs/ticker/AAPL/range", url)
        self.assertEqual(params.get("apiKey"), "demo-key")
        self.assertEqual(headers.get("Authorization"), "Bearer demo-key")


if __name__ == "__main__":
    unittest.main()
