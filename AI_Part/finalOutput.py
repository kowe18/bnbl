import cv2, csv, os, pathlib

CSV_PATH = "fatigue_predictions.csv"   # napovedi

def save_pred_video(video_path: str,
                    csv_path: str = CSV_PATH,
                    output_dir: str = "output") -> str:
    """Shrani video z alarm–overlayem; ne prikazuje v živo."""
    # ───── verjetnosti ─────
    probs = {}
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            if r["p_umoran"] == "train":
                continue
            fid = int(r["Frame"])
            probs[fid] = (float(r["p_umoran"]), float(r["p_uspavan"]))

    # ───── vhodni video ─────
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Ne morem odpreti videa: {video_path}")

    fps    = cap.get(cv2.CAP_PROP_FPS) or 30
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "video_pred.mp4")
    out_vid  = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    # ───── fuzzy parametri ─────
    TH_U_H, TH_U_L = 0.60, 0.40
    TH_S_H, TH_S_R = 0.50, 0.40
    need_mild = need_recov = int(2 * fps)
    STRONG_WIN = 4

    state = "OK"
    mild_cnt = recov_cnt = strong_win = 0
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        p_u, p_s = probs.get(frame_idx, (0.0, 0.0))

        # --- state-machine ---
        if state == "OK":
            mild_cnt = mild_cnt + 1 if p_u > TH_U_H else 0
            if mild_cnt >= need_mild:
                state, strong_win = "MILD", 0

        elif state == "MILD":
            if p_s > TH_S_H:
                state, recov_cnt = "STRONG", 0
            elif p_u < TH_U_L:
                state, mild_cnt = "OK", 0
            else:
                strong_win += 1
                if strong_win >= STRONG_WIN and p_s > 0.25:
                    state, recov_cnt = "STRONG", 0

        elif state == "STRONG":
            if p_s < TH_S_R and p_u >= TH_U_L:
                state, mild_cnt, recov_cnt = "MILD", 0, 0
            elif p_s < TH_S_R and p_u < TH_U_L:
                recov_cnt += 1
                if recov_cnt >= need_recov:
                    state = "OK"; mild_cnt = recov_cnt = 0
            else:
                recov_cnt = 0

        # --- overlay ---
        cv2.putText(frame, f"p_u={p_u:.2f} p_s={p_s:.2f}", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        if state == "MILD":
            cv2.putText(frame, "🟡 UTRUJEN – srednji alarm", (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 3)
        elif state == "STRONG":
            cv2.putText(frame, "🔴 ZASPAN – ALARM!", (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 3)
        else:
            cv2.putText(frame, "OK", (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        out_vid.write(frame)
        frame_idx += 1

    cap.release(); out_vid.release()
    print("✔ Video z napovedmi shranjen:", out_path)
    return out_path
