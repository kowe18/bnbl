# bnbl
 # 👥 Meet the Team

We are a team of students of Faculty of Electrical Engineering and Computer Science (UM FERI) in Maribor, Slovenia. We are researchers working on intelligent driver monitoring systems, as a project. Below are the members and contributors who helped shape this project.
<table>
  <tr>
    <td align="center" valign="top">
      <img src="images/milos.png" width="120" height="120"><br/>
      <strong>Miloš Avakumović</strong><br/>
      <a href="mailto:milos.avakumovic@student.um.si">milos.avakumovic@student.um.si</a>
    </td>
    <td align="center" valign="top">
      <img src="images/sladjana.png" width="120" height="120"><br/>
      <strong>Slađana Petrović</strong><br/>
      <a href="mailto:sladjana.petrovic1@student.um.si">sladjana.petrovic1@student.um.si</a>
    </td>
    <td align="center" valign="top">
      <img src="images/vedran.png" width="120" height="120"><br/>
      <strong>Vedran Dojčinović</strong><br/>
      <a href="mailto:vedran.dojcinovic@student.um.si">vedran.dojcinovic@student.um.si</a>
    </td>
  </tr>
</table>



  

# 🧠 Driver Fatigue Detection System

A real-time and trained computer vision system that detects signs of driver drowsiness using AI-powered facial analysis. Combining facial landmark tracking with neural object detection, our solution increases road safety by identifying head tilts, closed eyes, and yawning — before it's too late. By identifying signs of drowsiness early (e.g., head drooping, closed eyes, yawning), these systems can prevent accidents before they happen, alerting the driver or triggering automated responses.

---

## 🚗 About the Project

Driver fatigue is one of the most significant — yet preventable — contributors to road accidents worldwide. It impairs reaction time, decision-making ability, and overall driving performance. Studies show that drowsy driving can be as dangerous as driving under the influence of alcohol, with thousands of accidents and fatalities each year attributed to tired drivers.

This project aims to build a real-time driver fatigue detection system that monitors visual cues on the driver's face to recognize early signs of drowsiness or reduced attention. By analyzing the position and behavior of key facial landmarks — such as eye closure, yawning, and head movement — the system is capable of issuing timely warnings before the driver’s condition becomes dangerous.

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

