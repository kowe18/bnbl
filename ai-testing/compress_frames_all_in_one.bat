@echo off
echo ========================================
echo VIDEO FRAME COMPRESSION - ALL IN ONE
echo ========================================
echo.

REM Step 1: Check if video exists
echo [1/4] Checking for video file...
if not exist "output\yolo_predict.mp4" (
    echo ERROR: Video not found: output\yolo_predict.mp4
    echo Please run the fatigue detection pipeline first.
    pause
    exit /b 1
)
echo OK: Video found
echo.

REM Step 2: Check if executable exists, if not compile
echo [2/4] Checking C++ compressor...
if not exist "video_frame_compressor.exe" (
    echo Compressor not found. Compiling...
    call build_compressor.bat
    if %errorlevel% neq 0 (
        echo ERROR: Compilation failed!
        pause
        exit /b 1
    )
) else (
    echo OK: Compressor already compiled
)
echo.

REM Step 3: Run test
echo [3/4] Running setup test...
python test_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Setup test failed!
    echo Please fix the issues above.
    pause
    exit /b 1
)
echo.

REM Step 4: Run compression
echo [4/4] Starting compression...
echo.
python compress_video_frames.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Compression failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Compression completed.
echo ========================================
echo.
echo Results saved to:
echo   - output\frames_extracted\
echo   - output\frames_compressed\
echo.
pause
