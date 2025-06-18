import tkinter as tk
from PIL import Image, ImageTk
from gui import MainGUI
from gui_head_drop_live_ref import App as HeadDropApp

class StartGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Driver Fatigue Detection")
        self.geometry("900x600")
        self.configure(bg="white")
        self.resizable(False, False)

        # === LOGO ===
        try:
            logo_img = Image.open("bnbl-logo.png")
            logo_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
        except Exception:
            self.logo = None

        if self.logo:
            logo_label = tk.Label(self, image=self.logo, bg="white")
            logo_label.place(x=30, y=30)
        else:
            logo_label = tk.Label(self, text="logo\nslika", bg="white", font=("Arial", 12), width=10, height=5, relief="solid")
            logo_label.place(x=30, y=30)

        # === GLAVNO BESEDILO ===
        title = tk.Label(self, text="IZBERITE MOŽNOST", font=("Arial", 18), bg="white")
        title.place(relx=0.5, rely=0.3, anchor="center")

        # === GUMBI ===
        button_width = 40
        button_height = 2
        button_spacing = 30
        
        btn1 = tk.Button(
            self, text="POPOLNA ANALIZA (VIDEO)",
            font=("Arial", 14), bg="white", relief="solid", borderwidth=2,
            command=self.launch_main_gui, width=button_width, height=button_height
        )
        btn1.place(relx=0.5, rely=0.45, anchor="center")
        
        btn2 = tk.Button(
            self, text="ANALIZA POLOŽAJA GLAVE (KAMERA)",
            font=("Arial", 14), bg="white", relief="solid", borderwidth=2,
            command=self.launch_head_gui, width=button_width, height=button_height
        )
        btn2.place(relx=0.5, rely=0.45 + 0.15, anchor="center")  # 10 % nižje

    def launch_main_gui(self):
        self.destroy()
        MainGUI().mainloop()

    def launch_head_gui(self):
        self.destroy()
        root = tk.Tk()
        HeadDropApp(root)
        root.mainloop()

if __name__ == "__main__":
    StartGUI().mainloop()
