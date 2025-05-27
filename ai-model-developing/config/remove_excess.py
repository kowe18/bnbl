import os
import shutil

base_images = "images/train"
base_labels = "labels/train"
visak_images = "visak/images/train"
visak_labels = "visak/labels/train"

os.makedirs(visak_images, exist_ok=True)
os.makedirs(visak_labels, exist_ok=True)

all_images = sorted([f for f in os.listdir(base_images) if f.startswith(("milos", "milos2")) and f.endswith(".jpg")])

# Svaki treći (0, 3, 6, ...)
for i, fname in enumerate(all_images):
    if i % 3 == 0:
        # Slika
        src_img = os.path.join(base_images, fname)
        dst_img = os.path.join(visak_images, fname)
        shutil.move(src_img, dst_img)

        # Labela
        txt_name = fname.replace(".jpg", ".txt")
        src_lbl = os.path.join(base_labels, txt_name)
        dst_lbl = os.path.join(visak_labels, txt_name)
        if os.path.exists(src_lbl):
            shutil.move(src_lbl, dst_lbl)

print("✅ Premestio svaki treći frejm iz 'milos' i 'milos2' u 'visak/'.")
