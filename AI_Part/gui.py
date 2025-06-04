import tkinter as tk
from tkinter import filedialog, messagebox
import cv2, threading, os
from PIL import Image, ImageTk

from vektorizacija import extract_vectors_from_video
from head_drop_detector import head_drop_analysis
from spajanje import puttingTogether
from mlpF import MLP
from finalOutput import save_pred_video

# ---------------- VideoPlayer ----------------
class VideoPlayer(tk.Toplevel):
    def __init__(self, master, video_path):
        super().__init__(master)
        self.title(os.path.basename(video_path))
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Napaka", f"Ne morem odpreti videa:\n{video_path}")
            self.destroy(); return

        self.label = tk.Label(self, bg="black")
        self.label.pack(expand=True, fill="both")
        self.running = True
        self.after(10, self._update)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _update(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if not ret:
            self._close(); return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
        self.label.configure(image=imgtk)
        self.label.imgtk = imgtk
        self.after(20, self._update)

    def _close(self):
        if self.running:
            self.running = False
            self.cap.release()
        self.destroy()

# ---------------- Main GUI ----------------
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Driver‑Fatigue Toolkit")
        self.geometry("1000x620")
        self.resizable(False, False)

        # Levi placeholder
        self.canvas = tk.Label(self, text="VIDEO", bg="black", fg="white", font=("Arial", 26))
        self.canvas.place(x=20, y=20, width=600, height=580)

        # Desni panel
        panel = tk.Frame(self)
        panel.place(x=650, y=20, width=320, height=580)

        self.mode = tk.StringVar(value="")
        tk.Radiobutton(panel, text="Proces", variable=self.mode, value="proces", font=("Arial", 15), command=self._enable_btn).pack(anchor="w", pady=(15, 5))
        tk.Radiobutton(panel, text="Final", variable=self.mode, value="final", font=("Arial", 15), command=self._enable_btn).pack(anchor="w")

        self.btn_load = tk.Button(panel, text="Naloži video", font=("Arial", 13), state="disabled", command=self._select_video)
        self.btn_load.pack(pady=(30, 30))

        self.status = tk.StringVar(value="Izberi način in nato video …")
        tk.Label(panel, textvariable=self.status, justify="left", font=("Arial", 12), wraplength=300).pack(anchor="w")

    # ------ UI helpers ------
    def _enable_btn(self):
        self.btn_load.config(state="normal")

    def _select_video(self):
        path = filedialog.askopenfilename(title="Video", filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv"), ("All", "*.*")])
        if not path:
            return
        threading.Thread(target=self._pipeline, args=(path,), daemon=True).start()

    # ------ pipeline ------
    def _pipeline(self, video_path):
        try:
            base = os.path.basename(video_path)
            self._update_status(f"Vektorizacija ({base}) …")
            extract_vectors_from_video(video_path)  # ustvari output/yolo_predict.mp4

            if self.mode.get() == "proces":
                self._update_status("Pregled YOLO predikcij …")
                vp = VideoPlayer(self, "output/yolo_predict.mp4")
                self.wait_window(vp)

            self._update_status("Head‑drop analiza …")
            head_drop_analysis(video_path)          # ustvari output/headdrop_annot.mp4

            if self.mode.get() == "proces":
                self._update_status("Pregled Head‑drop videa …")
                vp2 = VideoPlayer(self, "output/headdrop_annot.mp4")
                self.wait_window(vp2)

            self._update_status("Spajanje vektorjev …")
            puttingTogether()

            self._update_status("MLP napovedi …")
            MLP()

            self._update_status("Shranjevanje video_pred.mp4 …")
            final_vid = save_pred_video(video_path)

            self._update_status("✔ Končano – predvajam rezultat")
            self.after(100, lambda: VideoPlayer(self, final_vid))

        except Exception as e:
            self._update_status("✖ Napaka – glej okno")
            messagebox.showerror("Napaka", str(e))

    def _update_status(self, txt):
        self.status.set(txt)

if __name__ == "__main__":
    MainGUI().mainloop()
