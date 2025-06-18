import tkinter as tk
from tkinter import Label
import cv2
import mediapipe as mp
from PIL import Image, ImageTk
from utilities import compute_vertical_angle, compute_length
import math

# Inicializacija MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# ================= Parametri =================
ANGLE_THRESHOLD = 15          # yaw (levo‑desno nagib)
PITCH_THRESHOLD = 20          # kot nos‑brada (pitch)
LENGTH_THRESHOLD_RATIO = 0.17 # skrajšanje čelo‑brada (pogled vstran)
X_DIFF_THRESHOLD = 60         # vodoravni odmik čelo vs. brada (roll)
Y_SHIFT_RATIO = 0.105         # 🔄 posodobljeno: nos se mora spustiti vsaj 11.5 % višine slike
CONSEC_FRAMES = 15            # zaporedni fram‑i za utrujenost
# ============================================

drop_counter = 0

# Funkcija za obdelavo frame‑a
def process_frame(frame, width, height):
    global drop_counter

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    message = "Status: OK"

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Ključne točke
            pt_forehead = face_landmarks.landmark[10]   # čelo (glabella)
            pt_chin    = face_landmarks.landmark[152]  # brada
            pt_nose    = face_landmarks.landmark[168]  # nosni vrh (središče obraza)

            x_f, y_f = int(pt_forehead.x * width), int(pt_forehead.y * height)
            x_c, y_c = int(pt_chin.x    * width), int(pt_chin.y    * height)
            x_n, y_n = int(pt_nose.x    * width), int(pt_nose.y    * height)

            # YAW kot (čelo‑brada)
            yaw_angle = compute_vertical_angle((x_f, y_f), (x_c, y_c))
            # PITCH kot (nos‑brada)
            pitch_angle = compute_vertical_angle((x_n, y_n), (x_c, y_c))

            # Normalizirana dolžina čelo‑brada
            norm_len_fore = compute_length((x_f, y_f), (x_c, y_c)) / height
            # Vodoravni odmik čelo‑brada
            x_diff = abs(x_c - x_f)
            # Navpični spust nosu pod čelo
            y_shift_ratio = (y_n - y_f) / height

            tired_cond = (
                (yaw_angle < ANGLE_THRESHOLD and norm_len_fore < LENGTH_THRESHOLD_RATIO) or  # pogled vstran
                x_diff > X_DIFF_THRESHOLD or                                               # močan roll
                pitch_angle < PITCH_THRESHOLD or                                           # glava navzdol
                y_shift_ratio > Y_SHIFT_RATIO                                              # nos se spusti precej navzdol
            )

            if tired_cond:
                drop_counter += 1
            else:
                drop_counter = 0

            if drop_counter >= CONSEC_FRAMES:
                message = "VOZNIK UTRUJEN!"

            # Vizualizacija meritev
            cv2.line(frame, (x_f, y_f), (x_c, y_c), (0, 255, 0), 2)
            cv2.line(frame, (x_n, y_n), (x_c, y_c), (255, 0, 0), 2)
            cv2.putText(frame, f"Yaw: {yaw_angle:.1f}",   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, f"Pitch: {pitch_angle:.1f}",(10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, f"dY nose: {y_shift_ratio:.3f}",(10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    return frame, message

# =================== Tkinter GUI ===================
class App:
    def __init__(self, window):
        self.window = window
        self.window.title("Zaznavanje utrujenosti voznika")
        self.video_label = Label(window)
        self.video_label.pack()

        self.status_label = Label(window, text="Status: Čakam...", font=("Arial", 16))
        self.status_label.pack()

        self.cap = cv2.VideoCapture(0)
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            h, w = frame.shape[:2]
            frame, message = process_frame(frame, w, h)
            self.status_label.config(text=message)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.window.after(10, self.update)

    def on_closing(self):
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
