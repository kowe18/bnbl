import cv2
import os
import subprocess
import sys

def compress_every_5th_frame(video_path, output_dir, compression_factor=8):
    """
    Extract every 5th frame from video and compress using C++ compressor.
    
    Args:
        video_path: Path to input video
        output_dir: Directory to store compressed frames
        compression_factor: Compression factor (0-15)
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    # Create output directories
    frames_dir = os.path.join(output_dir, "frames_extracted")
    compressed_dir = os.path.join(output_dir, "frames_compressed")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(compressed_dir, exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video: {video_path}")
        return False
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Video info:")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Extracting every 5th frame...")
    
    frame_idx = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Extract every 5th frame
        if frame_idx % 5 == 0:
            frame_filename = os.path.join(frames_dir, f"frame_{frame_idx:06d}.png")
            cv2.imwrite(frame_filename, frame)
            extracted_count += 1
            
            if extracted_count % 10 == 0:
                print(f"  Extracted {extracted_count} frames...")
        
        frame_idx += 1
    
    cap.release()
    print(f"✓ Extracted {extracted_count} frames to {frames_dir}")
    
    # Compress each extracted frame using C++ compressor
    print(f"\nCompressing frames with factor {compression_factor}...")
    
    # Check if C++ executable exists
    cpp_exe = "./video_frame_compressor.exe" if os.name == 'nt' else "./video_frame_compressor"
    if not os.path.exists(cpp_exe):
        print(f"Error: C++ compressor not found: {cpp_exe}")
        print("Please compile video_frame_compressor.cpp first!")
        return False
    
    compressed_count = 0
    for filename in sorted(os.listdir(frames_dir)):
        if filename.endswith('.png'):
            input_path = os.path.join(frames_dir, filename)
            output_path = os.path.join(compressed_dir, filename.replace('.png', '.bin'))
            
            # Prepare input for C++ program
            input_data = f"c\n{input_path}\n{output_path}\n{compression_factor}\n"
            
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
                    if compressed_count % 10 == 0:
                        print(f"  Compressed {compressed_count}/{extracted_count} frames...")
                else:
                    print(f"  Error compressing {filename}: {result.stderr}")
            
            except subprocess.TimeoutExpired:
                print(f"  Timeout compressing {filename}")
            except Exception as e:
                print(f"  Exception compressing {filename}: {e}")
    
    print(f"\n✓ Compressed {compressed_count} frames to {compressed_dir}")
    
    # Calculate statistics
    original_size = sum(os.path.getsize(os.path.join(frames_dir, f)) 
                       for f in os.listdir(frames_dir) if f.endswith('.png'))
    compressed_size = sum(os.path.getsize(os.path.join(compressed_dir, f)) 
                         for f in os.listdir(compressed_dir) if f.endswith('.bin'))
    
    print(f"\n=== COMPRESSION STATISTICS ===")
    print(f"Original size: {original_size / 1024 / 1024:.2f} MB")
    print(f"Compressed size: {compressed_size / 1024 / 1024:.2f} MB")
    print(f"Compression ratio: {original_size / compressed_size:.2f}x")
    
    return True


if __name__ == "__main__":
    # Default paths
    video_path = "output/yolo_predict.mp4"
    output_dir = "output"
    compression_factor = 8  # Default compression factor
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"Error: Video not found at {video_path}")
        print("Please run the fatigue detection pipeline first to generate yolo_predict.mp4")
        sys.exit(1)
    
    # Run compression
    success = compress_every_5th_frame(video_path, output_dir, compression_factor)
    
    if success:
        print("\n✓ All done!")
    else:
        print("\n✗ Compression failed!")
        sys.exit(1)
