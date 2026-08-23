import os
import urllib.parse

import requests


def normalize_whatsapp_number(phone_number: str) -> str:
    digits = ''.join(ch for ch in str(phone_number or '') if ch.isdigit())
    if not digits:
        return ''
    if digits.startswith('62'):
        return digits
    if digits.startswith('0'):
        return '62' + digits[1:]
    return '62' + digits


def build_wa_url(phone_number: str, message: str) -> str:
    normalized = normalize_whatsapp_number(phone_number)
    encoded_message = urllib.parse.quote(message)
    return f'https://wa.me/{normalized}?text={encoded_message}'


def send_whatsapp_message(api_token: str, phone_number_id: str, recipient: str, message: str):
    if not api_token or not phone_number_id:
        return {'ok': False, 'status': 'missing_credentials', 'error': 'API token atau phone number ID kosong'}

    normalized_recipient = normalize_whatsapp_number(recipient)
    if not normalized_recipient:
        return {'ok': False, 'status': 'invalid_recipient', 'error': 'Nomor WhatsApp penerima tidak valid'}

    url = f'https://graph.facebook.com/v18.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'messaging_product': 'whatsapp',
        'to': normalized_recipient,
        'type': 'text',
        'text': {'body': message},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        data = response.json() if response.content else {}

        if response.status_code in (200, 201, 202):
            return {
                'ok': True,
                'status': 'sent',
                'response': data,
            }

        return {
            'ok': False,
            'status': 'api_error',
            'http_status': response.status_code,
            'error': data,
        }
    except Exception as exc:
        return {
            'ok': False,
            'status': 'network_error',
            'error': str(exc),
        }
