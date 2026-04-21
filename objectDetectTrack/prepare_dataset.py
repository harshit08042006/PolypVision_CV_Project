from datasets import load_dataset
import os
import cv2
import numpy as np

ds = load_dataset("halyusuf/PolypGen2.0")

BASE_DIR = "polypgen_yolo"

for split in ["train", "validation"]:
    IMG_DIR = os.path.join(BASE_DIR, f"images/{split}")
    LBL_DIR = os.path.join(BASE_DIR, f"labels/{split}")

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(LBL_DIR, exist_ok=True)

    for i, sample in enumerate(ds[split]):
        image = sample["image"]
        bboxes = sample["objects"]["bbox"]

        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        h, w = img.shape[:2]

        img_name = f"{split}_{i}.jpg"
        label_name = f"{split}_{i}.txt"

        cv2.imwrite(os.path.join(IMG_DIR, img_name), img)

        with open(os.path.join(LBL_DIR, label_name), "w") as f:
            for bbox in bboxes:
                x_min, y_min, x_max, y_max = bbox

                x_center = ((x_min + x_max) / 2) / w
                y_center = ((y_min + y_max) / 2) / h
                bw = (x_max - x_min) / w
                bh = (y_max - y_min) / h

                f.write(f"0 {x_center} {y_center} {bw} {bh}\n")

print("✅ Dataset prepared!")