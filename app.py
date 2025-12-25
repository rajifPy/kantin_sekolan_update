"""
Aplikasi Pengelolaan Stok Kantin Sekolah Menggunakan Barcode
Pemrograman Terstruktur - Python + Streamlit
Version: 1.0.0 - Enhanced

FITUR LENGKAP:
- CRUD Data Produk dengan Barcode
- Scan Barcode (Webcam + Manual Input)
- Dashboard Real-time dengan Grafik
- Laporan Penjualan & Keuntungan
- Backup & Export Data
- Alert Stok Menipis
- Statistics & Analytics
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Import modul custom
from modules.data_handler import *
from modules.chart_handler import *
from modules.utils import *

# Import barcode handler dengan error handling untuk Windows
try:
    from modules.barcode_handler import *
    BARCODE_MODULE_LOADED = True
except Exception as e:
    BARCODE_MODULE_LOADED = False
    print(f"⚠️ Warning: Barcode scanner tidak tersedia - {e}")
    print("💡 Aplikasi tetap bisa digunakan dengan fitur lain")
    
    # Define dummy functions jika module gagal load
    def generate_barcode(barcode_id, product_name):
        """Dummy function - barcode generation disabled"""
        return None
    
    def generate_batch_barcodes(products_df):
        """Dummy function - batch barcode generation disabled"""
        return {
            'success': False,
            'message': 'Fitur generate barcode tidak tersedia. Install ZBar untuk mengaktifkan.'
        }
    
    def scan_barcode_from_camera():
        """Dummy function - camera scanner disabled"""
        return {
            'success': False,
            'message': 'Webcam scanner tidak tersedia. Gunakan Input Manual.'
        }
    
    def check_scanner_availability():
        """Return scanner not available"""
        return {
            'available': False,
            'message': '⚠️ Webcam scanner tidak tersedia - Gunakan input manual'
        }

# Konfigurasi halaman
st.set_page_config(
    page_title="Kantin Sekolah Manager",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom
def load_custom_css():
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            padding: 1rem;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .alert-danger {
            background: #fee;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #f44;
            margin: 1rem 0;
        }
        .alert-success {
            background: #efe;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #4f4;
            margin: 1rem 0;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# Inisialisasi session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'last_scan' not in st.session_state:
        st.session_state.last_scan = None
    if 'show_barcode_info' not in st.session_state:
        st.session_state.show_barcode_info = False

# Login page
def login_page():
    st.markdown("<h1 class='main-header'>🏪 Login Kantin Sekolah</h1>", unsafe_allow_html=True)
    
    # Info tentang aplikasi
    with st.expander("ℹ️ Tentang Aplikasi", expanded=False):
        st.markdown("""
        ### Aplikasi Pengelolaan Stok Kantin Sekolah
        
        **Fitur Utama:**
        - 📦 CRUD Data Produk dengan Barcode
        - 📷 Scan Barcode (Webcam/Manual)
        - 📊 Dashboard Real-time
        - 💰 Laporan Penjualan & Keuntungan
        - 💾 Backup & Export Data
        
        **Teknologi:**
        - Python + Streamlit
        - CSV untuk penyimpanan data
        - Barcode Code128
        - 100% Offline
        
        **Dibuat untuk:**
        - Tugas Pemrograman Terstruktur
        - Solusi digitalisasi kantin sekolah
        """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Silakan Login")
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔐 Login", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login berhasil!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah!")
        
        st.markdown("---")
        st.info("💡 **Demo Login:**\n- Username: `admin`\n- Password: `admin123`")

# Dashboard
def dashboard_page():
    st.markdown("<h1 class='main-header'>📊 Dashboard Kantin Sekolah</h1>", unsafe_allow_html=True)
    
    products_df = load_products_data()
    transactions_df = load_transactions_data()
    stats = calculate_statistics(products_df, transactions_df)
    
    # Metrik Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Produk", stats['total_products'], 
                 delta=None, delta_color="normal")
    with col2:
        st.metric("Total Stok", stats['total_stock'],
                 delta=None, delta_color="normal")
    with col3:
        st.metric("Transaksi Hari Ini", stats['today_transactions'],
                 delta=None, delta_color="normal")
    with col4:
        st.metric("Keuntungan Hari Ini", format_currency(stats['today_profit']),
                 delta=None, delta_color="normal")
    
    st.markdown("---")
    
    # Alert Stok Menipis
    if not products_df.empty:
        low_stock = products_df[products_df['stok'] < 10]
        if not low_stock.empty:
            st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
            st.warning(f"⚠️ **PERINGATAN:** Ada {len(low_stock)} produk dengan stok menipis (< 10)!")
            with st.expander("Lihat Detail Produk Stok Menipis"):
                for idx, row in low_stock.iterrows():
                    st.write(f"- **{row['nama_produk']}**: Stok tersisa {row['stok']}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Grafik
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Stok Produk (Top 10)")
        if not products_df.empty:
            fig = create_stock_chart(products_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data produk")
    
    with col2:
        st.subheader("💰 Keuntungan Harian")
        if not transactions_df.empty:
            fig = create_profit_chart(transactions_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data transaksi")
    
    # Grafik tambahan
    if not transactions_df.empty:
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("📊 Penjualan Harian")
            fig = create_sales_chart(transactions_df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            st.subheader("🏆 Produk Terlaris")
            fig = create_product_sales_chart(transactions_df)
            st.plotly_chart(fig, use_container_width=True)

# Data Master page
def data_master_page():
    st.markdown("<h1 class='main-header'>📦 Data Master Produk</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["➕ Tambah", "📋 Lihat Data", "✏️ Edit", "➕📦 Tambah Stok", "🗑️ Hapus", "🏷️ Generate Barcode"])
    
    # Tab Tambah
    with tab1:
        st.subheader("Tambah Produk Baru")
        with st.form("form_tambah"):
            col1, col2 = st.columns(2)
            with col1:
                barcode_id = st.text_input("Barcode ID *", placeholder="BRK001")
                nama_produk = st.text_input("Nama Produk *", placeholder="Aqua 600ml")
                kategori = st.selectbox("Kategori *", ["Makanan", "Minuman", "Snack", "Alat Tulis", "Lainnya"])
            with col2:
                stok = st.number_input("Stok Awal *", min_value=0, value=0)
                harga_modal = st.number_input("Harga Modal (Rp) *", min_value=0, value=0, step=100)
                harga_jual = st.number_input("Harga Jual (Rp) *", min_value=0, value=0, step=100)
            
            submitted = st.form_submit_button("💾 Simpan Produk", use_container_width=True)
            
            if submitted:
                if validate_not_empty(barcode_id) and validate_not_empty(nama_produk):
                    if harga_jual <= harga_modal:
                        st.error("❌ Harga jual harus lebih besar dari harga modal!")
                    else:
                        result = add_product(barcode_id, nama_produk, kategori, stok, harga_modal, harga_jual)
                        if result['success']:
                            st.success(result['message'])
                            # Generate barcode
                            barcode_path = generate_barcode(barcode_id, nama_produk)
                            if barcode_path:
                                st.success(f"✅ Barcode berhasil di-generate: {barcode_path}")
                                # Tampilkan preview barcode
                                if os.path.exists(barcode_path):
                                    st.image(barcode_path, caption=f"Barcode: {barcode_id}", width=300)
                            st.balloons()
                        else:
                            st.error(result['message'])
                else:
                    st.error("❌ Semua field wajib diisi!")
    
    # Tab Lihat Data
    with tab2:
        st.subheader("Daftar Semua Produk")
        
        # Search
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_keyword = st.text_input("🔍 Cari produk...", placeholder="Nama atau Barcode ID")
        with search_col2:
            kategori_filter = st.selectbox("Filter Kategori", ["Semua", "Makanan", "Minuman", "Snack", "Alat Tulis", "Lainnya"])
        
        df = load_products_data()
        
        if not df.empty:
            # Apply filters
            if search_keyword:
                df = search_product(search_keyword)
            
            if kategori_filter != "Semua":
                df = df[df['kategori'] == kategori_filter]
            
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Produk", len(df))
            with col2:
                st.metric("Total Stok", df['stok'].sum())
            with col3:
                total_value = (df['stok'] * df['harga_modal']).sum()
                st.metric("Nilai Stok", format_currency(total_value))
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Belum ada data produk. Silakan tambah produk baru.")
    
    # Tab Edit
    with tab3:
        st.subheader("Edit Data Produk")
        df = load_products_data()
        
        if not df.empty:
            barcode_list = df['barcode_id'].tolist()
            selected_barcode = st.selectbox("Pilih Produk", barcode_list)
            
            if selected_barcode:
                product = df[df['barcode_id'] == selected_barcode].iloc[0]
                
                with st.form("form_edit"):
                    st.info(f"Edit produk: **{product['nama_produk']}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_nama = st.text_input("Nama Produk", value=product['nama_produk'])
                        new_kategori = st.selectbox("Kategori", 
                                                   ["Makanan", "Minuman", "Snack", "Alat Tulis", "Lainnya"],
                                                   index=["Makanan", "Minuman", "Snack", "Alat Tulis", "Lainnya"].index(product['kategori']))
                    with col2:
                        new_stok = st.number_input("Stok", value=int(product['stok']), min_value=0)
                        new_harga_modal = st.number_input("Harga Modal", value=int(product['harga_modal']), min_value=0)
                    
                    new_harga_jual = st.number_input("Harga Jual", value=int(product['harga_jual']), min_value=0)
                    
                    submitted = st.form_submit_button("💾 Update Produk", use_container_width=True)
                    
                    if submitted:
                        result = update_product(selected_barcode, new_nama, new_kategori, 
                                              new_stok, new_harga_modal, new_harga_jual)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
        else:
            st.warning("⚠️ Belum ada data produk")
    
    # Tab Generate Barcode Batch
    with tab6:
        st.subheader("🏷️ Generate Barcode Secara Batch")
        
        st.info("""
        💡 **Fitur ini untuk:**
        - Generate barcode dari semua produk yang sudah ada di CSV
        - Re-generate barcode yang hilang atau rusak
        - Generate barcode setelah import data produk
        """)
        
        df = load_products_data()
        
        if not df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📊 Status Barcode")
                
                # Check existing barcodes
                total_products = len(df)
                existing_barcodes = 0
                missing_barcodes = []
                
                for idx, row in df.iterrows():
                    barcode_path = f"barcodes/{row['barcode_id']}.png"
                    if os.path.exists(barcode_path):
                        existing_barcodes += 1
                    else:
                        missing_barcodes.append(row['barcode_id'])
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Total Produk", total_products)
                with col_stat2:
                    st.metric("Barcode Sudah Ada", existing_barcodes)
                with col_stat3:
                    st.metric("Barcode Belum Ada", len(missing_barcodes))
                
                if missing_barcodes:
                    with st.expander(f"📋 Lihat {len(missing_barcodes)} Produk Tanpa Barcode"):
                        for barcode_id in missing_barcodes:
                            product = df[df['barcode_id'] == barcode_id].iloc[0]
                            st.write(f"- **{barcode_id}**: {product['nama_produk']}")
            
            with col2:
                st.markdown("### 🎯 Pilihan Generate")
                
                generate_option = st.radio(
                    "Pilih mode generate:",
                    ["Semua Produk", "Hanya yang Belum Ada"]
                )
            
            st.markdown("---")
            
            # Generate buttons
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            
            with col_btn2:
                if generate_option == "Semua Produk":
                    if st.button("🏷️ GENERATE SEMUA BARCODE", use_container_width=True, type="primary"):
                        with st.spinner(f"Generating {total_products} barcode..."):
                            result = generate_batch_barcodes(df)
                            
                            if result['success']:
                                st.success(result['message'])
                                
                                # Show details
                                col_res1, col_res2 = st.columns(2)
                                with col_res1:
                                    st.metric("✅ Berhasil", result['success_count'])
                                with col_res2:
                                    st.metric("❌ Gagal", len(result['failed_items']))
                                
                                if result['failed_items']:
                                    with st.expander("Lihat Item yang Gagal"):
                                        for item in result['failed_items']:
                                            st.write(f"- {item}")
                                
                                st.balloons()
                            else:
                                st.error(result['message'])
                
                else:  # Hanya yang belum ada
                    if len(missing_barcodes) > 0:
                        if st.button(f"🏷️ GENERATE {len(missing_barcodes)} BARCODE", use_container_width=True, type="primary"):
                            with st.spinner(f"Generating {len(missing_barcodes)} barcode..."):
                                # Filter only missing barcodes
                                df_missing = df[df['barcode_id'].isin(missing_barcodes)]
                                result = generate_batch_barcodes(df_missing)
                                
                                if result['success']:
                                    st.success(result['message'])
                                    
                                    col_res1, col_res2 = st.columns(2)
                                    with col_res1:
                                        st.metric("✅ Berhasil", result['success_count'])
                                    with col_res2:
                                        st.metric("❌ Gagal", len(result['failed_items']))
                                    
                                    st.balloons()
                                else:
                                    st.error(result['message'])
                    else:
                        st.success("✅ Semua produk sudah memiliki barcode!")
            
            st.markdown("---")
            
            # Preview barcodes
            st.markdown("### 🖼️ Preview Barcode")
            
            col_prev1, col_prev2 = st.columns([1, 3])
            
            with col_prev1:
                if len(df) > 0:
                    barcode_list = df['barcode_id'].tolist()
                    selected_preview = st.selectbox("Pilih barcode untuk preview:", barcode_list)
            
            with col_prev2:
                if selected_preview:
                    barcode_path = f"barcodes/{selected_preview}.png"
                    if os.path.exists(barcode_path):
                        product = df[df['barcode_id'] == selected_preview].iloc[0]
                        st.image(barcode_path, caption=f"{product['nama_produk']} - {selected_preview}", width=400)
                        
                        # Download button
                        with open(barcode_path, "rb") as file:
                            btn = st.download_button(
                                label="📥 Download Barcode",
                                data=file,
                                file_name=f"{selected_preview}.png",
                                mime="image/png"
                            )
                    else:
                        st.warning(f"⚠️ Barcode untuk {selected_preview} belum di-generate")
            
            # Bulk print option
            st.markdown("---")
            st.markdown("### 🖨️ Cetak Semua Barcode")
            
            col_print1, col_print2, col_print3 = st.columns([1, 2, 1])
            
            with col_print2:
                st.info("""
                💡 **Cara cetak barcode:**
                1. Generate semua barcode
                2. Buka folder `barcodes/`
                3. Pilih barcode yang ingin dicetak
                4. Print menggunakan software printer
                5. Tempelkan pada produk
                """)
                
                if st.button("📂 Buka Folder Barcodes", use_container_width=True):
                    import platform
                    import subprocess
                    
                    barcode_folder = os.path.abspath("barcodes")
                    
                    try:
                        if platform.system() == "Windows":
                            os.startfile(barcode_folder)
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.run(["open", barcode_folder])
                        else:  # Linux
                            subprocess.run(["xdg-open", barcode_folder])
                        
                        st.success(f"✅ Membuka folder: {barcode_folder}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        st.info(f"📁 Lokasi folder: `{barcode_folder}`")
        
        else:
            st.warning("⚠️ Belum ada data produk. Tambah produk terlebih dahulu.")
    
    # Tab Tambah Stok
    with tab4:
        st.subheader("Tambah Stok Produk")
        df = load_products_data()
        
        if not df.empty:
            barcode_list = df['barcode_id'].tolist()
            selected_barcode = st.selectbox("Pilih Produk untuk Tambah Stok", barcode_list, key="add_stock")
            
            if selected_barcode:
                product = df[df['barcode_id'] == selected_barcode].iloc[0]
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.info(f"**Produk:** {product['nama_produk']}\n\n**Stok Saat Ini:** {product['stok']}")
                
                with col2:
                    jumlah_tambah = st.number_input("Jumlah Stok yang Ditambah", min_value=1, value=10)
                    new_total = int(product['stok']) + jumlah_tambah
                    st.success(f"Stok setelah ditambah: **{new_total}**")
                    
                    if st.button("➕ Tambah Stok", use_container_width=True):
                        result = add_stock(selected_barcode, jumlah_tambah)
                        if result['success']:
                            st.success(result['message'])
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(result['message'])
        else:
            st.warning("⚠️ Belum ada data produk")
    
    # Tab Hapus
    with tab5:
        st.subheader("Hapus Produk")
        st.warning("⚠️ **PERHATIAN:** Menghapus produk akan menghapus semua data terkait termasuk barcode!")
        
        df = load_products_data()
        
        if not df.empty:
            barcode_list = df['barcode_id'].tolist()
            selected_barcode = st.selectbox("Pilih Produk yang Akan Dihapus", barcode_list, key="delete")
            
            if selected_barcode:
                product = df[df['barcode_id'] == selected_barcode].iloc[0]
                
                st.error(f"""
                **Produk yang akan dihapus:**
                - Barcode: {product['barcode_id']}
                - Nama: {product['nama_produk']}
                - Kategori: {product['kategori']}
                - Stok: {product['stok']}
                """)
                
                confirm = st.checkbox("Saya yakin ingin menghapus produk ini")
                
                if confirm:
                    if st.button("🗑️ Hapus Produk", use_container_width=True):
                        result = delete_product(selected_barcode)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
        else:
            st.warning("⚠️ Belum ada data produk")

# Scan Barcode page
def scan_page():
    st.markdown("<h1 class='main-header'>📷 Scan Barcode & Transaksi</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📷 Webcam Scanner", "⌨️ Input Manual"])
    
    # Tab Webcam Scanner
    with tab1:
        st.subheader("Scan Barcode via Webcam")
        
        # Check scanner availability
        availability = check_scanner_availability()
        
        if availability['available']:
            st.info("✅ Webcam scanner tersedia")
            
            if st.button("📷 Mulai Scan Barcode", use_container_width=True):
                with st.spinner("Membuka kamera... Arahkan barcode ke kamera"):
                    result = scan_barcode_from_camera()
                    
                    if result['success']:
                        st.session_state.last_scan = result['barcode_id']
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
        else:
            st.warning(availability['message'])
            st.info("💡 Gunakan **Input Manual** sebagai alternatif")
    
    # Tab Input Manual
    with tab2:
        st.subheader("Input Manual Barcode")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            barcode_input = st.text_input("Masukkan Barcode ID", 
                                         placeholder="BRK001",
                                         value=st.session_state.last_scan if st.session_state.last_scan else "")
        with col2:
            st.write("")
            st.write("")
            if st.button("🔍 Cari Produk", use_container_width=True):
                if barcode_input:
                    st.session_state.last_scan = barcode_input
                    st.rerun()
    
    # Jika ada barcode yang di-scan
    if st.session_state.last_scan:
        st.markdown("---")
        st.subheader("Detail Produk")
        
        product = get_product_by_barcode(st.session_state.last_scan)
        
        if product is not None:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                **Barcode ID:** {product['barcode_id']}  
                **Nama Produk:** {product['nama_produk']}  
                **Kategori:** {product['kategori']}  
                **Stok Tersedia:** {product['stok']}
                """)
            
            with col2:
                st.markdown(f"""
                **Harga Modal:** {format_currency(product['harga_modal'])}  
                **Harga Jual:** {format_currency(product['harga_jual'])}  
                **Margin:** {calculate_profit_margin(product['harga_jual'], product['harga_modal']):.1f}%
                """)
            
            with col3:
                # Preview barcode jika ada
                barcode_path = f"barcodes/{product['barcode_id']}.png"
                if os.path.exists(barcode_path):
                    st.image(barcode_path, caption="Barcode", width=150)
            
            # Form Transaksi
            st.markdown("---")
            st.subheader("💸 Proses Transaksi")
            
            col_trans1, col_trans2, col_trans3 = st.columns([1, 1, 1])
            
            with col_trans1:
                max_qty = int(product['stok'])
                if max_qty > 0:
                    jumlah = st.number_input("Jumlah", min_value=1, max_value=max_qty, value=1)
                else:
                    st.error("❌ Stok habis!")
                    jumlah = 0
            
            with col_trans2:
                if jumlah > 0:
                    total_harga = jumlah * product['harga_jual']
                    st.metric("Total Harga", format_currency(total_harga))
            
            with col_trans3:
                if jumlah > 0:
                    total_keuntungan = jumlah * (product['harga_jual'] - product['harga_modal'])
                    st.metric("Keuntungan", format_currency(total_keuntungan))
            
            if jumlah > 0:
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn2:
                    if st.button("💸 PROSES PENJUALAN", use_container_width=True, type="primary"):
                        result = reduce_stock(product['barcode_id'], jumlah, 
                                            product['nama_produk'], product['harga_jual'])
                        if result['success']:
                            st.success(result['message'])
                            st.balloons()
                            st.session_state.last_scan = None
                            st.rerun()
                        else:
                            st.error(result['message'])
        else:
            st.error(f"❌ Produk dengan barcode **{st.session_state.last_scan}** tidak ditemukan!")
            if st.button("🔄 Coba Lagi"):
                st.session_state.last_scan = None
                st.rerun()

# Laporan page
def laporan_page():
    st.markdown("<h1 class='main-header'>📊 Laporan & Statistik</h1>", unsafe_allow_html=True)
    
    transactions_df = load_transactions_data()
    products_df = load_products_data()
    
    if not transactions_df.empty:
        # Filter tanggal
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Dari Tanggal", value=datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("Sampai Tanggal", value=datetime.now())
        with col3:
            st.write("")
            st.write("")
            if st.button("🔍 Filter", use_container_width=True):
                st.rerun()
        
        # Filter data
        transactions_df['tanggal'] = pd.to_datetime(transactions_df['waktu']).dt.date
        mask = (transactions_df['tanggal'] >= start_date) & (transactions_df['tanggal'] <= end_date)
        filtered_df = transactions_df[mask]
        
        if not filtered_df.empty:
            # Summary Statistics
            st.subheader("📈 Ringkasan Periode")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transaksi", len(filtered_df))
            with col2:
                st.metric("Total Pendapatan", format_currency(filtered_df['total_harga'].sum()))
            with col3:
                st.metric("Total Keuntungan", format_currency(filtered_df['keuntungan'].sum()))
            with col4:
                avg_transaction = filtered_df['total_harga'].mean()
                st.metric("Rata-rata Transaksi", format_currency(avg_transaction))
            
            st.markdown("---")
            
            # Grafik
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Penjualan", "💰 Keuntungan", "🏆 Produk Terlaris", "📋 Detail Transaksi"])
            
            with tab1:
                fig = create_sales_chart(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = create_profit_chart(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = create_product_sales_chart(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.dataframe(filtered_df.sort_values('waktu', ascending=False), 
                           use_container_width=True, hide_index=True)
            
            # Export
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("📥 Export ke Excel", use_container_width=True):
                    path = export_to_excel(filtered_df, "laporan_transaksi")
                    if path:
                        st.success(f"✅ Export berhasil: {path}")
        else:
            st.warning("⚠️ Tidak ada transaksi pada periode yang dipilih")
    else:
        st.info("📝 Belum ada transaksi. Lakukan transaksi pertama untuk melihat laporan.")

# Settings page
def settings_page():
    st.markdown("<h1 class='main-header'>⚙️ Pengaturan & Utilitas</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💾 Backup", "📤 Export Data", "ℹ️ Info Aplikasi"])
    
    # Tab Backup
    with tab1:
        st.subheader("Backup & Restore Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Backup Manual")
            if st.button("💾 Backup Sekarang", use_container_width=True):
                result = auto_backup_all()
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])
        
        with col2:
            st.markdown("### Bersihkan Backup Lama")
            days = st.number_input("Hapus backup lebih dari (hari)", min_value=1, value=7)
            if st.button("🧹 Bersihkan", use_container_width=True):
                result = clean_old_backups(days)
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])
        
        # List backup files
        st.markdown("---")
        st.subheader("Daftar Backup")
        backup_folder = "data/backup"
        if os.path.exists(backup_folder):
            files = os.listdir(backup_folder)
            if files:
                for file in sorted(files, reverse=True):
                    file_path = os.path.join(backup_folder, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    st.text(f"📄 {file} - {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.info("Belum ada backup")
        else:
            st.info("Folder backup belum ada")
    
    # Tab Export
    with tab2:
        st.subheader("Export Data ke Excel/CSV")
        
        products_df = load_products_data()
        transactions_df = load_transactions_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Data Produk")
            if not products_df.empty:
                st.write(f"Total: {len(products_df)} produk")
                if st.button("📥 Export Produk (Excel)", use_container_width=True):
                    path = export_to_excel(products_df, "products")
                    if path:
                        st.success(f"✅ Export berhasil: {path}")
        
        with col2:
            st.markdown("### Data Transaksi")
            if not transactions_df.empty:
                st.write(f"Total: {len(transactions_df)} transaksi")
                if st.button("📥 Export Transaksi (Excel)", use_container_width=True):
                    path = export_to_excel(transactions_df, "transactions")
                    if path:
                        st.success(f"✅ Export berhasil: {path}")
    
    # Tab Info
    with tab3:
        st.subheader("Informasi Aplikasi")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📱 Aplikasi
            - **Nama:** Kantin Sekolah Manager
            - **Versi:** 1.0.0 Enhanced
            - **Framework:** Streamlit
            - **Database:** CSV (Offline)
            
            ### 🎯 Fitur Utama
            - ✅ CRUD Data Produk
            - ✅ Generate & Scan Barcode
            - ✅ Dashboard Real-time
            - ✅ Laporan & Statistik
            - ✅ Backup & Export Data
            - ✅ Alert Stok Menipis
            """)
        
        with col2:
            st.markdown("""
            ### 🛠️ Teknologi
            - Python 3.8+
            - Streamlit 1.31
            - Pandas 2.1
            - Plotly 5.18
            - Python-barcode 0.15
            - OpenCV & Pyzbar (optional)
            
            ### 📊 Statistik Aplikasi
            """)
            
            products_df = load_products_data()
            transactions_df = load_transactions_data()
            
            st.metric("Total Produk Terdaftar", len(products_df))
            st.metric("Total Transaksi", len(transactions_df))
            
            if not transactions_df.empty:
                total_revenue = transactions_df['total_harga'].sum()
                st.metric("Total Pendapatan All Time", format_currency(total_revenue))
        
        st.markdown("---")
        
        # System info
        st.subheader("💻 Informasi Sistem")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Python Version:**\n{sys.version.split()[0]}")
        with col2:
            st.info(f"**Streamlit Version:**\n{st.__version__}")
        with col3:
            availability = check_scanner_availability()
            status = "✅ Available" if availability['available'] else "❌ Not Available"
            st.info(f"**Barcode Scanner:**\n{status}")
        
        # Credits
        st.markdown("---")
        st.markdown("""
        ### 👥 Credits
        **Dibuat untuk:**
        - Tugas Pemrograman Terstruktur
        - Solusi digitalisasi kantin sekolah
        
        **Dikembangkan dengan:**
        - ❤️ Python & Streamlit
        - 📚 Paradigma Pemrograman Terstruktur
        - 🎯 100% Offline & CSV-based
        
        ---
        *© 2024 Kantin Sekolah Manager - All Rights Reserved*
        """)

# Main application
def main():
    load_custom_css()
    init_session_state()
    
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Sidebar
    with st.sidebar:
        st.title("🏪 Kantin Manager")
        st.write(f"👤 User: **{st.session_state.username}**")
        
        # Quick stats
        products_df = load_products_data()
        transactions_df = load_transactions_data()
        
        if not products_df.empty:
            st.metric("Produk", len(products_df), delta=None)
            low_stock = len(products_df[products_df['stok'] < 10])
            if low_stock > 0:
                st.warning(f"⚠️ {low_stock} stok menipis")
        
        st.markdown("---")
        
        menu = st.radio(
            "📍 Menu Navigasi",
            [
                "📊 Dashboard", 
                "📦 Data Master", 
                "📷 Scan Barcode", 
                "📊 Laporan", 
                "⚙️ Pengaturan"
            ]
        )
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("💾 Backup Data", use_container_width=True):
            result = auto_backup_all()
            if result['success']:
                st.success("✅ Backup berhasil!")
            else:
                st.error("❌ Backup gagal!")
        
        st.markdown("---")
        
        # Info
        st.info("💡 **Tips:**\nGunakan shortcut keyboard untuk navigasi lebih cepat!")
        
        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.last_scan = None
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption("v1.0.0 Enhanced")
        st.caption("© 2024 Kantin Manager")
    
    # Routing
    if menu == "📊 Dashboard":
        dashboard_page()
    elif menu == "📦 Data Master":
        data_master_page()
    elif menu == "📷 Scan Barcode":
        scan_page()
    elif menu == "📊 Laporan":
        laporan_page()
    elif menu == "⚙️ Pengaturan":
        settings_page()

if __name__ == "__main__":
    import sys
    main()