"""
Compression module for GUI integration
Compresses every 5th frame from yolo_predict.mp4
Uses exact Python translation of C++ algorithm (default, no compilation needed)
Also supports C++ executable as fallback option
"""
import cv2
import os
import subprocess
import sys

# Import exact C++ algorithm translation
try:
    from compression_exact import compress_yolo_frames_exact
    EXACT_COMPRESSION_AVAILABLE = True
except ImportError:
    EXACT_COMPRESSION_AVAILABLE = False

def compress_yolo_frames(compression_factor=8, status_callback=None, prefer_cpp=False):
    """
    Compress every 5th frame from output/yolo_predict.mp4
    Uses exact Python translation of C++ algorithm (default, recommended)
    
    Args:
        compression_factor: Compression factor (0-15, default 8)
        status_callback: Optional callback function to update status (takes string)
        prefer_cpp: Try C++ executable first if available (default False, uses Python exact implementation)
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    # Check what's available
    cpp_available = check_compressor_available()
    python_available = EXACT_COMPRESSION_AVAILABLE
    
    # Decide which method to use
    use_cpp = cpp_available and prefer_cpp
    use_python = python_available and not use_cpp
    
    if use_cpp:
        if status_callback:
            status_callback("Kompresija: Uporaba C++ kompresorja...")
        return _compress_with_cpp(compression_factor, status_callback)
    elif use_python:
        if status_callback:
            status_callback("Kompresija: Uporaba Python kompresorja (exact C++ algorithm)...")
        return compress_yolo_frames_exact(compression_factor, status_callback)
    elif cpp_available:
        # Fallback to C++ if Python not available
        if status_callback:
            status_callback("Kompresija: Uporaba C++ kompresorja (fallback)...")
        return _compress_with_cpp(compression_factor, status_callback)
    else:
        msg = "Kompresor ni na voljo"
        if not python_available:
            msg += " (manjka compression_exact.py)"
        return False, msg, {}

def _compress_with_cpp(compression_factor, status_callback):
    """
    Compress every 5th frame from output/yolo_predict.mp4
    
    Args:
        compression_factor: Compression factor (0-15, default 8)
        status_callback: Optional callback function to update status (takes string)
    
    Returns:
        tuple: (success: bool, message: str, stats: dict)
    """
    def update_status(msg):
        if status_callback:
            status_callback(msg)
        print(msg)
    
    video_path = "output/yolo_predict.mp4"
    output_dir = "output"
    
    # Check if video exists
    if not os.path.exists(video_path):
        return False, f"Video not found: {video_path}", {}
    
    # Create output directories
    frames_dir = os.path.join(output_dir, "frames_extracted")
    compressed_dir = os.path.join(output_dir, "frames_compressed")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(compressed_dir, exist_ok=True)
    
    # Check if C++ executable exists
    cpp_exe = "video_frame_compressor.exe" if os.name == 'nt' else "video_frame_compressor"
    if not os.path.exists(cpp_exe):
        return False, f"C++ compressor not found: {cpp_exe}. Please compile it first.", {}
    
    try:
        # Open video
        update_status("Kompresija: Odpiranje videa...")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, f"Cannot open video: {video_path}", {}
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        update_status(f"Kompresija: Ekstrahiranje vsakega 5. frame-a ({total_frames} skupaj)...")
        
        frame_idx = 0
        extracted_count = 0
        
        # Extract every 5th frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % 5 == 0:
                frame_filename = os.path.join(frames_dir, f"frame_{frame_idx:06d}.png")
                cv2.imwrite(frame_filename, frame)
                extracted_count += 1
                
                if extracted_count % 20 == 0:
                    update_status(f"Kompresija: Ekstrahirano {extracted_count} frame-ov...")
            
            frame_idx += 1
        
        cap.release()
        update_status(f"Kompresija: Ekstrahirano {extracted_count} frame-ov")
        
        # Compress each extracted frame
        update_status(f"Kompresija: Stiskanje frame-ov (faktor {compression_factor})...")
        
        compressed_count = 0
        failed_count = 0
        
        for filename in sorted(os.listdir(frames_dir)):
            if filename.endswith('.png'):
                input_path = os.path.join(frames_dir, filename)
                output_path = os.path.join(compressed_dir, filename.replace('.png', '.bin'))
                
                # Prepare input for C++ program
                input_data = f"c\n{input_path}\n{output_path}\n{compression_factor}\nd\n"
                
                try:
                    # Run C++ compressor
                    result = subprocess.run(
                        [cpp_exe],
                        input=input_data,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        compressed_count += 1
                        if compressed_count % 20 == 0:
                            update_status(f"Kompresija: Stisnjeno {compressed_count}/{extracted_count} frame-ov...")
                    else:
                        failed_count += 1
                
                except subprocess.TimeoutExpired:
                    failed_count += 1
                except Exception:
                    failed_count += 1
        
        # Calculate statistics
        original_size = sum(os.path.getsize(os.path.join(frames_dir, f)) 
                           for f in os.listdir(frames_dir) if f.endswith('.png'))
        compressed_size = sum(os.path.getsize(os.path.join(compressed_dir, f)) 
                             for f in os.listdir(compressed_dir) if f.endswith('.bin'))
        
        stats = {
            'extracted_frames': extracted_count,
            'compressed_frames': compressed_count,
            'failed_frames': failed_count,
            'original_size_mb': original_size / 1024 / 1024,
            'compressed_size_mb': compressed_size / 1024 / 1024,
            'compression_ratio': original_size / compressed_size if compressed_size > 0 else 0
        }
        
        if compressed_count > 0:
            msg = (f"Kompresija končana: {compressed_count} frame-ov stisnjenih "
                   f"({stats['compression_ratio']:.2f}x razmerje)")
            update_status(msg)
            return True, msg, stats
        else:
            return False, "Kompresija ni uspela - nobeden frame ni bil stisnjen", stats
    
    except Exception as e:
        return False, f"Napaka pri kompresiji: {str(e)}", {}


def check_compressor_available():
    """Check if C++ compressor is available"""
    cpp_exe = "video_frame_compressor.exe" if os.name == 'nt' else "video_frame_compressor"
    return os.path.exists(cpp_exe)

def check_any_compressor_available():
    """Check if any compressor (C++ or exact Python) is available"""
    return check_compressor_available() or EXACT_COMPRESSION_AVAILABLE
