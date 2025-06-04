from ultralytics import YOLO
import cv2, os, pathlib

MODEL_PATH = "bestM.pt"
CLASS_MAP  = {
    "Left_Eye":0,"Right_Eye":1,"Mouth":2,
    "Closed_Left":3,"Closed_Right":4,"Open_Mouth":5,
}

def frame_to_vector(result, class_map=CLASS_MAP):
    vec = [0]*len(class_map)
    if result.boxes is not None and result.boxes.data is not None:
        for box in result.boxes.data:
            cls = result.names[int(box[5])]
            if cls in class_map: vec[class_map[cls]] = 1
    return vec


def extract_vectors_from_video(video_path: str,
                               output_file: str = "output_vectors.txt",
                               model_path : str = MODEL_PATH,
                               conf_thres : float = 0.1):

    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    model = YOLO(model_path)
    print("✅ YOLO naložen – razredi:", model.names)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Ne morem odpreti videa: {video_path}")

    # ----- VideoWriter za anotirani posnetek -----
    os.makedirs("output", exist_ok=True)
    out_path = "output/yolo_predict.mp4"
    fourcc   = cv2.VideoWriter_fourcc(*"mp4v")
    fps      = cap.get(cv2.CAP_PROP_FPS) or 30
    w        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h        = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer   = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    frame_id = 0
    with open(output_file, "w") as f:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result = model.predict(frame, conf=conf_thres, verbose=False)[0]
            vec    = frame_to_vector(result)

            f.write(" ".join(map(str, vec)) + "\n")
            print(f"Frame {frame_id}: {vec}")
            frame_id += 1

            # shrani anotirani frame
            writer.write(result.plot())      # YOLO narise okvirje

    cap.release()
    writer.release()
    print(f"✔ Vsi vektorji zapisani v: {output_file}")
    print(f"✔ Anotirani video shranjen v: {out_path}")
    return output_file
