"""
Pure Python implementation of DCT-based frame compression
No C++ compilation required!
"""
import cv2
import numpy as np
import os
import pickle
from scipy.fftpack import dct, idct

def dct2(block):
    """2D DCT"""
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block):
    """2D IDCT"""
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

def apply_triangular_quantization(coeffs, factor):
    """Apply triangular quantization: K(u,v) = 15-(u+v)"""
    for u in range(8):
        for v in range(8):
            K = 15 - (u + v)
            if K <= factor:
                coeffs[u, v] = 0
    return coeffs

def compress_frame(frame, compression_factor=8):
    """
    Compress a single frame using DCT
    
    Args:
        frame: numpy array (H, W, C)
        compression_factor: 0-15 (higher = more compression)
    
    Returns:
        dict with compressed data
    """
    H, W, C = frame.shape
    H8 = ((H + 7) // 8) * 8
    W8 = ((W + 7) // 8) * 8
    
    # Pad to multiple of 8
    padded = np.zeros((H8, W8, C), dtype=np.uint8)
    padded[:H, :W, :] = frame
    
    compressed_data = {
        'width': W,
        'height': H,
        'channels': C,
        'factor': compression_factor,
        'blocks': []
    }
    
    # Process 8x8 blocks
    for by in range(0, H8, 8):
        for bx in range(0, W8, 8):
            for c in range(C):
                # Extract block and shift to [-128, 127]
                block = padded[by:by+8, bx:bx+8, c].astype(np.float64) - 128.0
                
                # DCT
                dct_block = dct2(block)
                
                # Quantization
                dct_block = apply_triangular_quantization(dct_block, compression_factor)
                
                # Round and store
                compressed_data['blocks'].append(np.round(dct_block).astype(np.int16))
    
    return compressed_data

def decompress_frame(compressed_data):
    """
    Decompress frame data
    
    Args:
        compressed_data: dict from compress_frame
    
    Returns:
        numpy array (H, W, C)
    """
    W = compressed_data['width']
    H = compressed_data['height']
    C = compressed_data['channels']
    blocks = compressed_data['blocks']
    
    H8 = ((H + 7) // 8) * 8
    W8 = ((W + 7) // 8) * 8
    
    reconstructed = np.zeros((H8, W8, C), dtype=np.uint8)
    
    block_idx = 0
    for by in range(0, H8, 8):
        for bx in range(0, W8, 8):
            for c in range(C):
                # Get DCT coefficients
                dct_block = blocks[block_idx].astype(np.float64)
                block_idx += 1
                
                # IDCT
                spatial_block = idct2(dct_block)
                
                # Shift back to [0, 255] and clip
                spatial_block = np.clip(spatial_block + 128.0, 0, 255)
                
                reconstructed[by:by+8, bx:bx+8, c] = spatial_block.astype(np.uint8)
    
    # Crop to original size
    return reconstructed[:H, :W, :]

def compress_yolo_frames_python(compression_factor=8, status_callback=None):
    """
    Python-based compression (no C++ required!)
    
    Args:
        compression_factor: 0-15 (default 8)
        status_callback: Optional callback for status updates
    
    Returns:
        tuple: (success, message, stats)
    """
    def update_status(msg):
        if status_callback:
            status_callback(msg)
        print(msg)
    
    video_path = "output/yolo_predict.mp4"
    output_dir = "output"
    
    if not os.path.exists(video_path):
        return False, f"Video not found: {video_path}", {}
    
    # Create output directories
    frames_dir = os.path.join(output_dir, "frames_extracted")
    compressed_dir = os.path.join(output_dir, "frames_compressed")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(compressed_dir, exist_ok=True)
    
    try:
        # Open video
        update_status("Kompresija: Odpiranje videa...")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, f"Cannot open video: {video_path}", {}
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        update_status(f"Kompresija: Ekstrahiranje vsakega 5. frame-a ({total_frames} skupaj)...")
        
        frame_idx = 0
        extracted_count = 0
        frames_to_compress = []
        
        # Extract every 5th frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % 5 == 0:
                frame_filename = os.path.join(frames_dir, f"frame_{frame_idx:06d}.png")
                cv2.imwrite(frame_filename, frame)
                frames_to_compress.append((frame_idx, frame))
                extracted_count += 1
                
                if extracted_count % 20 == 0:
                    update_status(f"Kompresija: Ekstrahirano {extracted_count} frame-ov...")
            
            frame_idx += 1
        
        cap.release()
        update_status(f"Kompresija: Ekstrahirano {extracted_count} frame-ov")
        
        # Compress each frame
        update_status(f"Kompresija: Stiskanje frame-ov (faktor {compression_factor})...")
        
        compressed_count = 0
        original_size = 0
        compressed_size = 0
        
        for frame_idx, frame in frames_to_compress:
            try:
                # Compress
                compressed_data = compress_frame(frame, compression_factor)
                
                # Save compressed data
                output_path = os.path.join(compressed_dir, f"frame_{frame_idx:06d}.pkl")
                with open(output_path, 'wb') as f:
                    pickle.dump(compressed_data, f)
                
                # Calculate sizes
                original_size += frame.nbytes
                compressed_size += os.path.getsize(output_path)
                
                compressed_count += 1
                if compressed_count % 20 == 0:
                    update_status(f"Kompresija: Stisnjeno {compressed_count}/{extracted_count} frame-ov...")
            
            except Exception as e:
                print(f"Error compressing frame {frame_idx}: {e}")
        
        stats = {
            'extracted_frames': extracted_count,
            'compressed_frames': compressed_count,
            'failed_frames': extracted_count - compressed_count,
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
            return False, "Kompresija ni uspela", stats
    
    except Exception as e:
        return False, f"Napaka pri kompresiji: {str(e)}", {}

def check_python_compressor_available():
    """Check if scipy is available for Python compression"""
    try:
        import scipy.fftpack
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    # Test compression
    print("Testing Python compression...")
    success, msg, stats = compress_yolo_frames_python()
    
    if success:
        print(f"\n✓ {msg}")
        print(f"  Original: {stats['original_size_mb']:.2f} MB")
        print(f"  Compressed: {stats['compressed_size_mb']:.2f} MB")
        print(f"  Ratio: {stats['compression_ratio']:.2f}x")
    else:
        print(f"\n✗ {msg}")
