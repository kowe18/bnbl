import cv2, os, csv
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

def head_drop_analysis(video_path: str):
    """Analiziraj nagib glave za podan video.
    Shrani anotirani posnetek v output/headdrop_annot.mp4 in CSV‑log.
    Ne prikazuje v živo.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)

    os.makedirs("output", exist_ok=True)
    out_vid_path = "output/headdrop_annot.mp4"
    log_path     = "output/headdrop_log.csv"

    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Ne morem odpreti videa: {video_path}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30
    w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(out_vid_path, fourcc, fps, (w, h))

    with open(log_path, "w", newline="") as lf:
        csvw = csv.writer(lf)
        csvw.writerow(["frame", "brada_Y_ratio", "x_diff", "is_tired", "direction"])

        y_thr, x_thr, consec = 0.10, 80, 15
        ref_y = None; drop = 0; idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = face_mesh.process(rgb)
            is_tired = False; dir_txt = "OK"; y_ratio = 0; x_diff = 0

            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0]
                pt_f = lm.landmark[10]; pt_c = lm.landmark[152]
                x_f, y_f = int(pt_f.x*w), int(pt_f.y*h)
                x_c, y_c = int(pt_c.x*w), int(pt_c.y*h)

                if ref_y is None and idx < 10: ref_y = y_c
                if ref_y: y_ratio = (y_c - ref_y) / ref_y
                x_diff = abs(x_c - x_f)

                if x_f - x_c > x_thr:       dir_txt = "levo"
                elif x_c - x_f > x_thr:     dir_txt = "desno"
                elif y_ratio > y_thr:       dir_txt = "navzdol"

                if y_ratio > y_thr or x_diff > x_thr:
                    drop += 1
                else:
                    drop = 0
            else:
                drop += 1; dir_txt = "Obraz ni viden"

            if drop >= consec: is_tired = True

            cv2.putText(frame, f"Smer: {dir_txt}", (30,40), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,200),2)
            cv2.putText(frame, f"Drop Counter: {drop}", (30,70), cv2.FONT_HERSHEY_SIMPLEX,0.7,(200,255,200),2)
            if is_tired:
                cv2.putText(frame, "VOZNIK UTRUJEN!", (30,110), cv2.FONT_HERSHEY_SIMPLEX,1.2,(0,0,255),3)

            csvw.writerow([idx, f"{y_ratio:.3f}" if ref_y else "NA", f"{x_diff:.1f}", int(is_tired), dir_txt])
            writer.write(frame)
            idx += 1

    cap.release(); writer.release()
    print("✔ Zaključeno →", out_vid_path)
    return out_vid_path, log_path
