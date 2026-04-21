from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.pt")

    model.train(
        data="polypgen.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        device=0,
        workers=0   # important for Windows
    )

if __name__ == "__main__":
    main()