import tkinter as tk
from tkinter import filedialog, messagebox
import cv2, threading, os
from PIL import Image, ImageTk

from vectorisation import extract_vectors_from_video
from head_drop_detector import head_drop_analysis
from merging import puttingTogether
from mlpF import MLP
from finalOutput import save_pred_video

# ---------------- Main GUI ----------------
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Driver‑Fatigue Toolkit")
        self.geometry("1000x620")
        self.resizable(False, False)
        self.configure(bg="white")  # celotno okno belo

        # Levi placeholder (tu bomo predvajali video)
        self.canvas = tk.Label(self, bg="black", fg="white", font=("Arial", 26))
        self.canvas.place(x=20, y=20, width=600, height=580)

        # Desni panel
        panel = tk.Frame(self, bg="white")
        panel.place(x=650, y=20, width=320, height=580)

        # === Gumb Naloži video ===
        self.btn_load = tk.Button(
            panel, text="Naloži video",
            font=("Arial", 15), bg="white", relief="solid", borderwidth=2,
            command=self._select_video, width=40, height=2
        )
        self.btn_load.pack(pady=(140, 30))

        # === Status ===
        self.status = tk.StringVar(value="Izberi video …")
        tk.Label(panel, textvariable=self.status, justify="left", font=("Arial", 12), bg="white", wraplength=300).pack(anchor="w")

        # === Frame za rezultate ===
        self.result_frame = tk.LabelFrame(panel, text="Rezultati (izberi video)", font=("Arial", 12), bg="white", fg="black")
        self.result_var = tk.StringVar(value="")

        # === Gumb Nazaj na meni ===
        btn_back = tk.Button(
            self, text="Nazaj na meni",
            font=("Arial", 11), bg="white", relief="solid", borderwidth=2,
            command=self._go_back, width=20, height=1
        )
        btn_back.place(x=850, y=10, width=140, height=40)

        # Za predvajanje videa
        self.cap = None  # cv2.VideoCapture objekt

    # ------ UI helpers ------
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

            self._update_status("Head‑drop analiza …")
            head_drop_analysis(video_path)          # ustvari output/headdrop_annot.mp4

            self._update_status("Spajanje vektorjev …")
            puttingTogether()

            self._update_status("MLP napovedi …")
            MLP()

            self._update_status("Shranjevanje video_pred.mp4 …")
            final_vid = save_pred_video(video_path)

            # Ko je pipeline končan:
            self._update_status("✔ Analiza uspešno zaključena!")

            # Prikaži gumbe za izbor videa:
            self._show_result_buttons()

        except Exception as e:
            self._update_status("✖ Napaka – glej okno")
            messagebox.showerror("Napaka", str(e))

    def _update_status(self, txt):
        self.status.set(txt)
        
    def _go_back(self):
        self.destroy()
        import start_gui
        start_gui.StartGUI().mainloop()

    def _show_result_buttons(self):
        # Prikazemo frame in gumbe
        self.result_frame.place(x=0, y=400, width=300, height=150)

        videos = [
            ("YOLO Predict", "output/yolo_predict.mp4"),
            ("HeadDrop Annot", "output/headdrop_annot.mp4"),
            ("Video Pred", "output/video_pred.mp4")
        ]

        for text, path in videos:
            tk.Radiobutton(
                self.result_frame, text=text, variable=self.result_var,
                value=path, font=("Arial", 11), command=self._play_selected_video,
                bg="white", activebackground="white", selectcolor="white"
            ).pack(anchor="w", padx=10, pady=5)

    def _play_selected_video(self):
        path = self.result_var.get()
        if not os.path.exists(path):
            messagebox.showerror("Napaka", f"Video ne obstaja:\n{path}")
            return

        # Ustavi prejšnje predvajanje, če obstaja
        if self.cap:
            self.cap.release()
            self.cap = None

        # Odpri video
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            messagebox.showerror("Napaka", f"Ne morem odpreti videa:\n{path}")
            self.cap = None
            return

        self._update_video_frame()

    def _update_video_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.cap = None
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
        self.canvas.configure(image=imgtk)
        self.canvas.imgtk = imgtk

        # Loop (30ms)
        self.after(30, self._update_video_frame)

if __name__ == "__main__":
    MainGUI().mainloop()
