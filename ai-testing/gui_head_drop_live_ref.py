import tkinter as tk
from tkinter import Label
import cv2
import mediapipe as mp
from PIL import Image, ImageTk
import numpy as np
from utilities import compute_vertical_angle, compute_length

# ========== Inicializacija MediaPipe ==========
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# ========== Parametri sistema ==========
PITCH_THRESHOLD = 20          # kot nos-brada (pitch)
X_DIFF_THRESHOLD = 60         # vodoravni odmik čelo vs. brada
CONSEC_FRAMES = 10            # št. zaporednih frame-ov za zaznavo utrujenosti
BLINK_INTERVAL = 20           # cikli za utripanje rdeče (npr. 20 = 0.5 s pri 40 fps)

# ========== Inicializacija spremenljivk ==========
drop_counter = 0              # števec zaporednih utrujenih framov
ref_len_fore = None           # referenčna dolžina (čelo-brada)
ref_y_shift = None            # referenčni y-shift (nos - čelo)
ref_samples = []              # vzorci za dolžino (prvih 10)
ref_y_samples = []            # vzorci za y-shift (prvih 10)
blink_state = False           # za utripanje
frame_tick = 0                # števec za BLINK_INTERVAL

# ========== Obdelava slike ==========
def process_frame(frame, width, height):
    global drop_counter, ref_len_fore, ref_y_shift, ref_samples, ref_y_samples
    global blink_state, frame_tick

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    message = "Status: OK"

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # --- Ključne točke obraza ---
            pt_forehead = face_landmarks.landmark[10]   # čelo
            pt_chin    = face_landmarks.landmark[152]  # brada
            pt_nose    = face_landmarks.landmark[168]  # nos

            # --- Koordinate v pikslov ---
            x_f, y_f = int(pt_forehead.x * width), int(pt_forehead.y * height)
            x_c, y_c = int(pt_chin.x    * width), int(pt_chin.y    * height)
            x_n, y_n = int(pt_nose.x    * width), int(pt_nose.y    * height)

            # --- Izračuni kotov ---
            yaw_angle = compute_vertical_angle((x_f, y_f), (x_c, y_c))     # nagib levo-desno
            pitch_angle = compute_vertical_angle((x_n, y_n), (x_c, y_c))   # nagib naprej

            # --- Dolžina čelo-brada ---
            current_len = compute_length((x_f, y_f), (x_c, y_c))
            if ref_len_fore is None and len(ref_samples) < 10:
                ref_samples.append(current_len)
                if len(ref_samples) == 10:
                    ref_len_fore = sum(ref_samples) / len(ref_samples)    # srednja dolžina

            ratio_to_ref = current_len / ref_len_fore if ref_len_fore else 1.0

            # --- Višinska razlika nos-čelo ---
            y_shift_ratio = (y_n - y_f) / height
            if ref_y_shift is None and len(ref_y_samples) < 10:
                ref_y_samples.append(y_shift_ratio)
                if len(ref_y_samples) == 10:
                    ref_y_shift = sum(ref_y_samples) / len(ref_y_samples)

            ratio_y_shift_to_ref = y_shift_ratio / ref_y_shift if ref_y_shift else 1.0
            x_diff = abs(x_c - x_f)

            # --- Pogoji za utrujenost ---
            tired_cond = (
                ratio_to_ref < 0.80 or                     # čelo-brada skrajšanje
                x_diff > X_DIFF_THRESHOLD or              # nagib glave vstran
                pitch_angle < PITCH_THRESHOLD or          # glava navzdol
                ratio_y_shift_to_ref > 1.3                # nos se spusti glede na začetno pozicijo
            )

            # --- Posodabljanje števca ---
            if tired_cond:
                drop_counter += 1
            else:
                drop_counter = 0

            # --- Utripanje vsake X frame-ov ---
            frame_tick += 1
            if frame_tick >= BLINK_INTERVAL:
                blink_state = not blink_state
                frame_tick = 0

            # --- Če je dovolj utrujenih frame-ov, sprožimo alarm ---
            if drop_counter >= CONSEC_FRAMES:
                message = "VOZNIK UTRUJEN!"
                if blink_state:
                    overlay = frame.copy()
                    red_layer = np.full_like(frame, (0, 0, 255))
                    alpha = 0.4
                    cv2.addWeighted(red_layer, alpha, overlay, 1 - alpha, 0, overlay)
                    frame = overlay

            # --- Vizualizacija meritev ---
            cv2.line(frame, (x_f, y_f), (x_c, y_c), (0, 255, 0), 2)
            cv2.line(frame, (x_n, y_n), (x_c, y_c), (255, 0, 0), 2)
            cv2.putText(frame, f"Yaw: {yaw_angle:.1f}",     (10, 30),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, f"Pitch: {pitch_angle:.1f}", (10, 60),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, f"YShift ratio: {ratio_y_shift_to_ref:.3f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
            cv2.putText(frame, f"Length ratio: {ratio_to_ref:.3f}",    (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

    else:
        # --- Če obraz ni zaznan, štejemo kot potencialno utrujenost ---
        drop_counter += 1
        frame_tick += 1
        if frame_tick >= BLINK_INTERVAL:
            blink_state = not blink_state
            frame_tick = 0
        if drop_counter >= CONSEC_FRAMES:
            message = "VOZNIK UTRUJEN!"
            if blink_state:
                overlay = frame.copy()
                red_layer = np.full_like(frame, (0, 0, 255))
                alpha = 0.4
                cv2.addWeighted(red_layer, alpha, overlay, 1 - alpha, 0, overlay)
                frame = overlay
        else:
            message = "Obraz ni zaznan"
            cv2.putText(frame, "Obraz ni zaznan", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    return frame, message

# ========== Tkinter GUI ==========
class App:
    def __init__(self, window):
        self.window = window
        self.window.title("Zaznavanje utrujenosti – Finalna verzija")
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

# ========== Zagon aplikacije ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
