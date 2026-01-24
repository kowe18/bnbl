"""
Quick test to verify the compression setup is ready
"""
import os
import sys

def test_setup():
    print("Testing Video Frame Compression Setup")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Test 1: Check if video exists
    print("1. Checking for video file...")
    video_path = "output/yolo_predict.mp4"
    if os.path.exists(video_path):
        size_mb = os.path.getsize(video_path) / 1024 / 1024
        print(f"   ✓ Video found: {video_path} ({size_mb:.2f} MB)")
    else:
        print(f"   ✗ Video not found: {video_path}")
        print("     → Run the fatigue detection pipeline first")
        all_ok = False
    print()
    
    # Test 2: Check if C++ source exists
    print("2. Checking for C++ source code...")
    cpp_file = "video_frame_compressor.cpp"
    if os.path.exists(cpp_file):
        lines = len(open(cpp_file).readlines())
        print(f"   ✓ C++ source found: {cpp_file} ({lines} lines)")
    else:
        print(f"   ✗ C++ source not found: {cpp_file}")
        all_ok = False
    print()
    
    # Test 3: Check if C++ executable exists
    print("3. Checking for compiled C++ executable...")
    exe_name = "video_frame_compressor.exe" if os.name == 'nt' else "video_frame_compressor"
    if os.path.exists(exe_name):
        size_kb = os.path.getsize(exe_name) / 1024
        print(f"   ✓ Executable found: {exe_name} ({size_kb:.2f} KB)")
    else:
        print(f"   ✗ Executable not found: {exe_name}")
        print("     → Compile using: build_compressor.bat")
        all_ok = False
    print()
    
    # Test 4: Check Python dependencies
    print("4. Checking Python dependencies...")
    try:
        import cv2
        print(f"   ✓ OpenCV installed: version {cv2.__version__}")
    except ImportError:
        print("   ✗ OpenCV not installed")
        print("     → Install using: pip install opencv-python")
        all_ok = False
    print()
    
    # Test 5: Check output directory
    print("5. Checking output directory...")
    if os.path.exists("output"):
        print("   ✓ Output directory exists")
    else:
        print("   ✗ Output directory not found")
        os.makedirs("output", exist_ok=True)
        print("   ✓ Created output directory")
    print()
    
    # Test 6: Check helper scripts
    print("6. Checking helper scripts...")
    scripts = [
        "compress_video_frames.py",
        "run_compression.py",
        "CMakeLists.txt",
        "build_compressor.bat"
    ]
    for script in scripts:
        if os.path.exists(script):
            print(f"   ✓ {script}")
        else:
            print(f"   ✗ {script} missing")
            all_ok = False
    print()
    
    # Summary
    print("=" * 60)
    if all_ok:
        print("✓ ALL TESTS PASSED!")
        print()
        print("You're ready to compress frames!")
        print("Run: python run_compression.py")
    else:
        print("✗ SOME TESTS FAILED")
        print()
        print("Please fix the issues above before running compression.")
        print("See COMPRESSION_README.md for detailed instructions.")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
