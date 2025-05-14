from ultralytics import YOLO

model = YOLO("yolov8m.pt")

model.train(
    data="dataset.yaml",
    epochs=10,
    imgsz=640,
    device="cpu"  # "cuda" if we are using GPU
)

metrics = model.val()

# Predict (detect) objects in images/train (source can be file, folder, URL, camera...)
results = model.predict(
    source="images/train",
    show=True,
    save=True,
    conf=0.25
)

# Export as ONNX format
model.export(format="onnx")
