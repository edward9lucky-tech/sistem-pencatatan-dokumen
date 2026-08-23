import unittest
from unittest.mock import patch

from whatsapp_utils import build_wa_url, normalize_whatsapp_number, send_whatsapp_message


class TestWhatsappUtils(unittest.TestCase):
    def test_normalize_whatsapp_number(self):
        self.assertEqual(normalize_whatsapp_number('081234567890'), '6281234567890')
        self.assertEqual(normalize_whatsapp_number('+62 812-3456-7890'), '6281234567890')
        self.assertEqual(normalize_whatsapp_number('6281234567890'), '6281234567890')

    def test_build_wa_url(self):
        url = build_wa_url('6281234567890', 'Hallo admin')
        self.assertIn('wa.me/6281234567890', url)
        self.assertIn('Hallo%20admin', url)

    @patch('whatsapp_utils.requests.post')
    def test_send_whatsapp_message_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'messages': [{'id': 'abc'}]}

        result = send_whatsapp_message(
            'token123',
            'phoneid123',
            '6281234567890',
            'OTP: 123456'
        )

        self.assertTrue(result['ok'])
        self.assertEqual(result['status'], 'sent')
        mock_post.assert_called_once()

    @patch('whatsapp_utils.requests.post')
    def test_send_whatsapp_message_missing_credentials(self, mock_post):
        result = send_whatsapp_message('', '', '6281234567890', 'OTP: 123456')

        self.assertFalse(result['ok'])
        self.assertEqual(result['status'], 'missing_credentials')
        mock_post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
