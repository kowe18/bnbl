import os
import shutil

# Lista svih korisničkih foldera
source_dirs = ["milos", "milos2", "sladja", "sladja2", "vedran"]

# Gde će se spajati svi podaci
target_images = "images/train"
target_labels = "labels/train"

os.makedirs(target_images, exist_ok=True)
os.makedirs(target_labels, exist_ok=True)

for person in source_dirs:
    image_dir = os.path.join(person, "images", "train")
    label_dir = os.path.join(person, "labels", "train")

    # Prefiks npr. milos_
    prefix = person + "_"

    for fname in os.listdir(image_dir):
        if fname.endswith(".jpg"):
            new_name = prefix + fname
            shutil.copy(os.path.join(image_dir, fname), os.path.join(target_images, new_name))

            txt_name = fname.replace(".jpg", ".txt")
            new_txt = prefix + txt_name
            shutil.copy(os.path.join(label_dir, txt_name), os.path.join(target_labels, new_txt))

print("✅ Dataset spojen bez duplikata imena.")