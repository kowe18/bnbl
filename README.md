# bnbl
 
# 🧠 Driver Fatigue Detection System

A real-time computer vision system that detects signs of driver drowsiness using AI-powered facial analysis. Combining facial landmark tracking with neural object detection, our solution increases road safety by identifying head tilts, closed eyes, and yawning — before it's too late.

---

## 🚗 About the Project

Driver fatigue is a critical factor in traffic accidents worldwide. Our system monitors key facial indicators to detect early signs of fatigue and alert the driver or external system. It's designed to be lightweight, real-time, and modular — ideal for prototyping smart car safety systems or research in driver monitoring.

---

## 🔍 Key Features

- 🧠 **Head Pose Analysis (MediaPipe)**  
  Calculates vertical and horizontal head orientation using forehead–chin landmark geometry.

- 👁️ **Eye & Mouth Detection (YOLOv8)**  
  Detects LeftEye, RightEye, and Mouth to monitor signs of slow eye closure or yawning.

- 📉 **Drowsiness Detection Logic**  
  Rule-based logic using angles, facial movement thresholds, and landmark shifts.

- 🖥️ **Live GUI Visualization**  
  Real-time status display showing fatigue detection overlays and alerts.

- 🔄 **MQTT Integration**  
  Sends fatigue events as messages to external systems (for vehicle automation, logging, etc.).

- 📊 **Monitoring Dashboard (Prometheus + Grafana)**  
  Tracks frame rate, memory usage, and detection statistics across the system.

---

## 🧩 Technologies Used

| Component         | Technology                |
|------------------|---------------------------|
| Neural Detection | YOLOv8 (Ultralytics)      |
| Landmark Tracking| MediaPipe FaceMesh        |
| GUI              | OpenCV + Tkinter          |
| Communication    | MQTT (Mosquitto + paho)   |
| Metrics          | Prometheus + Grafana      |
| VPN              | ZeroTier                  |

---

## 📦 Project Structure

