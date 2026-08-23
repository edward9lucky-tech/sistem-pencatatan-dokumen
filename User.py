import streamlit as st
import pandas as pd
import os
import random
import time
import urllib.parse

# Konfigurasi Halaman Login
st.set_page_config(page_title="Login - Aplikasi Administrasi", layout="centered")

file_users = "users.xlsx"
NOMOR_SUPER_ADMIN = "6285156009275"

# --- INISIALISASI SUPER ADMIN ---
df_super_admin = pd.DataFrame([{
    "Username": "edward",
    "Password": "090990",
    "No_WA": f"+{NOMOR_SUPER_ADMIN}",
    "Status": "Aktif"
}])

if not os.path.exists(file_users):
    df_super_admin.to_excel(file_users, index=False)
else:
    try:
        df_u = pd.read_excel(file_users, dtype=str)
        df_u["Username"] = df_u["Username"].astype(str).str.strip().str.lower()
        if "edward" not in df_u["Username"].values:
            df_u = pd.concat([df_u, df_super_admin], ignore_index=True)
            df_u.to_excel(file_users, index=False)
    except Exception:
        df_super_admin.to_excel(file_users, index=False)

# --- INISIALISASI SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "otp_terkirim" not in st.session_state:
    st.session_state.otp_terkirim = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = ""
if "temp_user" not in st.session_state:
    st.session_state.temp_user = ""
if "temp_pass" not in st.session_state:
    st.session_state.temp_pass = ""
if "temp_wa" not in st.session_state:
    st.session_state.temp_wa = ""

# --- JIKA SUDAH LOGIN, LANGSUNG MASUK KE SYSTEM (PAGES/NEW.PY) ---
if st.session_state.logged_in:
    st.switch_page("pages/New.py")

@st.dialog("🔐 Verifikasi OTP Pendaftaran Akun")
def modal_verifikasi_otp():
    st.info("Permohonan akun baru berhasil dicatat dalam sistem.")
    st.write("Silakan masukkan 6 digit kode OTP yang dikirim oleh super admin:")
    
    pesan_wa = (
        f"Halo Super Admin (Edward),\n\n"
        f"Ada pendaftaran akun baru:\n"
        f"Username: {st.session_state.temp_user}\n"
        f"No WA: {st.session_state.temp_wa}\n"
        f"Kode OTP: *{st.session_state.generated_otp}*"
    )
    url_wa = f"https://wa.me/{NOMOR_SUPER_ADMIN}?text={urllib.parse.quote(pesan_wa)}"
    
    st.markdown(f"""
        <a href="{url_wa}" target="_blank">
            <button style="background-color:#25D366; color:white; padding:10px 15px; border:none; border-radius:6px; cursor:pointer; font-weight:bold; width:100%; margin-bottom:15px; font-size:14px;">
                📲 Klik di Sini untuk Kirim Pesan ke WhatsApp Super Admin
            </button>
        </a>
    """, unsafe_allow_html=True)
    
    input_otp = st.text_input("Masukkan 6 Digit Kode OTP", key="otp_in_modal")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Verifikasi & Aktifkan", key="btn_verif_modal"):
            if input_otp.strip() == st.session_state.generated_otp:
                df_u = pd.read_excel(file_users, dtype=str)
                new_user = pd.DataFrame([{
                    "Username": st.session_state.temp_user,
                    "Password": st.session_state.temp_pass,
                    "No_WA": st.session_state.temp_wa,
                    "Status": "Aktif"
                }])
                df_u = pd.concat([df_u, new_user], ignore_index=True)
                df_u.to_excel(file_users, index=False)
                
                st.success("✅ Akun berhasil diverifikasi! Masuk ke sistem...")
                st.session_state.logged_in = True
                st.session_state.username = st.session_state.temp_user.strip().lower()
                st.session_state.otp_terkirim = False
                
                time.sleep(1) 
                st.switch_page("pages/New.py")
            else:
                st.error("❌ Kode OTP salah.")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button("Batal", key="btn_batal_modal"):
            st.session_state.otp_terkirim = False
            st.rerun()

# --- TAMPILAN UTAMA LOGIN & REGISTER ---
st.title("🔐 Silakan Masuk atau Daftar Akun")
menu = st.tabs(["Masuk (Login)", "Daftar (Register)"])

with menu[0]:
    st.subheader("Form Masuk")
    login_user = st.text_input("Username", key="input_user_login")
    login_pass = st.text_input("Password", type="password", key="input_pass_login")
    
    if st.button("Tombol Masuk", key="btn_login_eksekusi"):
        if login_user and login_pass:
            df_u = pd.read_excel(file_users, dtype=str)
            df_u["Username_Clean"] = df_u["Username"].astype(str).str.strip().str.lower()
            df_u["Password_Clean"] = df_u["Password"].astype(str).str.strip()
            
            input_u_clean = login_user.strip().lower()
            input_p_clean = login_pass.strip()
            
            user_match = df_u[(df_u["Username_Clean"] == input_u_clean) & (df_u["Password_Clean"] == input_p_clean)]
            
            if not user_match.empty:
                status = str(user_match.iloc[0]["Status"]).strip()
                if status == "Aktif":
                    st.session_state.logged_in = True
                    st.session_state.username = input_u_clean
                    st.success("Berhasil masuk! Membuka sistem...")
                    time.sleep(1)
                    st.switch_page("pages/New.py")
                else:
                    st.error("Akun Anda belum diverifikasi dengan OTP.")
            else:
                st.error("Username atau Password salah.")
        else:
            st.warning("Mohon isi username dan password.")

with menu[1]:
    st.subheader("Buat Akun Baru")
    reg_user = st.text_input("Buat Username Baru", key="reg_u")
    reg_pass = st.text_input("Buat Password Baru", type="password", key="reg_p")
    reg_wa = st.text_input("Nomor WhatsApp Pendaftar (Contoh: 0851XXXXXXXX)", key="reg_w")
    
    if st.button("Kirim Permohonan & Buat OTP", key="btn_reg"):
        if reg_user and reg_pass and reg_wa:
            df_u = pd.read_excel(file_users, dtype=str)
            existing_users = df_u["Username"].astype(str).str.strip().str.lower().values
            
            if reg_user.strip().lower() in existing_users:
                st.warning("Username sudah terpakai.")
            else:
                kode_otp = str(random.randint(100000, 999999))
                st.session_state.generated_otp = kode_otp
                st.session_state.temp_user = reg_user.strip()
                st.session_state.temp_pass = reg_pass.strip()
                st.session_state.temp_wa = reg_wa.strip()
                st.session_state.otp_terkirim = True
                st.rerun()
        else:
            st.warning("Mohon lengkapi semua data pendaftaran.")

if st.session_state.otp_terkirim:
    modal_verifikasi_otp()
