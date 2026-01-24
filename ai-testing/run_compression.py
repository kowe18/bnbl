"""
Simple script to compress every 5th frame from yolo_predict.mp4
This script checks for the C++ executable and guides you through the process.
"""
import os
import sys
import subprocess

def check_cpp_executable():
    """Check if C++ compressor is compiled"""
    exe_name = "video_frame_compressor.exe" if os.name == 'nt' else "video_frame_compressor"
    
    if os.path.exists(exe_name):
        print(f"✓ Found C++ compressor: {exe_name}")
        return True
    else:
        print(f"✗ C++ compressor not found: {exe_name}")
        print("\nYou need to compile it first:")
        print("  1. Make sure you have OpenCV and CMake installed")
        print("  2. Run: build_compressor.bat (Windows)")
        print("     Or: mkdir build && cd build && cmake .. && make && cp video_frame_compressor .. && cd ..")
        print("\nSee COMPRESSION_README.md for detailed instructions.")
        return False

def check_video():
    """Check if video exists"""
    video_path = "output/yolo_predict.mp4"
    
    if os.path.exists(video_path):
        print(f"✓ Found video: {video_path}")
        return True
    else:
        print(f"✗ Video not found: {video_path}")
        print("\nYou need to generate it first:")
        print("  1. Run: python start_gui.py")
        print("  2. Select 'POPOLNA ANALIZA (VIDEO)'")
        print("  3. Process a video file")
        return False

def main():
    print("=" * 60)
    print("VIDEO FRAME COMPRESSION TOOL")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    print()
    
    video_ok = check_video()
    cpp_ok = check_cpp_executable()
    
    print()
    
    if not video_ok or not cpp_ok:
        print("✗ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    print("✓ All prerequisites met!")
    print()
    print("=" * 60)
    print()
    
    # Run compression
    print("Starting compression process...")
    print()
    
    try:
        result = subprocess.run([sys.executable, "compress_video_frames.py"], check=True)
        print()
        print("=" * 60)
        print("✓ COMPRESSION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ COMPRESSION FAILED!")
        print("=" * 60)
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("Compression cancelled by user.")
        sys.exit(1)

if __name__ == "__main__":
    main()
