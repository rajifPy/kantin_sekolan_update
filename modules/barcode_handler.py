"""
Module untuk menangani generate dan scan barcode
VERSI STREAMLIT NATIVE - Preview di Browser
"""

import barcode
from barcode.writer import ImageWriter
import os
import streamlit as st
import time

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

# Option 1: Try pyzxing
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
    """Fungsi untuk generate barcode image"""
    try:
        os.makedirs("barcodes", exist_ok=True)
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_id, writer=ImageWriter())
        filename = f"barcodes/{barcode_id}"
        full_path = barcode_instance.save(filename)
        return full_path
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

def generate_batch_barcodes(products_df):
    """Fungsi untuk generate barcode secara batch"""
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

# ==================== HELPER FUNCTIONS FOR UI ====================

def draw_scan_frame(frame, status="scanning", message="Arahkan barcode ke area hijau"):
    """
    Menggambar frame UI untuk scanning dengan overlay
    """
    height, width = frame.shape[:2]
    
    # Status color
    if status == "scanning":
        color = (0, 255, 0)  # Green
        box_color = (0, 255, 0)
    elif status == "detected":
        color = (0, 255, 0)  # Green
        box_color = (0, 255, 0)
    else:  # error
        color = (0, 0, 255)  # Red
        box_color = (0, 0, 255)
    
    # Draw scan area (center rectangle)
    scan_width = int(width * 0.6)
    scan_height = int(height * 0.4)
    scan_x = (width - scan_width) // 2
    scan_y = (height - scan_height) // 2
    
    # Draw corner markers
    corner_length = 30
    corner_thickness = 3
    
    # Top-left corner
    cv2.line(frame, (scan_x, scan_y), (scan_x + corner_length, scan_y), box_color, corner_thickness)
    cv2.line(frame, (scan_x, scan_y), (scan_x, scan_y + corner_length), box_color, corner_thickness)
    
    # Top-right corner
    cv2.line(frame, (scan_x + scan_width, scan_y), (scan_x + scan_width - corner_length, scan_y), box_color, corner_thickness)
    cv2.line(frame, (scan_x + scan_width, scan_y), (scan_x + scan_width, scan_y + corner_length), box_color, corner_thickness)
    
    # Bottom-left corner
    cv2.line(frame, (scan_x, scan_y + scan_height), (scan_x + corner_length, scan_y + scan_height), box_color, corner_thickness)
    cv2.line(frame, (scan_x, scan_y + scan_height), (scan_x, scan_y + corner_length), box_color, corner_thickness)
    
    # Bottom-right corner
    cv2.line(frame, (scan_x + scan_width, scan_y + scan_height), (scan_x + scan_width - corner_length, scan_y + scan_height), box_color, corner_thickness)
    cv2.line(frame, (scan_x + scan_width, scan_y + scan_height), (scan_x + scan_width, scan_y + scan_height - corner_length), box_color, corner_thickness)
    
    # Draw scanning line animation
    scan_line_y = scan_y + (scan_height // 2)
    cv2.line(frame, (scan_x, scan_line_y), (scan_x + scan_width, scan_line_y), (0, 255, 255), 2)
    
    # Dark overlay outside scan area
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.rectangle(mask, (scan_x, scan_y), (scan_x + scan_width, scan_y + scan_height), 255, -1)
    mask_inv = cv2.bitwise_not(mask)
    
    frame_dark = frame.copy()
    frame_dark = cv2.addWeighted(frame_dark, 0.3, frame_dark, 0, 0)
    frame = np.where(mask_inv[:, :, np.newaxis] == 255, frame_dark, frame)
    
    # Draw top banner
    banner_height = 80
    cv2.rectangle(frame, (0, 0), (width, banner_height), (0, 0, 0), -1)
    cv2.rectangle(frame, (0, 0), (width, banner_height), color, 3)
    
    cv2.putText(frame, "BARCODE SCANNER - REAL TIME", 
               (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, message, 
               (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Draw bottom info bar
    info_y = height - 100
    cv2.rectangle(frame, (0, info_y), (width, height), (0, 0, 0), -1)
    cv2.rectangle(frame, (0, info_y), (width, height), (100, 100, 100), 2)
    
    instructions = [
        ("Scanner:", f"{SCANNER_METHOD.upper() if SCANNER_METHOD else 'N/A'}", (20, info_y + 25)),
        ("Tips:", "Letakkan barcode di area hijau", (20, info_y + 50)),
        ("Control:", "Klik 'Stop' untuk berhenti", (20, info_y + 75))
    ]
    
    for label, value, pos in instructions:
        cv2.putText(frame, f"{label} {value}", pos, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    return frame

def draw_detected_barcode(frame, barcode_data, barcode_rect=None):
    """Menggambar highlight saat barcode terdeteksi"""
    height, width = frame.shape[:2]
    
    # Draw success banner
    cv2.rectangle(frame, (0, 0), (width, 100), (0, 200, 0), -1)
    
    # Success icon (checkmark)
    cv2.circle(frame, (50, 50), 30, (255, 255, 255), 3)
    cv2.line(frame, (35, 50), (45, 60), (255, 255, 255), 3)
    cv2.line(frame, (45, 60), (65, 35), (255, 255, 255), 3)
    
    # Success text
    cv2.putText(frame, "BARCODE DETECTED!", 
               (100, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"ID: {barcode_data}", 
               (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Highlight barcode area if coordinates provided
    if barcode_rect:
        x, y, w, h = barcode_rect
        cv2.rectangle(frame, (x-10, y-10), (x+w+10, y+h+10), (0, 255, 0), 3)
        
        corner_len = 20
        # Corners
        cv2.line(frame, (x-10, y-10), (x-10+corner_len, y-10), (0, 255, 0), 5)
        cv2.line(frame, (x-10, y-10), (x-10, y-10+corner_len), (0, 255, 0), 5)
        cv2.line(frame, (x+w+10, y-10), (x+w+10-corner_len, y-10), (0, 255, 0), 5)
        cv2.line(frame, (x+w+10, y-10), (x+w+10, y-10+corner_len), (0, 255, 0), 5)
        cv2.line(frame, (x-10, y+h+10), (x-10+corner_len, y+h+10), (0, 255, 0), 5)
        cv2.line(frame, (x-10, y+h+10), (x-10, y+h+10-corner_len), (0, 255, 0), 5)
        cv2.line(frame, (x+w+10, y+h+10), (x+w+10-corner_len, y+h+10), (0, 255, 0), 5)
        cv2.line(frame, (x+w+10, y+h+10), (x+w+10, y+h+10-corner_len), (0, 255, 0), 5)
    
    return frame

# ==================== STREAMLIT NATIVE CAMERA SCANNER ====================

def scan_barcode_from_camera_streamlit():
    """
    Fungsi untuk scan barcode dengan preview di Streamlit
    Menggunakan st.camera_input() untuk capture
    
    Returns:
        dict: Status dan barcode_id yang terbaca
    """
    if not WEBCAM_AVAILABLE:
        error_msg = "⚠️ Webcam scanner tidak tersedia.\n\n"
        
        if SCANNER_METHOD is None:
            if "404" in SCANNER_ERROR_MESSAGE or "HTTP" in SCANNER_ERROR_MESSAGE:
                error_msg += (
                    "**Penyebab:**\n"
                    "- Pyzxing gagal download file JAR (perlu internet)\n\n"
                    "**Solusi:**\n"
                    "1. **Gunakan 'Input Manual Barcode'** ✅\n"
                    "2. Atau install pyzbar: `pip install pyzbar`\n\n"
                )
            else:
                error_msg += f"**Error:** {SCANNER_ERROR_MESSAGE}\n\n"
        
        error_msg += "**Catatan:** Aplikasi tetap berfungsi dengan Input Manual!"
        
        return {
            'success': False,
            'message': error_msg
        }
    
    try:
        # Streamlit camera input (simplified approach)
        st.info("📸 **Ambil foto barcode menggunakan kamera**")
        
        camera_photo = st.camera_input("Arahkan kamera ke barcode, lalu klik 'Take Photo'")
        
        if camera_photo is not None:
            # Save temporary image
            temp_path = "temp_camera_capture.jpg"
            with open(temp_path, "wb") as f:
                f.write(camera_photo.getbuffer())
            
            st.image(camera_photo, caption="Foto yang diambil", width=400)
            
            with st.spinner("🔍 Scanning barcode dari foto..."):
                # Scan barcode dari foto
                if SCANNER_METHOD == "pyzxing":
                    try:
                        results = reader.decode(temp_path)
                        
                        if results and len(results) > 0:
                            barcode_data = results[0].get('parsed', None)
                            if barcode_data:
                                # Cleanup
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                
                                return {
                                    'success': True,
                                    'barcode_id': barcode_data,
                                    'message': f"✅ Barcode berhasil di-scan: {barcode_data}"
                                }
                    except Exception as e:
                        st.error(f"Error scanning: {e}")
                
                elif SCANNER_METHOD == "pyzbar":
                    try:
                        image = cv2.imread(temp_path)
                        if image is not None:
                            decoded_objects = decode(image)
                            
                            if decoded_objects:
                                barcode_data = decoded_objects[0].data.decode('utf-8')
                                
                                # Cleanup
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                
                                return {
                                    'success': True,
                                    'barcode_id': barcode_data,
                                    'message': f"✅ Barcode berhasil di-scan: {barcode_data}"
                                }
                    except Exception as e:
                        st.error(f"Error scanning: {e}")
                
                # Cleanup jika gagal
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                st.warning("⚠️ Tidak ada barcode yang terdeteksi. Coba ambil foto lagi dengan kondisi:")
                st.markdown("""
                - ✅ Barcode jelas dan fokus
                - ✅ Pencahayaan cukup
                - ✅ Tidak blur atau goyang
                - ✅ Jarak 10-20 cm
                """)
        
        return {
            'success': False,
            'message': "Ambil foto barcode terlebih dahulu"
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}\n\nGunakan 'Input Manual Barcode' sebagai alternatif."
        }

# ==================== ORIGINAL OPENCV WINDOW SCANNER ====================

def scan_barcode_from_camera():
    """
    Fungsi original dengan OpenCV window terpisah
    (Untuk backward compatibility)
    """
    if not WEBCAM_AVAILABLE:
        error_msg = "⚠️ Webcam scanner tidak tersedia.\n\n"
        
        if SCANNER_METHOD is None:
            if "404" in SCANNER_ERROR_MESSAGE or "HTTP" in SCANNER_ERROR_MESSAGE:
                error_msg += (
                    "**Penyebab:**\n"
                    "- Pyzxing gagal download file JAR (perlu internet)\n\n"
                    "**Solusi:**\n"
                    "1. **Gunakan 'Input Manual Barcode'** ✅\n"
                    "2. Atau install pyzbar: `pip install pyzbar`\n\n"
                )
            else:
                error_msg += f"**Error:** {SCANNER_ERROR_MESSAGE}\n\n"
        
        error_msg += "**Catatan:** Aplikasi tetap berfungsi dengan Input Manual!"
        
        return {
            'success': False,
            'message': error_msg
        }
    
    try:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not cap.isOpened():
            return {
                'success': False,
                'message': (
                    "❌ Tidak dapat membuka kamera.\n\n"
                    "**Solusi:**\n"
                    "- Tutup aplikasi lain yang pakai kamera\n"
                    "- Gunakan 'Input Manual Barcode'"
                )
            }
        
        print(f"✅ Kamera aktif dengan Real-time Preview")
        print(f"📷 Scanner: {SCANNER_METHOD}")
        print("⌨️  Tekan 'Q' untuk keluar")
        
        barcode_detected = None
        frame_count = 0
        scan_interval = 10
        max_frames = 900
        
        temp_frame_path = "temp_scan_frame.jpg" if SCANNER_METHOD == "pyzxing" else None
        
        window_name = "🏪 Kantin Scanner - Real-time Preview (Tekan Q untuk keluar)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            current_status = "scanning"
            current_message = "Arahkan barcode ke area hijau - Hold steady"
            detected_rect = None
            
            if frame_count % scan_interval == 0:
                try:
                    if SCANNER_METHOD == "pyzxing":
                        cv2.imwrite(temp_frame_path, frame)
                        results = reader.decode(temp_frame_path)
                        
                        if results and len(results) > 0:
                            barcode_data = results[0].get('parsed', None)
                            if barcode_data:
                                barcode_detected = barcode_data
                                current_status = "detected"
                                current_message = f"BARCODE TERDETEKSI: {barcode_data}"
                    
                    elif SCANNER_METHOD == "pyzbar":
                        decoded_objects = decode(frame)
                        
                        if decoded_objects:
                            obj = decoded_objects[0]
                            barcode_data = obj.data.decode('utf-8')
                            barcode_detected = barcode_data
                            current_status = "detected"
                            current_message = f"BARCODE TERDETEKSI: {barcode_data}"
                            
                            rect = obj.rect
                            detected_rect = (rect.left, rect.top, rect.width, rect.height)
                
                except Exception:
                    current_status = "scanning"
            
            # Draw UI
            if current_status == "detected" and barcode_detected:
                frame = draw_detected_barcode(frame, barcode_detected, detected_rect)
            else:
                frame = draw_scan_frame(frame, current_status, current_message)
            
            # Add FPS
            fps_text = f"FPS: {int(cap.get(cv2.CAP_PROP_FPS))}"
            cv2.putText(frame, fps_text, (frame.shape[1] - 120, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.imshow(window_name, frame)
            
            if barcode_detected:
                cv2.waitKey(1500)
                break
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("👋 Scan dibatalkan oleh user")
                break
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
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
                    "⏱️ Scan selesai tanpa hasil.\n\n"
                    "**Tips:**\n"
                    "- Pastikan barcode jelas dan tidak blur\n"
                    "- Letakkan barcode di area hijau\n"
                    "- Pegang steady (jangan goyang)\n"
                    "- Atau gunakan 'Input Manual Barcode'"
                )
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"❌ Error: {str(e)}\n\nGunakan 'Input Manual Barcode' sebagai alternatif."
        }

# ==================== OTHER FUNCTIONS ====================

def scan_barcode_from_image(image_path):
    """Fungsi untuk scan barcode dari file gambar"""
    if SCANNER_METHOD is None:
        return {
            'success': False,
            'message': "Scanner library tidak tersedia. Gunakan input manual."
        }
    
    try:
        if not os.path.exists(image_path):
            return {
                'success': False,
                'message': "File gambar tidak ditemukan!"
            }
        
        if SCANNER_METHOD == "pyzxing":
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
            image = cv2.imread(image_path)
            if image is None:
                return {'success': False, 'message': "Gagal membaca gambar!"}
            
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
    """Validasi format barcode ID"""
    try:
        if len(barcode_id) < 3:
            return False
        if ' ' in barcode_id:
            return False
        return True
    except:
        return False

def check_scanner_availability():
    """Cek availability scanner"""
    if WEBCAM_AVAILABLE:
        message = f"✅ Webcam scanner tersedia ({SCANNER_METHOD}) dengan Real-time Preview"
    else:
        if "404" in SCANNER_ERROR_MESSAGE or "HTTP" in SCANNER_ERROR_MESSAGE:
            message = (
                "⚠️ Webcam scanner tidak tersedia (Pyzxing HTTP 404)\n\n"
                "**SOLUSI MUDAH:** Gunakan 'Input Manual Barcode' ✅"
            )
        else:
            message = f"⚠️ Scanner tidak tersedia - Gunakan Input Manual"
    
    return {
        'available': WEBCAM_AVAILABLE,
        'message': message,
        'method': SCANNER_METHOD
    }

def get_product_by_barcode(barcode_id):
    """Get product data by barcode ID"""
    from modules.data_handler import get_product_by_barcode as get_product
    return get_product(barcode_id)
