import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO

model = YOLO("yolov8s.pt")
#model = YOLO("runs/detect/train/weights/best.pt")


model.train(
    data="dataset.yaml",
    epochs=40,
    imgsz=640,
    device="cpu",  # "cuda" if we are using GPU
)

metrics = model.val()

# Export as ONNX format
model.export(format="onnx")

# set KMP_DUPLICATE_LIB_OK=TRUE
