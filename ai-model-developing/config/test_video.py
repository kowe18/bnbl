# ---- TESTING MODEL USING PRERECORED VIDEOS -----

from ultralytics import YOLO

# path to best.pt
model = YOLO(r"D:\semester4\projektnipraktikum\model_1\model1.3\runs\detect\train2\weights\best.pt")

results = model.predict(
    source=r"IMG_3631.mov", # path to video used for testing
    conf=0.25,
    show=True,
    save=True
)