import unittest
import asyncio
from alcanza_check.checks import check_dns, check_tcp, check_ssl, check_ping

class TestChecks(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_dns_lookup(self):
        result = self.loop.run_until_complete(check_dns("google.com"))
        self.assertEqual(result['status'], 'passed')
        self.assertIn('.', result['details'])

    def test_tcp_connection(self):
        # google.com port 443 should be open
        result = self.loop.run_until_complete(check_tcp("google.com", 443))
        self.assertEqual(result['status'], 'passed')

    def test_ssl_validation(self):
        # google.com should have a valid SSL cert
        result = self.loop.run_until_complete(check_ssl("google.com", 443))
        self.assertEqual(result['status'], 'passed')
        self.assertIn('Valid until', result['details'])

    def test_ping(self):
        # google.com should be pingable (usually)
        result = self.loop.run_until_complete(check_ping("google.com"))
        # Some environments might block ICMP, so we just check it doesn't crash
        self.assertIn(result['status'], ['passed', 'failed'])

if __name__ == '__main__':
    unittest.main()
