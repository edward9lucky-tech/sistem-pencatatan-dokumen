import os
import random
import urllib.parse
import pandas as pd
import streamlit as st

# File database excel lokal
USER_FILE = 'users.xlsx'


# Fungsi load user dengan proteksi otomatis jika format kolom beda/kosong
def load_users():
  if not os.path.exists(USER_FILE):
    df_init = pd.DataFrame(
        {
            'username': ['edward'],
            'password': ['admin123'],
            'no_wa': ['628123456789'],
        }
    )
    df_init.to_excel(USER_FILE, index=False)
    return df_init

  try:
    df = pd.read_excel(USER_FILE, dtype=str)
    # Cek apakah kolom yang dibutuhkan lengkap
    required_cols = ['username', 'password', 'no_wa']
    if not all(col in df.columns for col in required_cols):
      # Jika tidak lengkap, buat ulang file default-nya
      df_init = pd.DataFrame(
          {
              'username': ['edward'],
              'password': ['admin123'],
              'no_wa': ['628123456789'],
          }
      )
      df_init.to_excel(USER_FILE, index=False)
      return df_init
    return df
  except Exception:
    df_init = pd.DataFrame(
        {
            'username': ['edward'],
            'password': ['admin123'],
            'no_wa': ['628123456789'],
        }
    )
    df_init.to_excel(USER_FILE, index=False)
    return df_init


def save_user(username, password, no_wa):
  df = load_users()
  new_row = pd.DataFrame(
      {'username': [username], 'password': [password], 'no_wa': [no_wa]}
  )
  df = pd.concat([df, new_row], ignore_index=True)
  df.to_excel(USER_FILE, index=False)


# Session state untuk status login
if 'logged_in' not in st.session_state:
  st.session_state.logged_in = False
if 'username' not in st.session_state:
  st.session_state.username = ''
if 'otp_code' not in st.session_state:
  st.session_state.otp_code = None
if 'temp_reg' not in st.session_state:
  st.session_state.temp_reg = {}

# --- HALAMAN JIKA SUDAH LOGIN ---
if st.session_state.logged_in:
  st.success(f'Selamat datang, {st.session_state.username}!')

  # Menu navigasi halaman utama
  st.page_link('pages/New.py', label='📂 Buka Menu Pencatatan & Dokumen')

  if st.button('Logout'):
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.rerun()

# --- HALAMAN LOGIN & REGISTRASI ---
else:
  st.title('Sistem Arsip & Dokumen')
  menu = st.selectbox('Pilih Menu', ['Login', 'Register / Daftar Akun'])

  df_users = load_users()

  if menu == 'Login':
    st.subheader('Silakan Login')
    username_input = st.text_input('Username')
    password_input = st.text_input('Password', type='password')

    if st.button('Login'):
      user_row = df_users[df_users['username'] == username_input]
      if (
          not user_row.empty
          and str(user_row.iloc[0]['password']).strip() == str(password_input).strip()
      ):
        st.session_state.logged_in = True
        st.session_state.username = username_input
        st.success('Login Berhasil!')
        st.rerun()
      else:
        st.error('Username atau Password salah!')

  elif menu == 'Register / Daftar Akun':
    st.subheader('Daftar Akun Baru dengan Verifikasi WhatsApp')

    reg_user = st.text_input('Buat Username Baru')
    reg_pass = st.text_input('Buat Password Baru', type='password')
    reg_wa = st.text_input(
        'Nomor WhatsApp (Awali dengan 62, cth: 628123456789)'
    )

    # Langkah 1: Kirim OTP
    if st.button('Kirim Kode OTP ke WhatsApp'):
      if reg_user and reg_pass and reg_wa:
        if reg_user in df_users['username'].values:
          st.error('Username sudah digunakan!')
        else:
          # Generate OTP 6 digit
          st.session_state.otp_code = str(random.randint(100000, 999999))
          st.session_state.temp_reg = {
              'username': reg_user,
              'password': reg_pass,
              'no_wa': reg_wa,
          }

          # Pesan WA
          pesan = (
              f'Halo {reg_user}, kode verifikasi OTP pendaftaran sistem Anda'
              f' adalah: *{st.session_state.otp_code}*. Jangan berikan ke'
              ' siapa pun.'
          )
          pesan_encoded = urllib.parse.quote(pesan)
          wa_url = f'https://api.whatsapp.com/send?phone={reg_wa}&text={pesan_encoded}'

          st.success('Kode OTP berhasil dibuat!')
          st.markdown(
              f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">📲 Klik Disini untuk Kirim WA ke HP Anda</button></a>',
              unsafe_allow_html=True,
          )
      else:
        st.warning('Harap isi semua kolom pendaftaran terlebih dahulu!')

    # Langkah 2: Masukkan OTP dan Simpan
    st.write('---')
    otp_input = st.text_input('Masukkan 6 Digit Kode OTP yang Diterima di WA')

    if st.button('Verifikasi & Selesaikan Pendaftaran'):
      if (
          st.session_state.otp_code
          and otp_input == st.session_state.otp_code
      ):
        # Simpan ke Excel/database lokal
        data = st.session_state.temp_reg
        save_user(data['username'], data['password'], data['no_wa'])
        st.success(
            'Registrasi Berhasil! Silakan pindah ke menu Login untuk masuk.'
        )
        st.session_state.otp_code = None
      else:
        st.error('Kode OTP salah atau belum dikirim.')
