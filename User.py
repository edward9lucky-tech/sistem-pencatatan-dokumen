import random
import streamlit as st

st.title("Form Pendaftaran & Verifikasi OTP WhatsApp")

# Input data pendaftar
nama = st.text_input("Nama Lengkap")
no_wa = st.text_input(
    "Nomor WhatsApp (Contoh: 628123456789)"
)  # Pastikan formatnya pakai 62 di depan

# Inisialisasi session state untuk OTP agar tidak berubah-ubah saat diklik
if "otp_code" not in st.session_state:
  st.session_state.otp_code = None

if st.button("Kirim Kode OTP"):
  if no_wa:
    # 1. Generate 6 digit angka OTP secara acak
    st.session_state.otp_code = str(random.randint(100000, 999999))

    # 2. Format pesan WhatsApp
    pesan = (
        f"Halo {nama}, berikut adalah kode verifikasi OTP pendaftaran Anda:"
        f" *{st.session_state.otp_code}*. Jangan berikan kode ini ke siapa"
        " pun."
    )

    # 3. Buat URL API WhatsApp otomatis
    # Mengubah teks pesan agar aman dibaca URL (URL encode)
    import urllib.parse

    pesan_encoded = urllib.parse.quote(pesan)
    wa_url = f"https://api.whatsapp.com/send?phone={no_wa}&text={pesan_encoded}"

    st.success("Kode OTP berhasil digenerate!")
    # Menampilkan link tombol agar pendaftar/admin bisa langsung klik untuk mengirim pesan WA
    st.markdown(
        f'<a href="{wa_url}" target="_blank"><button" style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">📲 Klik untuk Kirim OTP via WhatsApp</button></a>',
        unsafe_allow_html=True,
    )
  else:
    st.error("Silakan masukkan nomor WhatsApp terlebih dahulu!")

# Kolom verifikasi kode yang diterima
otp_input = st.text_input("Masukkan Kode OTP yang diterima:")

if st.button("Verifikasi & Simpan Data"):
  if (
      st.session_state.otp_code
      and otp_input == st.session_state.otp_code
  ):
    st.success(
        "Verifikasi Berhasil! Data pendaftar Anda telah disimpan ke sistem."
    )
    # Lanjutkan aksi simpan data ke database / excel di sini
  else:
    st.error("Kode OTP salah atau belum dikirim.")
