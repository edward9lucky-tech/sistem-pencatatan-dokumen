import streamlit as st
import pandas as pd
import os
import time

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Sistem Pencatatan Dokumen & Inventaris", layout="wide")

file_data = "data_penyimpanan.xlsx"
FOLDER_UPLOAD = "uploads"
USER_FILE = "users.xlsx"

# --- KEAMANAN: CEK APAKAH SUDAH LOGIN ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Anda belum login! Silakan login terlebih dahulu.")
    time.sleep(1)
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
if "admin_edit_index" not in st.session_state:
    st.session_state.admin_edit_index = None
if "document_form_version" not in st.session_state:
    st.session_state.document_form_version = 0

# Load user metadata
if os.path.exists(USER_FILE):
    df_users = pd.read_excel(USER_FILE, dtype=str)
    for column, default in [('username', ''), ('password', ''), ('no_wa', ''), ('role', 'user'), ('status', 'approved')]:
        if column not in df_users.columns:
            df_users[column] = default
        df_users[column] = df_users[column].fillna(default).astype(str).str.strip()
else:
    df_users = pd.DataFrame(columns=['username', 'password', 'no_wa', 'role', 'status'])

current_user = df_users[df_users['username'].astype(str).str.strip().str.lower() == st.session_state.get('username', '').lower()]
current_role = current_user.iloc[0]['role'] if not current_user.empty else 'user'


def render_saved_data():
    st.subheader("📋 Daftar Data Tersimpan & Aksi")

    if not os.path.exists(file_data):
        st.info("Belum ada data tersimpan.")
        return

    df_tampil = pd.read_excel(file_data, dtype=str)
    if df_tampil.empty:
        st.info("Belum ada data tersimpan.")
        return

    table_columns = st.columns([1.4, 2.7, 3, 2, 1.8, 1.5, 3.2])
    table_headers = [
        "Nomor Dokumen", "Perihal", "Keterangan", "Oleh",
        "Tanggal", "Foto_Berkas",
    ]
    for header_column, header in zip(table_columns, table_headers):
        header_column.markdown(f"**{header}**")
    table_columns[6].markdown("<div style='text-align:center'><strong>Action</strong></div>", unsafe_allow_html=True)
    st.divider()

    for i, row in df_tampil.iterrows():
        document_columns = st.columns([1.4, 2.7, 3, 2, 1.8, 1.5, 3.2])
        document_columns[0].write(str(row.get('Nomor Dokumen', '')))
        document_columns[1].write(str(row.get('Perihal', '')))
        document_columns[2].write(str(row.get('Keterangan', '')))
        document_columns[3].write(str(row.get('Oleh', '')))
        document_columns[4].write(str(row.get('Tanggal', '')))
        foto_path = str(row.get("Foto_Berkas", ''))
        document_columns[5].write(foto_path if foto_path not in ('', 'nan', 'None') else '-')

        action_columns = document_columns[6].columns(3)
        with action_columns[0]:
            if foto_path and foto_path not in ('nan', 'None') and os.path.exists(foto_path):
                if st.button("Lihat", key=f"view_{i}", help="Lihat Foto Berkas"):
                    st.image(foto_path, caption=f"Berkas Dokumen: {row['Nomor Dokumen']}")
            else:
                st.write('-')
        with action_columns[1]:
            if st.button("Edit", key=f"edit_{i}", help="Edit Data"):
                st.session_state.edit_index = i
                st.session_state.next_user_menu = "Tambah Data Baru"
                st.rerun()
        with action_columns[2]:
            if st.button("Hapus", key=f"del_{i}", help="Hapus Data"):
                df_tampil = df_tampil.drop(i).reset_index(drop=True)
                df_tampil.to_excel(file_data, index=False)
                st.success("Data berhasil dihapus!")
                time.sleep(1)
                st.rerun()
        st.divider()

# Sidebar Navigasi / Info Pengguna
st.sidebar.title(f"Halo, {st.session_state.get('username', 'User')}!")
if current_role.lower() == 'superadmin':
    st.sidebar.caption("🛡️ Super Admin")
if st.sidebar.button("🚪 Keluar (Logout)"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.edit_index = None
    time.sleep(1)
    st.switch_page("User.py")

st.sidebar.markdown("---")
st.sidebar.info("Sistem Pencatatan Dokumen & Inventaris aktif.")

if current_role.lower() != 'superadmin':
    if 'next_user_menu' in st.session_state:
        st.session_state.user_menu = st.session_state.pop('next_user_menu')
    user_menu = st.sidebar.radio(
        "Menu User",
        ["Tambah Data Baru", "Daftar Data Tersimpan & Aksi"],
        key="user_menu",
    )
else:
    user_menu = "Tambah Data Baru"

if current_role.lower() == 'superadmin':
    st.title("🛡️ Panel Super Admin")
    admin_menu = st.sidebar.radio(
        "Menu Super Admin",
        ["Persetujuan & User", "Data Dokumen"],
    )

    if admin_menu == "Data Dokumen":
        st.subheader("Data yang Diinput User")
        df_admin_data = pd.read_excel(file_data, dtype=str)

        if df_admin_data.empty:
            st.info("Belum ada data dokumen yang diinput user.")
        else:
            table_columns = st.columns([1.4, 2.7, 3, 2, 1.8, 1.8, 2.6])
            table_headers = [
                "Nomor Dokumen", "Perihal", "Keterangan", "Oleh",
                "Tanggal", "Foto_Berkas",
            ]
            for header_column, header in zip(table_columns, table_headers):
                header_column.markdown(f"**{header}**")
            table_columns[6].markdown("<div style='text-align:center'><strong>Action</strong></div>", unsafe_allow_html=True)
            st.divider()

            for data_idx, data_row in df_admin_data.iterrows():
                if st.session_state.admin_edit_index == data_idx:
                    with st.form(f"admin_edit_data_{data_idx}"):
                        edited_date = st.text_input("Tanggal", value=str(data_row.get('Tanggal', '')))
                        edited_number = st.text_input("Nomor/Kode Dokumen", value=str(data_row.get('Nomor Dokumen', '')))
                        edited_subject = st.text_input("Perihal / Nama Barang", value=str(data_row.get('Perihal', '')))
                        edited_description = st.text_area("Keterangan", value=str(data_row.get('Keterangan', '')))
                        save_document = st.form_submit_button("Simpan perubahan", type="primary")

                    if save_document:
                        if not edited_number.strip() or not edited_subject.strip():
                            st.error("Nomor Dokumen dan Perihal wajib diisi.")
                        else:
                            df_admin_data.loc[data_idx, 'Tanggal'] = edited_date.strip()
                            df_admin_data.loc[data_idx, 'Nomor Dokumen'] = edited_number.strip()
                            df_admin_data.loc[data_idx, 'Perihal'] = edited_subject.strip()
                            df_admin_data.loc[data_idx, 'Keterangan'] = edited_description.strip()
                            df_admin_data.to_excel(file_data, index=False)
                            st.session_state.admin_edit_index = None
                            st.success("Data dokumen berhasil diperbarui.")
                            time.sleep(0.5)
                            st.rerun()

                    if st.button("Batal edit", key=f"cancel_admin_edit_{data_idx}"):
                        st.session_state.admin_edit_index = None
                        st.rerun()
                else:
                    document_columns = st.columns([1.4, 2.7, 3, 2, 1.8, 1.8, 2.6])
                    document_columns[0].write(str(data_row.get('Nomor Dokumen', '')))
                    document_columns[1].write(str(data_row.get('Perihal', '')))
                    document_columns[2].write(str(data_row.get('Keterangan', '')))
                    document_columns[3].write(str(data_row.get('Oleh', '')))
                    document_columns[4].write(str(data_row.get('Tanggal', '')))
                    document_columns[5].write(str(data_row.get('Foto_Berkas', '')))
                    action_columns = document_columns[6].columns(2)
                    with action_columns[0]:
                        if st.button("Edit", key=f"admin_edit_{data_idx}"):
                            st.session_state.admin_edit_index = data_idx
                            st.rerun()
                    with action_columns[1]:
                        if st.button("Hapus", key=f"admin_delete_{data_idx}"):
                            df_admin_data = df_admin_data.drop(index=data_idx).reset_index(drop=True)
                            df_admin_data.to_excel(file_data, index=False)
                            st.success("Data dokumen berhasil dihapus.")
                            time.sleep(0.5)
                            st.rerun()
                st.divider()

        st.stop()

    st.subheader("Persetujuan user baru")

    pending_users = df_users[(df_users['status'].astype(str).str.lower() == 'pending') | (df_users['status'].astype(str).str.lower() == 'waiting')]
    if pending_users.empty:
        st.info("Tidak ada user yang menunggu persetujuan saat ini.")
    else:
        for idx, row in pending_users.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{row['username']}** | WA: {row['no_wa']}")
            with col2:
                if st.button("Accept", key=f"accept_{idx}"):
                    df_users.loc[idx, 'status'] = 'approved'
                    df_users.to_excel(USER_FILE, index=False)
                    st.success(f"User {row['username']} diterima.")
                    time.sleep(0.5)
                    st.rerun()
            with col3:
                if st.button("Reject", key=f"reject_{idx}"):
                    df_users = df_users.drop(idx)
                    df_users.to_excel(USER_FILE, index=False)
                    st.warning(f"User {row['username']} ditolak.")
                    time.sleep(0.5)
                    st.rerun()

    st.subheader("Daftar semua user")
    if df_users.empty:
        st.info("Belum ada user yang terdaftar.")
    else:
        user_table_columns = st.columns([2, 3, 1.5, 1.5, 2.6])
        user_headers = ["Username", "Nomor WhatsApp", "Status", "Privilage", "Action"]
        for header_column, header in zip(user_table_columns, user_headers):
            if header == "Action":
                header_column.markdown("<div style='text-align:center'><strong>Action</strong></div>", unsafe_allow_html=True)
            else:
                header_column.markdown(f"**{header}**")
        st.divider()

        for idx, row in df_users.iterrows():
            username = str(row['username']).strip()
            is_current_user = username.lower() == st.session_state.get('username', '').strip().lower()
            if st.session_state.get(f'editing_user_{idx}', False):
                with st.form(f"edit_user_{idx}"):
                    edited_username = st.text_input("Username", value=username)
                    edited_wa = st.text_input("Nomor WhatsApp", value=str(row['no_wa']))
                    edited_password = st.text_input(
                        "Password baru (kosongkan jika tidak diubah)",
                        type="password",
                    )
                    edited_status = st.selectbox(
                        "Status",
                        ['approved', 'pending', 'rejected'],
                        index=['approved', 'pending', 'rejected'].index(str(row['status']).lower())
                        if str(row['status']).lower() in ['approved', 'pending', 'rejected'] else 0,
                    )
                    role_options = ['user', 'superadmin']
                    edited_role = st.selectbox(
                        "Privilage",
                        role_options,
                        index=role_options.index(str(row['role']).lower())
                        if str(row['role']).lower() in role_options else 0,
                    )
                    save_user_changes = st.form_submit_button("Simpan perubahan", type="primary")

                if save_user_changes:
                    clean_username = edited_username.strip()
                    duplicate_username = df_users[
                        (df_users.index != idx)
                        & (df_users['username'].str.lower() == clean_username.lower())
                    ]
                    if not clean_username:
                        st.error("Username tidak boleh kosong.")
                    elif not duplicate_username.empty:
                        st.error("Username tersebut sudah digunakan user lain.")
                    elif is_current_user and edited_role != 'superadmin':
                        st.error("Privilage akun Super Admin yang sedang digunakan tidak boleh diturunkan.")
                    elif is_current_user and edited_status != 'approved':
                        st.error("Status akun Super Admin yang sedang digunakan harus tetap approved.")
                    else:
                        df_users.loc[idx, 'username'] = clean_username
                        df_users.loc[idx, 'no_wa'] = edited_wa.strip()
                        df_users.loc[idx, 'status'] = edited_status
                        df_users.loc[idx, 'role'] = edited_role
                        if edited_password.strip():
                            df_users.loc[idx, 'password'] = edited_password.strip()
                        if is_current_user:
                            st.session_state.username = clean_username
                        df_users.to_excel(USER_FILE, index=False)
                        st.success(f"Data user {clean_username} berhasil diperbarui.")
                        time.sleep(0.5)
                        st.rerun()

                if is_current_user:
                    st.caption("Akun Super Admin yang sedang digunakan tidak dapat dihapus.")
                if st.button("Batal edit", key=f"cancel_user_edit_{idx}"):
                    st.session_state[f'editing_user_{idx}'] = False
                    st.rerun()
            else:
                user_columns = st.columns([2, 3, 1.5, 1.5, 2.6])
                user_columns[0].write(username)
                user_columns[1].write(str(row['no_wa']))
                user_columns[2].write(str(row['status']))
                user_columns[3].write(str(row['role']))
                user_actions = user_columns[4].columns(2)
                with user_actions[0]:
                    if st.button("Edit", key=f"edit_user_button_{idx}"):
                        st.session_state[f'editing_user_{idx}'] = True
                        st.rerun()
                with user_actions[1]:
                    if is_current_user:
                        st.caption("Aktif")
                    elif st.button("Hapus", key=f"delete_user_{idx}", type="secondary"):
                        df_users = df_users.drop(index=idx).reset_index(drop=True)
                        df_users.to_excel(USER_FILE, index=False)
                        st.success(f"User {username} berhasil dihapus.")
                        time.sleep(0.5)
                        st.rerun()
            st.divider()

    st.stop()

st.title("📁 Sistem Pencatatan Dokumen & Inventaris")
st.write("Kelola data dokumen, inventaris, dan unggah foto berkas dengan mudah.")

if current_role.lower() != 'superadmin' and user_menu == "Daftar Data Tersimpan & Aksi":
    render_saved_data()
    st.stop()

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

document_form_version = st.session_state.document_form_version
no_dokumen = st.text_input(
    "Nomor/Kode Dokumen",
    value=default_no,
    key=f"document_number_{document_form_version}",
)
perihal = st.text_input(
    "Perihal / Nama Barang",
    value=default_perihal,
    key=f"document_subject_{document_form_version}",
)
keterangan = st.text_area(
    "Keterangan Tambahan",
    value=default_ket,
    key=f"document_description_{document_form_version}",
)

foto_berkas = st.file_uploader(
    "Upload Foto Berkas / Ambil Foto via HP",
    type=["jpg", "jpeg", "png"],
    key=f"document_photo_{document_form_version}",
)

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
                st.session_state.document_form_version += 1
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
            st.session_state.next_user_menu = "Daftar Data Tersimpan & Aksi"
            time.sleep(1)
            st.rerun()

with col_btn2:
    if is_editing:
        if st.button("Batal Edit"):
            st.session_state.edit_index = None
            st.session_state.next_user_menu = "Daftar Data Tersimpan & Aksi"
            st.rerun()

