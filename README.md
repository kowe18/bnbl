# bnbl
 # 👥 Meet the Team

We are a team of students of Faculty of Electrical Engineering and Computer Science (UM FERI) in Maribor, Slovenia. We are researchers working on intelligent driver monitoring systems, as a project. Below are the members and contributors who helped shape this project.
<table border="0">
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

A real-time and trained computer vision system that detects signs of driver drowsiness using AI-powered facial analysis. Combining facial landmark tracking with neural object detection, our solution increases road safety by identifying head tilts, closed eyes, and yawning, before it becomes dangerous. By identifying signs of drowsiness early (e.g., head drooping, closed eyes, yawning), these systems can prevent accidents before they happen, alerting the driver or triggering automated responses.

---

## 🚗 About the Project

Driver fatigue is one of the most significant contributors to road accidents worldwide. It impairs reaction time, decision-making ability, and overall driving performance. Studies show that drowsy driving can be as dangerous as driving under the influence of alcohol, with thousands of accidents and fatalities each year attributed to tired drivers.

This project aims to build a real-time driver fatigue detection system that monitors visual cues on the driver's face to recognize early signs of drowsiness or reduced attention. By analyzing the position and behavior of key facial landmarks as eye closure, yawning, and head movement - the system is capable of issuing timely warnings before the driver’s condition becomes dangerous.

---

## 🔍 Key Features

- 🧠 **Head Pose Analysis (MediaPipe)**  
  Calculates vertical and horizontal head orientation using forehead–chin landmark geometry.

- 👁️ **Eye & Mouth Detection (YOLOv8)**  
  Detects LeftEye, RightEye, and Mouth to monitor signs of slow eye closure or yawning.

- 📉 **Drowsiness Detection Logic**  
  Rule-based logic using angles, facial movement thresholds, and landmark shifts.

- 🧩 **Multi-Modal Vectorization Model** 
  Collect, normalize, and structure the outputs from different subsystems into a single feature vector per frame.

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
| Communication    | MQTT (Mosquitto)   |
| Metrics          | Prometheus + Grafana      |
| VPN              | ZeroTier                  |

---

## 📦 Manual

## 📂 Project Structure

```
.
├── start_gui.py                  # Entry point – main menu with two modes
├── gui.py                        # Full video analysis (YOLO + head detection + MLP)
├── gui_head_drop_live_ref.py    # Real-time head drop detection from webcam
├── vectorisation.py             # Feature extraction from YOLO
├── head_drop_detector.py        # Head angle analysis on video
├── mlpF.py                      # Loads trained MLP model for prediction
├── finalOutput.py               # Merges analysis results into output video
├── merging.py                   # Combines predictions from multiple models
├── utilities.py                 # Math functions for angles, distances, etc.
├── environment.yml              # Conda environment file for installing dependencies
├── output/                      # Folder where analyzed videos are saved
└── README.md                    # Project overview
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/bnbl-fatigue-detector.git
cd bnbl-fatigue-detector
```

### 2. Create and activate environment

```bash
conda env create -f environment.yml
conda activate bnbl-fatigue-detector
```

### 3. Launch the application

```bash
python start_gui.py
```

---

## 🖥️ Application Modes

### 🦚 Mode 1: Full Video Analysis

- From the main menu, select **"Full Analysis"**
- Upload a video of the driver
- The system runs:
  - YOLO object detection
  - Head angle estimation
  - MLP fatigue classification
- After analysis, select which result video to preview:
  - `video_pred.mp4` – MLP fatigue detection overlay
  - `yolo_predict.mp4` – bounding boxes from YOLO
  - `headdrop_annot.mp4` – head drop angle visualization

### 🎥 Mode 2: Real-time Head Drop Detection

- From the main menu, select **"Head Position Monitor"**
- The webcam feed opens
- Head position is tracked using MediaPipe
- If fatigue (head drop) is detected:
  - A red flashing screen will blink
  - Status changes to `"DRIVER TIRED!"`

---

## 🧠 Machine Learning Models

- MLP model is pre-trained and loaded from disk (`mlpF.py`)
- YOLO model is loaded via Ultralytics
- No training required for end-users
- If you want to train your own model, use `mlpNN.py` (not included in production environment)

---

## 📦 Dependencies

All dependencies are managed via `environment.yml`, including:

- `opencv`
- `mediapipe`
- `pillow`
- `numpy`
- `scikit-learn`
- `ultralytics`
- `joblib`

Use:

```bash
conda env create -f environment.yml
```

---

## 🧪 Output Videos

After analysis, you’ll find these files in the `output/` directory:

| File                 | Description                          |
| -------------------- | ------------------------------------ |
| `video_pred.mp4`     | Final fatigue classification overlay |
| `yolo_predict.mp4`   | Object detection via YOLO            |
| `headdrop_annot.mp4` | Visualization of head movement       |

---

## 🧑‍💻 Developer Notes

- `main` branch contains the final deployable version.
- `feature/`, `devel/`, and `final/` branches are for historical development.
- GUI is built using Tkinter and PIL.
- The logic is modular – each step of the pipeline is encapsulated.

---

## ❓ FAQ

**Q: How can I test with my own webcam?**\
A: Launch `start_gui.py`, choose "Head Position Monitor" mode.

**Q: Will this work on macOS/Linux?**\
A: Yes, as long as your webcam is accessible and you use the Conda environment.

**Q: Can I use my own MLP model?**\
A: Yes, replace the file in `mlpF.py` with your custom `.joblib` model.

---

## 🤝 Contributors

This project was developed as part of a student project at **Fakulteta za elektrotehniko, računalništvo in informatiko FERI, Maribor**.\
Special thanks to all contributors, our mentor Borko Bošković, and reviewers.
