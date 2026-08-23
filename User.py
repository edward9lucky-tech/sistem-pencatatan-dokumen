import os
import time
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
  from dotenv import load_dotenv
except ModuleNotFoundError:
  def load_dotenv(*args, **kwargs):
    return False

from whatsapp_utils import build_wa_url, normalize_whatsapp_number, send_whatsapp_message

load_dotenv(Path(__file__).resolve().parent / '.env')

# File database excel lokal
USER_FILE = 'users.xlsx'
SUPER_ADMIN_WA = os.getenv('SUPER_ADMIN_WA', '628123456789')
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN', '')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID', '')


def send_approval_to_admin(reg_user, reg_wa):
  admin_phone = normalize_whatsapp_number(SUPER_ADMIN_WA)
  if not admin_phone:
    return {'ok': False, 'status': 'missing_admin_phone', 'message': 'Nomor admin kosong'}

  message = (
      'Permohonan pendaftaran akun baru\n'
      f'Username: {reg_user.strip()}\n'
      f'Nomor WA pendaftar: {reg_wa.strip()}\n'
      'Status: menunggu persetujuan Super Admin'
  )

  if WHATSAPP_API_TOKEN and WHATSAPP_PHONE_ID:
    result = send_whatsapp_message(
        WHATSAPP_API_TOKEN,
        WHATSAPP_PHONE_ID,
        admin_phone,
        message,
    )
    if result.get('ok'):
      return {'ok': True, 'status': 'sent', 'message': 'Permohonan terkirim otomatis ke admin'}
    return {'ok': False, 'status': result.get('status', 'api_error'), 'message': result.get('error', 'Gagal kirim API WhatsApp')}

  wa_url = build_wa_url(admin_phone, message)
  return {'ok': False, 'status': 'fallback_link', 'message': wa_url}


@st.dialog('Kirim Permohonan WhatsApp')
def show_whatsapp_popup(wa_url):
  st.write('Klik tombol di bawah untuk membuka WhatsApp dalam jendela popup.')
  popup_url = json.dumps(wa_url).replace('&', '&amp;')
  components.html(
      f'''<a href={popup_url} target="whatsapp_popup"
      style="display:inline-block;background:#128C7E;color:white;border-radius:6px;padding:10px 20px;font-weight:600;text-decoration:none;">
      Buka WhatsApp</a>''',
      height=50,
  )
  if st.button('Tutup dan Refresh', type='primary'):
    st.session_state.whatsapp_popup_url = None
    st.session_state.menu = 'Login'
    for field_key in ('reg_user', 'reg_pass', 'reg_wa'):
      st.session_state.pop(field_key, None)
    st.rerun()


def normalize_user_df(df):
  required_cols = ['username', 'password', 'no_wa', 'status', 'role']
  for col in required_cols:
    if col not in df.columns:
      df[col] = ''

  df = df.copy()
  df['username'] = df['username'].astype(str).str.strip()
  df['password'] = df['password'].astype(str).str.strip()
  df['no_wa'] = df['no_wa'].astype(str).str.strip()
  df['status'] = df['status'].fillna('approved').astype(str).str.strip().str.lower()
  df['role'] = df['role'].fillna('user').astype(str).str.strip().str.lower()

  admin_mask = df['username'].astype(str).str.strip().str.lower() == 'edward'
  if admin_mask.any():
    df.loc[admin_mask, 'password'] = '090990'
    df.loc[admin_mask, 'status'] = 'approved'
    df.loc[admin_mask, 'role'] = 'superadmin'
  else:
    df = pd.concat([
        df,
        pd.DataFrame([{'username': 'edward', 'password': '090990', 'no_wa': '628123456789', 'status': 'approved', 'role': 'superadmin'}])
    ], ignore_index=True)

  return df


def load_users():
  default_users = pd.DataFrame(
      {
          'username': ['edward'],
          'password': ['090990'],
          'no_wa': ['628123456789'],
          'status': ['approved'],
          'role': ['superadmin'],
      }
  )

  if not os.path.exists(USER_FILE):
    default_users.to_excel(USER_FILE, index=False)
    return default_users

  try:
    df = pd.read_excel(USER_FILE, dtype=str)
    required_cols = ['username', 'password', 'no_wa']
    if not all(col in df.columns for col in required_cols):
      default_users.to_excel(USER_FILE, index=False)
      return default_users

    normalized = normalize_user_df(df)
    normalized.to_excel(USER_FILE, index=False)
    return normalized
  except Exception:
    default_users.to_excel(USER_FILE, index=False)
    return default_users


def save_user(username, password, no_wa, status='pending', role='user'):
  df = load_users()
  df = normalize_user_df(df)
  new_row = pd.DataFrame(
      [{
          'username': username,
          'password': password,
          'no_wa': no_wa,
          'status': status,
          'role': role
      }]
  )
  df = pd.concat([df, new_row], ignore_index=True)
  df = normalize_user_df(df)
  df.to_excel(USER_FILE, index=False)


# Session state untuk status login
if 'logged_in' not in st.session_state:
  st.session_state.logged_in = False
if 'username' not in st.session_state:
  st.session_state.username = ''
if 'whatsapp_popup_url' not in st.session_state:
  st.session_state.whatsapp_popup_url = None

df_users = load_users()

# --- HALAMAN JIKA SUDAH LOGIN ---
if st.session_state.logged_in:
  user_row = df_users[df_users['username'].astype(str).str.strip().str.lower() == st.session_state.username.lower()]
  if not user_row.empty and user_row.iloc[0].get('role', '').lower() == 'superadmin':
    time.sleep(1)
    st.switch_page('pages/New.py')
  else:
    time.sleep(1)
    st.switch_page('pages/New.py')

# --- HALAMAN LOGIN & REGISTRASI ---
else:
  st.title('Sistem Arsip & Dokumen')
  menu = st.selectbox('Pilih Menu', ['Login', 'Register / Daftar Akun'], key='menu')

  if menu == 'Login':
    st.subheader('Silakan Login')
    username_input = st.text_input('Username')
    password_input = st.text_input('Password', type='password')

    if st.button('Login'):
      # Membersihkan spasi inputan
      u_input = username_input.strip()
      p_input = str(password_input).strip()

      # Mencari kecocokan data secara fleksibel (mengabaikan huruf besar/kecil pada username)
      df_users['clean_user'] = df_users['username'].astype(str).str.strip().str.lower()
      user_row = df_users[df_users['clean_user'] == u_input.lower()]

      if not user_row.empty:
        db_pass = str(user_row.iloc[0]['password']).strip()
        if db_pass == p_input:
          status_user = str(user_row.iloc[0].get('status', 'approved')).strip().lower()
          if status_user not in ('approved', 'aktif', 'active'):
            st.warning('Akun Anda masih menunggu persetujuan Super Admin.')
          else:
            st.session_state.logged_in = True
            st.session_state.username = user_row.iloc[0]['username']
            st.success('Login Berhasil!')
            time.sleep(1)
            st.rerun()
        else:
          st.error('Password salah!')
      else:
        st.error('Username tidak ditemukan!')

  elif menu == 'Register / Daftar Akun':
    st.subheader('Daftar Akun Baru - Ajukan ke Super Admin')

    with st.form('registration_form'):
      reg_user = st.text_input('Buat Username Baru', key='reg_user')
      reg_pass = st.text_input('Buat Password Baru', type='password', key='reg_pass')
      reg_wa = st.text_input(
        'Nomor WhatsApp (Awali dengan 62, cth: 628123456789)',
        key='reg_wa',
      )
      submit_registration = st.form_submit_button('Ajukan Ke Super Admin')

    if submit_registration:
      clean_user = reg_user.strip()
      clean_pass = reg_pass.strip()
      clean_wa = reg_wa.strip()

      if all((clean_user, clean_pass, clean_wa)):
        normalized_reg_wa = normalize_whatsapp_number(clean_wa)
        registered_numbers = df_users['no_wa'].astype(str).map(normalize_whatsapp_number)
        username_exists = df_users['username'].astype(str).str.strip().str.lower().eq(clean_user.lower()).any()
        number_exists = bool(normalized_reg_wa) and registered_numbers.eq(normalized_reg_wa).any()

        if username_exists:
          st.error('Username sudah digunakan!')
        elif number_exists:
          st.error('Nomor WhatsApp sudah terdaftar. Silakan hubungi admin.')
        else:
          save_user(clean_user, clean_pass, clean_wa, status='pending', role='user')

          admin_result = send_approval_to_admin(clean_user, clean_wa)

          st.success('Pendaftaran Anda telah dikirim ke Super Admin. Mohon menunggu persetujuan.')

          if admin_result.get('status') == 'sent':
            st.success('✅ Notifikasi juga terkirim otomatis ke Super Admin.')
          elif admin_result.get('message', '').startswith('http'):
            st.session_state.whatsapp_popup_url = admin_result['message']
      else:
        st.warning('Harap isi semua kolom pendaftaran terlebih dahulu!')

  if st.session_state.whatsapp_popup_url:
    show_whatsapp_popup(st.session_state.whatsapp_popup_url)
