@echo off
echo Building video frame compressor...

REM Create build directory
if not exist build mkdir build
cd build

REM Run CMake
cmake .. -G "MinGW Makefiles"
if %errorlevel% neq 0 (
    echo CMake configuration failed!
    cd ..
    exit /b 1
)

REM Build
cmake --build .
if %errorlevel% neq 0 (
    echo Build failed!
    cd ..
    exit /b 1
)

REM Copy executable to root
copy video_frame_compressor.exe ..
cd ..

echo.
echo Build successful! Executable: video_frame_compressor.exe
echo.
echo Now you can run: python compress_video_frames.py
