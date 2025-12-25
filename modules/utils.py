"""
Module utilitas untuk fungsi-fungsi pembantu
"""

import pandas as pd
import os
from datetime import datetime
import shutil

# ==================== FUNGSI VALIDASI ====================

def validate_number(value):
    """
    Fungsi untuk validasi apakah value adalah angka valid
    
    Args:
        value: Nilai yang akan divalidasi
        
    Returns:
        bool: True jika valid, False jika tidak
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def validate_not_empty(value):
    """
    Fungsi untuk validasi apakah value tidak kosong
    
    Args:
        value: Nilai yang akan divalidasi
        
    Returns:
        bool: True jika tidak kosong, False jika kosong
    """
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    return True

def validate_positive_number(value):
    """
    Fungsi untuk validasi apakah value adalah angka positif
    
    Args:
        value: Nilai yang akan divalidasi
        
    Returns:
        bool: True jika valid, False jika tidak
    """
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_date_format(date_str, format="%Y-%m-%d"):
    """
    Fungsi untuk validasi format tanggal
    
    Args:
        date_str: String tanggal
        format: Format tanggal yang diharapkan
        
    Returns:
        bool: True jika valid, False jika tidak
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

# ==================== FUNGSI FORMATTING ====================

def format_currency(amount):
    """
    Fungsi untuk format angka menjadi format mata uang Rupiah
    
    Args:
        amount: Jumlah uang
        
    Returns:
        str: Format Rupiah
    """
    try:
        return f"Rp {amount:,.0f}".replace(",", ".")
    except:
        return "Rp 0"

def format_date(date_obj, format="%d-%m-%Y"):
    """
    Fungsi untuk format tanggal
    
    Args:
        date_obj: Object datetime
        format: Format output
        
    Returns:
        str: Tanggal terformat
    """
    try:
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime(format)
    except:
        return str(date_obj)

def format_datetime(datetime_str):
    """
    Fungsi untuk format datetime ke format yang lebih readable
    
    Args:
        datetime_str: String datetime
        
    Returns:
        str: Datetime terformat
    """
    try:
        dt = pd.to_datetime(datetime_str)
        return dt.strftime("%d %B %Y, %H:%M")
    except:
        return datetime_str

# ==================== FUNGSI FILE MANAGEMENT ====================

def create_backup(file_path):
    """
    Fungsi untuk membuat backup file
    
    Args:
        file_path: Path file yang akan di-backup
        
    Returns:
        dict: Status dan path backup
    """
    try:
        # Buat folder backup jika belum ada
        backup_folder = "data/backup"
        os.makedirs(backup_folder, exist_ok=True)
        
        # Generate nama file backup dengan timestamp
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{timestamp}_{filename}"
        backup_path = os.path.join(backup_folder, backup_filename)
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        
        return {
            'success': True,
            'backup_path': backup_path,
            'message': f"Backup berhasil: {backup_filename}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Gagal membuat backup: {str(e)}"
        }

def auto_backup_all():
    """
    Fungsi untuk backup semua file data secara otomatis
    
    Returns:
        dict: Status backup
    """
    try:
        results = []
        
        # Backup products
        if os.path.exists("data/products.csv"):
            result = create_backup("data/products.csv")
            results.append(result)
        
        # Backup transactions
        if os.path.exists("data/transactions.csv"):
            result = create_backup("data/transactions.csv")
            results.append(result)
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'success': True,
            'total': len(results),
            'success_count': success_count,
            'message': f"Backup berhasil untuk {success_count} file"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def clean_old_backups(days=7):
    """
    Fungsi untuk menghapus backup lama
    
    Args:
        days: Jumlah hari untuk menyimpan backup
        
    Returns:
        dict: Status pembersihan
    """
    try:
        backup_folder = "data/backup"
        if not os.path.exists(backup_folder):
            return {
                'success': True,
                'message': "Tidak ada folder backup"
            }
        
        deleted_count = 0
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        for filename in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_time < cutoff_date:
                os.remove(file_path)
                deleted_count += 1
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'message': f"Berhasil menghapus {deleted_count} backup lama"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

# ==================== FUNGSI EXPORT ====================

def export_to_excel(df, filename_prefix):
    """
    Fungsi untuk export DataFrame ke Excel
    
    Args:
        df: DataFrame yang akan di-export
        filename_prefix: Prefix nama file
        
    Returns:
        str: Path file Excel atau None jika gagal
    """
    try:
        # Buat folder exports jika belum ada
        os.makedirs("data/exports", exist_ok=True)
        
        # Generate nama file dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        filepath = os.path.join("data/exports", filename)
        
        # Export ke Excel
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        return filepath
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return None

def export_to_csv(df, filename_prefix):
    """
    Fungsi untuk export DataFrame ke CSV
    
    Args:
        df: DataFrame yang akan di-export
        filename_prefix: Prefix nama file
        
    Returns:
        str: Path file CSV atau None jika gagal
    """
    try:
        # Buat folder exports jika belum ada
        os.makedirs("data/exports", exist_ok=True)
        
        # Generate nama file dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join("data/exports", filename)
        
        # Export ke CSV
        df.to_csv(filepath, index=False)
        
        return filepath
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

# ==================== FUNGSI STATISTIK HELPER ====================

def calculate_percentage(part, total):
    """
    Fungsi untuk menghitung persentase
    
    Args:
        part: Bagian
        total: Total
        
    Returns:
        float: Persentase
    """
    try:
        if total == 0:
            return 0
        return (part / total) * 100
    except:
        return 0

def calculate_profit_margin(harga_jual, harga_modal):
    """
    Fungsi untuk menghitung margin keuntungan
    
    Args:
        harga_jual: Harga jual
        harga_modal: Harga modal
        
    Returns:
        float: Margin dalam persen
    """
    try:
        if harga_jual == 0:
            return 0
        keuntungan = harga_jual - harga_modal
        return (keuntungan / harga_jual) * 100
    except:
        return 0

# ==================== FUNGSI DATA CLEANING ====================

def clean_dataframe(df):
    """
    Fungsi untuk membersihkan DataFrame dari nilai null dan duplikat
    
    Args:
        df: DataFrame yang akan dibersihkan
        
    Returns:
        DataFrame: DataFrame yang sudah dibersihkan
    """
    try:
        # Hapus duplikat
        df = df.drop_duplicates()
        
        # Fill NaN dengan 0 untuk kolom numerik
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Fill NaN dengan string kosong untuk kolom string
        string_columns = df.select_dtypes(include=['object']).columns
        df[string_columns] = df[string_columns].fillna('')
        
        return df
        
    except Exception as e:
        print(f"Error cleaning dataframe: {e}")
        return df

def remove_duplicates(df, subset=None):
    """
    Fungsi untuk menghapus duplikat berdasarkan kolom tertentu
    
    Args:
        df: DataFrame
        subset: Kolom yang dijadikan acuan
        
    Returns:
        DataFrame: DataFrame tanpa duplikat
    """
    try:
        if subset:
            return df.drop_duplicates(subset=subset, keep='first')
        else:
            return df.drop_duplicates(keep='first')
    except:
        return df

# ==================== FUNGSI LOGGING ====================

def log_activity(activity_type, description, user="admin"):
    """
    Fungsi untuk mencatat aktivitas sistem
    
    Args:
        activity_type: Tipe aktivitas (CREATE, UPDATE, DELETE, etc)
        description: Deskripsi aktivitas
        user: User yang melakukan aktivitas
        
    Returns:
        bool: True jika berhasil
    """
    try:
        log_file = "data/activity_log.csv"
        
        # Buat log entry
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': user,
            'activity_type': activity_type,
            'description': description
        }
        
        # Load atau buat log file
        if os.path.exists(log_file):
            log_df = pd.read_csv(log_file)
        else:
            log_df = pd.DataFrame(columns=['timestamp', 'user', 'activity_type', 'description'])
        
        # Append log
        log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        
        # Simpan
        log_df.to_csv(log_file, index=False)
        
        return True
        
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False

def get_recent_logs(limit=10):
    """
    Fungsi untuk mengambil log aktivitas terbaru
    
    Args:
        limit: Jumlah log yang akan diambil
        
    Returns:
        DataFrame: Log terbaru
    """
    try:
        log_file = "data/activity_log.csv"
        
        if os.path.exists(log_file):
            log_df = pd.read_csv(log_file)
            return log_df.tail(limit)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error getting logs: {e}")
        return pd.DataFrame()