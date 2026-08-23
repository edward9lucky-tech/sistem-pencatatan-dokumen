import streamlit as st
import pandas as pd
import os
import time

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Sistem Pencatatan Dokumen & Inventaris", layout="wide")

file_data = "data_penyimpanan.xlsx"
FOLDER_UPLOAD = "uploads"

# --- KEAMANAN: CEK APAKAH SUDAH LOGIN ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Anda belum login! Silakan login terlebih dahulu.")
    time.sleep(1.5)
    st.switch_page("User.py")

if not os.path.exists(FOLDER_UPLOAD):
    os.makedirs(FOLDER_UPLOAD)

if not os.path.exists(file_data):
    df_init_data = pd.DataFrame(columns=["Tanggal", "Nomor Dokumen", "Perihal", "Keterangan", "Oleh", "Foto_Berkas"])
    df_init_data.to_excel(file_data, index=False)
else:
    df_check = pd.read_excel(file_data, dtype=str)
    if "Foto_Berkas" not in df_check.columns:
        df_check["Foto_Berkas"] = ""
        df_check.to_excel(file_data, index=False)

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Sidebar Navigasi / Info Pengguna
st.sidebar.title(f"Halo, {st.session_state.get('username', 'User')}!")
if st.sidebar.button("🚪 Keluar (Logout)"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.edit_index = None
    st.switch_page("User.py")

st.sidebar.markdown("---")
st.sidebar.info("Sistem Pencatatan Dokumen & Inventaris aktif.")

st.title("📁 Sistem Pencatatan Dokumen & Inventaris")
st.write("Kelola data dokumen, inventaris, dan unggah foto berkas dengan mudah.")

# --- FORM TAMBAH / EDIT DATA ---
is_editing = st.session_state.edit_index is not None

if is_editing:
    st.subheader(f"✏️ Edit Data (Baris ke-{st.session_state.edit_index})")
    df_load = pd.read_excel(file_data, dtype=str)
    row_edit = df_load.iloc[int(st.session_state.edit_index)]
    
    default_no = row_edit["Nomor Dokumen"]
    default_perihal = row_edit["Perihal"]
    default_ket = row_edit["Keterangan"]
    default_foto = row_edit["Foto_Berkas"]
else:
    st.subheader("➕ Tambah Data Baru")
    default_no = ""
    default_perihal = ""
    default_ket = ""
    default_foto = ""

no_dokumen = st.text_input("Nomor/Kode Dokumen", value=default_no)
perihal = st.text_input("Perihal / Nama Barang", value=default_perihal)
keterangan = st.text_area("Keterangan Tambahan", value=default_ket)

foto_berkas = st.file_uploader("Upload Foto Berkas / Ambil Foto via HP", type=["jpg", "jpeg", "png"])

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if not is_editing:
        if st.button("Simpan ke Database", type="primary"):
            if no_dokumen and perihal:
                file_path_saved = ""
                if foto_berkas is not None:
                    file_name = f"{int(time.time())}_{foto_berkas.name}"
                    file_path_saved = os.path.join(FOLDER_UPLOAD, file_name)
                    with open(file_path_saved, "wb") as f:
                        f.write(foto_berkas.getbuffer())
                
                df_existing = pd.read_excel(file_data, dtype=str)
                data_baru = pd.DataFrame([{
                    "Tanggal": str(pd.Timestamp.now().date()),
                    "Nomor Dokumen": no_dokumen,
                    "Perihal": perihal,
                    "Keterangan": keterangan,
                    "Oleh": st.session_state.username,
                    "Foto_Berkas": file_path_saved
                }])
                
                df_updated = pd.concat([df_existing, data_baru], ignore_index=True)
                df_updated.to_excel(file_data, index=False)
                st.success("✅ Data berhasil disimpan!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Mohon isi Nomor Dokumen dan Perihal.")
    else:
        if st.button("Perbarui Data (Update)", type="primary"):
            df_existing = pd.read_excel(file_data, dtype=str)
            idx = int(st.session_state.edit_index)
            
            file_path_saved = default_foto
            if foto_berkas is not None:
                file_name = f"{int(time.time())}_{foto_berkas.name}"
                file_path_saved = os.path.join(FOLDER_UPLOAD, file_name)
                with open(file_path_saved, "wb") as f:
                    f.write(foto_berkas.getbuffer())
            
            df_existing.loc[idx, "Nomor Dokumen"] = no_dokumen
            df_existing.loc[idx, "Perihal"] = perihal
            df_existing.loc[idx, "Keterangan"] = keterangan
            df_existing.loc[idx, "Foto_Berkas"] = file_path_saved
            
            df_existing.to_excel(file_data, index=False)
            st.success("✅ Data berhasil diperbarui!")
            st.session_state.edit_index = None
            time.sleep(1)
            st.rerun()
            
with col_btn2:
    if is_editing:
        if st.button("Batal Edit"):
            st.session_state.edit_index = None
            st.rerun()

st.markdown("---")
st.subheader("📋 Daftar Data Tersimpan & Aksi")

if os.path.exists(file_data):
    df_tampil = pd.read_excel(file_data, dtype=str)
    
    if df_tampil.empty:
        st.info("Belum ada data tersimpan.")
    else:
        for i, row in df_tampil.iterrows():
            with st.container():
                col_info, col_action = st.columns([4, 2])
                with col_info:
                    st.markdown(f"**No. Dokumen:** {row['Nomor Dokumen']} | **Perihal:** {row['Perihal']}")
                    st.caption(f"Tanggal: {row['Tanggal']} | Oleh: {row['Oleh']} | Ket: {row['Keterangan']}")
                with col_action:
                    sub_c1, sub_c2, sub_c3 = st.columns(3)
                    
                    # Ikon Tanda Mata (Lihat Foto)
                    with sub_c1:
                        foto_path = str(row["Foto_Berkas"])
                        if foto_path and os.path.exists(foto_path):
                            if st.button("👁️", key=f"view_{i}", help="Lihat Foto Berkas"):
                                st.image(foto_path, caption=f"Berkas Dokumen: {row['Nomor Dokumen']}")
                        else:
                            st.markdown("❌")
                            
                    # Tombol Edit
                    with sub_c2:
                        if st.button("✏️", key=f"edit_{i}", help="Edit Data"):
                            st.session_state.edit_index = i
                            st.rerun()
                            
                    # Tombol Delete
                    with sub_c3:
                        if st.button("🗑️", key=f"del_{i}", help="Hapus Data"):
                            df_tampil = df_tampil.drop(i).reset_index(drop=True)
                            df_tampil.to_excel(file_data, index=False)
                            st.success("Data berhasil dihapus!")
                            time.sleep(1)
                            st.rerun()
                st.divider()
