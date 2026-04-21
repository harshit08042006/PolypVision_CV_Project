import cv2
import os

IMG_DIR = "polypgen_yolo/images/train"
LBL_DIR = "polypgen_yolo/labels/train"

# Pick a sample image
img_name = os.listdir(IMG_DIR)[0]

img_path = os.path.join(IMG_DIR, img_name)
label_path = os.path.join(LBL_DIR, img_name.replace(".jpg", ".txt"))

img = cv2.imread(img_path)
h, w = img.shape[:2]

# Read label
with open(label_path, "r") as f:
    lines = f.readlines()

for line in lines:
    cls, x_center, y_center, bw, bh = map(float, line.strip().split())

    # Convert back to pixel coordinates
    x_center *= w
    y_center *= h
    bw *= w
    bh *= h

    x1 = int(x_center - bw / 2)
    y1 = int(y_center - bh / 2)
    x2 = int(x_center + bw / 2)
    y2 = int(y_center + bh / 2)

    # Draw box
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv2.putText(img, "polyp", (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

# Show image
cv2.imshow("Bounding Box Check", img)
cv2.waitKey(0)
cv2.destroyAllWindows()