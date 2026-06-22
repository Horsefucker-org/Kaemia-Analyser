import unittest
from unittest.mock import patch, Mock

from safety_checker import run_all_checks


class TestRunAllChecks(unittest.TestCase):
    @patch('safety_checker.requests.get')
    def test_basic_run(self, mock_get):
        html = b"<html><head><title>Test</title><meta name=\"description\" content=\"desc\"></head><body><form action=\"/login\"><input type=\"password\" name=\"pw\"></form><a href=\"/about\">about</a></body></html>"
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.content = html
        mock_resp.headers = {'Server': 'test', 'Set-Cookie': ''}
        mock_resp.cookies = []
        mock_resp.url = 'https://example.com'
        mock_get.return_value = mock_resp

        res = run_all_checks('https://example.com', deep=True)
        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['forms_count'], 1)
        self.assertIn('title', res)


if __name__ == '__main__':
    unittest.main()
