# Video Frame Compression Tool

This tool extracts every 5th frame from `output/yolo_predict.mp4` and compresses them using a custom DCT-based compression algorithm.

## Prerequisites

1. **OpenCV** - Required for C++ compressor
   - Windows: Download from https://opencv.org/releases/
   - Or install via vcpkg: `vcpkg install opencv`

2. **CMake** - For building the C++ code
   - Download from https://cmake.org/download/

3. **C++ Compiler**
   - Windows: MinGW-w64 or Visual Studio
   - Linux: g++

4. **Python 3** with OpenCV
   ```bash
   pip install opencv-python
   ```

## Build Instructions

### Windows

1. **Option 1: Using CMake (Recommended)**
   ```cmd
   mkdir build
   cd build
   cmake .. -G "MinGW Makefiles"
   cmake --build .
   copy video_frame_compressor.exe ..
   cd ..
   ```

2. **Option 2: Using batch script**
   ```cmd
   build_compressor.bat
   ```

3. **Option 3: Manual compilation**
   ```cmd
   g++ -o video_frame_compressor.exe video_frame_compressor.cpp -I"C:/path/to/opencv/include" -L"C:/path/to/opencv/lib" -lopencv_core -lopencv_imgcodecs -lopencv_imgproc -std=c++11
   ```

### Linux

```bash
mkdir build && cd build
cmake ..
make
cp video_frame_compressor ..
cd ..
```

Or manually:
```bash
g++ -o video_frame_compressor video_frame_compressor.cpp `pkg-config --cflags --libs opencv4` -std=c++11
```

## Usage

1. **First, generate the video** by running your fatigue detection pipeline:
   ```python
   python start_gui.py
   # Select "POPOLNA ANALIZA (VIDEO)" and process a video
   ```

2. **Compile the C++ compressor** (see Build Instructions above)

3. **Run the compression script**:
   ```bash
   python compress_video_frames.py
   ```

## Output

The script will create two directories in `output/`:

- `output/frames_extracted/` - Every 5th frame extracted as PNG
- `output/frames_compressed/` - Compressed frames as .bin files

## Compression Parameters

The default compression factor is **8** (balanced quality/size).

To change it, edit `compress_video_frames.py`:
```python
compression_factor = 8  # Change to 0-15
```

- **0** = Highest quality, lowest compression
- **8** = Balanced (recommended)
- **14** = Lowest quality, highest compression

## How It Works

1. **Frame Extraction**: Opens `output/yolo_predict.mp4` and extracts every 5th frame
2. **DCT Compression**: Each frame is:
   - Split into 8x8 blocks
   - Transformed using Discrete Cosine Transform (DCT)
   - Quantized using triangular quantization
   - Encoded using Run-Length Encoding (RLE)
3. **Storage**: Compressed frames saved as `.bin` files

## Troubleshooting

### "C++ compressor not found"
- Make sure you compiled the C++ code first
- Check that `video_frame_compressor.exe` (Windows) or `video_frame_compressor` (Linux) exists

### "Video not found"
- Run the fatigue detection pipeline first to generate `output/yolo_predict.mp4`

### OpenCV not found during compilation
- Install OpenCV and set the path in CMake or compiler flags
- Windows: Set `OpenCV_DIR` environment variable to OpenCV installation

### Compilation errors
- Ensure you have C++11 or later compiler
- Check OpenCV version compatibility (tested with OpenCV 4.x)
