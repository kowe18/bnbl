import os
import cv2

# === PODEŠAVANJE ===
root_dir = "."  # stavi "." ako pokrećeš skriptu iz foldera gde su videi
video_ext = ".mov"

# === NAĐI SVE VIDEO FAJLOVE ===
mov_files = [f for f in os.listdir(root_dir) if f.endswith(video_ext)]

for mov_file in mov_files:
    video_path = os.path.join(root_dir, mov_file)
    video_name = os.path.splitext(mov_file)[0]

    # === KREIRAJ OUTPUT STRUKTURU ===
    output_dir = os.path.join(root_dir, video_name, "images", "train")
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Ne mogu otvoriti {mov_file}")
        continue

    print(f"🎞️ Obrađujem: {mov_file}")
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        #frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        filename = f"frame_{frame_id:06d}.jpg"
        cv2.imwrite(os.path.join(output_dir, filename), frame)
        frame_id += 1

    cap.release()
    print(f"✅ {frame_id} frejmova izvučeno u: {output_dir}")
