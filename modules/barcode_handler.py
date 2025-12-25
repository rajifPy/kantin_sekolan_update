"""
Module untuk menangani generate dan scan barcode
VERSI WINDOWS OPTIMIZED - Multiple Fallback Options
Solusi untuk error HTTP 404 pyzxing
"""

import barcode
from barcode.writer import ImageWriter
import os

# Import OpenCV dengan error handling
OPENCV_AVAILABLE = False
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
    print("✅ OpenCV loaded successfully")
except ImportError as e:
    print(f"⚠️ OpenCV not available: {e}")

# Try multiple barcode scanning options
SCANNER_METHOD = None
SCANNER_ERROR_MESSAGE = ""

# Option 1: Try pyzxing (requires internet for first time)
try:
    from pyzxing import BarCodeReader
    reader = BarCodeReader()
    SCANNER_METHOD = "pyzxing"
    print("✅ Pyzxing barcode scanner initialized")
except Exception as e:
    print(f"⚠️ Pyzxing not available: {e}")
    SCANNER_ERROR_MESSAGE = str(e)
    
    # Option 2: Try pyzbar as fallback
    try:
        from pyzbar.pyzbar import decode
        SCANNER_METHOD = "pyzbar"
        print("✅ Pyzbar barcode scanner initialized (fallback)")
    except ImportError:
        print("⚠️ Pyzbar also not available")
        SCANNER_METHOD = None

WEBCAM_AVAILABLE = OPENCV_AVAILABLE and SCANNER_METHOD is not None

# ==================== FUNGSI GENERATE BARCODE ====================

def generate_barcode(barcode_id, product_name):
    """
    Fungsi untuk generate barcode image
    
    Args:
        barcode_id: ID untuk barcode
        product_name: Nama produk (untuk caption)
        
    Returns:
        str: Path file barcode atau None jika gagal
    """
    try:
        # Buat folder barcodes jika belum ada
        os.makedirs("barcodes", exist_ok=True)
        
        # Generate barcode Code128
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_id, writer=ImageWriter())
        
        # Simpan barcode
        filename = f"barcodes/{barcode_id}"
        full_path = barcode_instance.save(filename)
        
        return full_path
        
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

def generate_batch_barcodes(products_df):
    """
    Fungsi untuk generate barcode secara batch untuk banyak produk
    
    Args:
        products_df: DataFrame berisi produk-produk
        
    Returns:
        dict: Status dan jumlah barcode yang berhasil dibuat
    """
    try:
        success_count = 0
        failed_items = []
        
        for index, row in products_df.iterrows():
            result = generate_barcode(row['barcode_id'], row['nama_produk'])
            if result:
                success_count += 1
            else:
                failed_items.append(row['barcode_id'])
        
        return {
            'success': True,
            'total': len(products_df),
            'success_count': success_count,
            'failed_items': failed_items,
            'message': f"Berhasil generate {success_count} dari {len(products_df)} barcode"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

# ==================== FUNGSI SCAN BARCODE ====================

def scan_barcode_from_camera():
    """
    Fungsi untuk scan barcode menggunakan webcam
    Support multiple methods: pyzxing, pyzbar
    
    Returns:
        dict: Status dan barcode_id yang terbaca
    """
    # Cek apakah webcam tersedia
    if not WEBCAM_AVAILABLE:
        error_msg = "⚠️ Webcam scanner tidak tersedia.\n\n"
        
        if SCANNER_METHOD is None:
            if "404" in SCANNER_ERROR_MESSAGE or "HTTP" in SCANNER_ERROR_MESSAGE:
                error_msg += (
                    "**Penyebab:**\n"
                    "- Pyzxing gagal download file JAR (perlu internet)\n"
                    "- Koneksi internet bermasalah saat instalasi\n\n"
                    "**Solusi:**\n"
                    "1. **Gunakan 'Input Manual Barcode'** (Tab 2) - RECOMMENDED ✅\n"
                    "2. Atau install pyzbar sebagai alternatif:\n"
                    "   ```\n"
                    "   pip install pyzbar\n"
                    "   ```\n"
                    "   (Catatan: pyzbar butuh ZBar DLL di Windows)\n\n"
                )
            else:
                error_msg += (
                    "**Penyebab:**\n"
                    f"- {SCANNER_ERROR_MESSAGE}\n\n"
                    "**Solusi:**\n"
                    "1. **Gunakan 'Input Manual Barcode'** (Tab 2) - RECOMMENDED ✅\n"
                    "2. Reinstall scanner:\n"
                    "   ```\n"
                    "   pip install pyzxing\n"
                    "   ```\n\n"
                )
        
        error_msg += "**Catatan:** Aplikasi tetap berfungsi 100% dengan Input Manual!"
        
        return {
            'success': False,
            'message': error_msg
        }
    
    try:
        # Buka webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return {
                'success': False,
                'message': (
                    "❌ Tidak dapat membuka kamera.\n\n"
                    "**Kemungkinan penyebab:**\n"
                    "- Webcam tidak terhubung\n"
                    "- Kamera sedang digunakan aplikasi lain\n"
                    "- Permission kamera diblok\n\n"
                    "**Solusi:**\n"
                    "- Tutup aplikasi lain yang pakai kamera\n"
                    "- Gunakan 'Input Manual Barcode' sebagai alternatif"
                )
            }
        
        print(f"✅ Kamera aktif. Menggunakan scanner: {SCANNER_METHOD}")
        print("⌨️  Tekan 'q' untuk keluar")
        
        barcode_detected = None
        frame_count = 0
        scan_interval = 15  # Scan every 15 frames
        max_frames = 900  # Timeout 30 detik
        
        # Temporary file untuk pyzxing
        temp_frame_path = "temp_frame.jpg" if SCANNER_METHOD == "pyzxing" else None
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Tambahkan instruksi di frame
            text_color = (0, 255, 0)
            cv2.putText(frame, "Arahkan barcode ke kamera", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
            cv2.putText(frame, f"Scanner: {SCANNER_METHOD}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            cv2.putText(frame, "Tekan 'Q' untuk keluar", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
            
            # Scan barcode setiap interval
            if frame_count % scan_interval == 0:
                try:
                    if SCANNER_METHOD == "pyzxing":
                        # Pyzxing: simpan frame ke file
                        cv2.imwrite(temp_frame_path, frame)
                        results = reader.decode(temp_frame_path)
                        
                        if results and len(results) > 0:
                            barcode_data = results[0].get('parsed', None)
                            if barcode_data:
                                barcode_detected = barcode_data
                                cv2.rectangle(frame, (10, 10), 
                                            (frame.shape[1]-10, frame.shape[0]-10), 
                                            (0, 255, 0), 3)
                                cv2.putText(frame, f"DETECTED: {barcode_data}", (10, 120),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                cv2.imshow('Barcode Scanner - SUCCESS!', frame)
                                cv2.waitKey(1000)
                                break
                    
                    elif SCANNER_METHOD == "pyzbar":
                        # Pyzbar: decode langsung dari frame
                        decoded_objects = decode(frame)
                        
                        if decoded_objects:
                            barcode_data = decoded_objects[0].data.decode('utf-8')
                            barcode_detected = barcode_data
                            
                            # Gambar kotak
                            points = decoded_objects[0].polygon
                            if len(points) == 4:
                                pts = [(point.x, point.y) for point in points]
                                pts = np.array(pts, dtype=np.int32)
                                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                            
                            cv2.putText(frame, f"DETECTED: {barcode_data}", (10, 120),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.imshow('Barcode Scanner - SUCCESS!', frame)
                            cv2.waitKey(1000)
                            break
                            
                except Exception as scan_error:
                    # Silent fail untuk scan error
                    pass
            
            # Tampilkan frame
            cv2.imshow('Barcode Scanner - Tekan Q untuk keluar', frame)
            
            # Break jika tekan 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Hapus file temporary
        if temp_frame_path and os.path.exists(temp_frame_path):
            try:
                os.remove(temp_frame_path)
            except:
                pass
        
        if barcode_detected:
            return {
                'success': True,
                'barcode_id': barcode_detected,
                'message': f"✅ Barcode berhasil di-scan: {barcode_detected}"
            }
        else:
            return {
                'success': False,
                'message': (
                    "⏱️ Timeout - Tidak ada barcode yang terdeteksi.\n\n"
                    "**Tips:**\n"
                    "- Pastikan barcode jelas terlihat di kamera\n"
                    "- Atur jarak dan pencahayaan\n"
                    "- Pegang barcode steady (tidak goyang)\n"
                    "- Atau gunakan 'Input Manual Barcode'"
                )
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}\n\nGunakan 'Input Manual Barcode' sebagai alternatif."
        }

def scan_barcode_from_image(image_path):
    """
    Fungsi untuk scan barcode dari file gambar
    Support multiple methods
    
    Args:
        image_path: Path ke file gambar
        
    Returns:
        dict: Status dan barcode_id yang terbaca
    """
    if SCANNER_METHOD is None:
        return {
            'success': False,
            'message': "Scanner library tidak tersedia. Gunakan input manual."
        }
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return {
                'success': False,
                'message': "File gambar tidak ditemukan!"
            }
        
        if SCANNER_METHOD == "pyzxing":
            # Decode menggunakan pyzxing
            results = reader.decode(image_path)
            
            if results and len(results) > 0:
                barcode_data = results[0].get('parsed', None)
                
                if barcode_data:
                    return {
                        'success': True,
                        'barcode_id': barcode_data,
                        'message': f"Barcode berhasil di-scan: {barcode_data}"
                    }
        
        elif SCANNER_METHOD == "pyzbar":
            # Decode menggunakan pyzbar
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'success': False,
                    'message': "Gagal membaca gambar!"
                }
            
            decoded_objects = decode(image)
            
            if decoded_objects:
                barcode_data = decoded_objects[0].data.decode('utf-8')
                return {
                    'success': True,
                    'barcode_id': barcode_data,
                    'message': f"Barcode berhasil di-scan: {barcode_data}"
                }
        
        return {
            'success': False,
            'message': "Tidak ada barcode yang terdeteksi pada gambar!"
        }
            
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}"
        }

def validate_barcode_format(barcode_id):
    """
    Fungsi untuk validasi format barcode ID
    
    Args:
        barcode_id: ID barcode yang akan divalidasi
        
    Returns:
        bool: True jika valid, False jika tidak
    """
    try:
        # Validasi panjang (minimal 3 karakter)
        if len(barcode_id) < 3:
            return False
        
        # Validasi tidak boleh ada spasi
        if ' ' in barcode_id:
            return False
        
        return True
        
    except:
        return False

def check_scanner_availability():
    """
    Fungsi untuk cek apakah scanner tersedia
    
    Returns:
        dict: Status availability
    """
    if WEBCAM_AVAILABLE:
        message = f"✅ Webcam scanner tersedia ({SCANNER_METHOD})"
    else:
        if "404" in SCANNER_ERROR_MESSAGE or "HTTP" in SCANNER_ERROR_MESSAGE:
            message = (
                "⚠️ Webcam scanner tidak tersedia\n\n"
                "Pyzxing gagal download file JAR (HTTP 404).\n"
                "Ini terjadi karena pyzxing membutuhkan internet untuk download ZXing library.\n\n"
                "**SOLUSI MUDAH:**\n"
                "Gunakan 'Input Manual Barcode' (Tab 2) - Sama cepatnya! ✅\n\n"
                "**Alternatif (opsional):**\n"
                "Install pyzbar: pip install pyzbar\n"
                "(Catatan: pyzbar butuh ZBar DLL di Windows)"
            )
        else:
            message = f"⚠️ Webcam scanner tidak tersedia - {SCANNER_ERROR_MESSAGE}\n\nGunakan Input Manual"
    
    return {
        'available': WEBCAM_AVAILABLE,
        'message': message,
        'method': SCANNER_METHOD
    }

# ==================== FUNGSI GET PRODUCT BY BARCODE ====================

def get_product_by_barcode(barcode_id):
    """
    Fungsi untuk mendapatkan data produk berdasarkan barcode
    (Menggunakan fungsi dari data_handler)
    
    Args:
        barcode_id: ID barcode
        
    Returns:
        dict atau None: Data produk
    """
    from modules.data_handler import get_product_by_barcode as get_product
    return get_product(barcode_id)