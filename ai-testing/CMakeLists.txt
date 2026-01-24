cmake_minimum_required(VERSION 3.10)
project(VideoFrameCompressor)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV
find_package(OpenCV REQUIRED)

# Add executable
add_executable(video_frame_compressor video_frame_compressor.cpp)

# Link OpenCV libraries
target_link_libraries(video_frame_compressor ${OpenCV_LIBS})

# Include OpenCV headers
target_include_directories(video_frame_compressor PRIVATE ${OpenCV_INCLUDE_DIRS})
