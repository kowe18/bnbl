# ---- TESTING MODEL USING PRERECORED VIDEOS -----

from ultralytics import YOLO

# path to best.pt
model = YOLO(r"D:\semester4\projektnipraktikum\model_1\m_1_milos_o\runs\detect\train\weights\best.pt")

results = model.predict(
    source=r"ezgif-44b37d4e0bbe0c.mov", # path to video used for testing
    conf=0.25,
    show=True,
    save=True
)