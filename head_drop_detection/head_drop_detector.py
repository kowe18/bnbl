import cv2
import mediapipe as mp
import os
import math
import csv

def compute_vertical_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle  # ohranimo smer

def compute_length(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

video_path = "input/IMG_3647.mov"
output_path = "output/out.mp4"
log_path = "output/utrujenost_smer_log.csv"
os.makedirs("output", exist_ok=True)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"Ne morem odpreti videa: {video_path}")

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# === CSV log ===
log_file = open(log_path, "w", newline="")
csv_writer = csv.writer(log_file)
csv_writer.writerow(["frame", "angle", "angle_from_vertical", "length", "x_diff", "is_tired", "direction"])

# === Parametri ===
angle_threshold = 25
length_threshold_ratio = 0.20
x_shift_threshold = 80
required_consecutive_frames = 15

frame_index = 0
drop_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    is_tired = False
    direction = ""

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            pt1 = face_landmarks.landmark[10]  # čelo
            pt2 = face_landmarks.landmark[152] # brada

            x1, y1 = int(pt1.x * width), int(pt1.y * height)
            x2, y2 = int(pt2.x * width), int(pt2.y * height)

            angle = compute_vertical_angle((x1, y1), (x2, y2))
            angle_from_vertical = abs(90 - abs(angle))
            length = compute_length((x1, y1), (x2, y2))
            norm_length = length / height
            x_diff = abs(x2 - x1)

            # Smer pada glave
            if angle_from_vertical < angle_threshold and norm_length < length_threshold_ratio:
                direction = "naprej"
            elif x1 - x2 > x_shift_threshold:
                direction = "levo"
            elif x2 - x1 > x_shift_threshold:
                direction = "desno"

            # Glavni pogoj za utrujenost
            if (angle_from_vertical < angle_threshold and norm_length < length_threshold_ratio) or x_diff > x_shift_threshold:
                drop_counter += 1
            else:
                drop_counter = 0

            if drop_counter >= required_consecutive_frames:
                is_tired = True

            # === Vizualizacija ===
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, f"Angle: {angle:.1f}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Vert.Angle: {angle_from_vertical:.1f}", (30, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 255, 200), 2)
            cv2.putText(frame, f"Length: {norm_length:.2f}", (30, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Smer: {direction}", (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2)

            if is_tired:
                cv2.putText(frame, "VOZNIK UTRUJEN!", (30, 170),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            # Log zapis
            csv_writer.writerow([
                frame_index,
                f"{angle:.2f}",
                f"{angle_from_vertical:.2f}",
                f"{norm_length:.3f}",
                f"{x_diff:.1f}",
                int(is_tired),
                direction
            ])

    out.write(frame)
    cv2.imshow("Detekcija utrujenosti", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

    frame_index += 1

cap.release()
out.release()
log_file.close()
cv2.destroyAllWindows()
