import torch
import torch.nn.functional as F
import numpy as np
import os, argparse
from lib.pvt import PolypPVT
import cv2
import torchvision.transforms as transforms
from PIL import Image

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_video', type=str, required=True, help='Path to the input video')
    parser.add_argument('--output_video', type=str, required=True, help='Path to save the output video')
    parser.add_argument('--pth_path', type=str, default='./model_pth/PolypPVT.pth', help='Model weights path')
    parser.add_argument('--testsize', type=int, default=352, help='Model input size')
    return parser.parse_args()

def main():
    opt = get_args()
    
    # 1. Load model
    print(f"Loading model from {opt.pth_path}")
    model = PolypPVT()
    if os.path.exists(opt.pth_path):
        model.load_state_dict(torch.load(opt.pth_path, map_location='cpu'))
    else:
        print(f"WARNING: Model weights not found at {opt.pth_path}. Attempting to run anyway, but results will be randomly initialized unless weights are present.")
        
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    
    # 2. Setup preprocessing
    transform = transforms.Compose([
        transforms.Resize((opt.testsize, opt.testsize)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    
    # 3. Video Capture
    cap = cv2.VideoCapture(opt.input_video)
    if not cap.isOpened():
        raise IOError(f"Cannot open video {opt.input_video}")
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video Info: {width}x{height} @ {fps}fps, Total Frames: {total_frames}")
    
    # Use XVID - most compatible software encoder on Linux
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(opt.output_video, fourcc, fps, (width, height))
    
    frame_idx = 0
    with torch.no_grad():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_idx += 1
            if frame_idx % 10 == 0:
                print(f"Processing frame {frame_idx}/{total_frames}")
                
            # OpenCV provides BGR, convert to RGB for PIL & model
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            
            # Preprocess
            input_tensor = transform(pil_img).unsqueeze(0).to(device)
            
            # Predict
            P1, P2 = model(input_tensor)
            
            # Postprocess mask
            # The model outputs a multi-layer tensor, sum them before upsampling
            res = F.interpolate(P1+P2, size=(height, width), mode='bilinear', align_corners=False)
            res = res.sigmoid().data.cpu().numpy().squeeze()
            
            # Normalize
            if res.max() > res.min():
                res = (res - res.min()) / (res.max() - res.min() + 1e-8)
            else:
                res = np.zeros_like(res)
                
            # Create overlay (green mask on polyp, semi-transparent)
            # Use res as an alpha mask to blend between the original frame and a green tint
            green_overlay = np.zeros_like(frame)
            green_overlay[:, :] = [0, 255, 0] # BGR format: Green
            
            # Stack alpha channel to match the color dimensions (H, W, 3)
            alpha = np.stack([res]*3, axis=2) 
            
            # Blend: original_frame * (1 - alpha * 0.5) + green_overlay * (alpha * 0.5)
            # Setting 0.5 gives the polyp mask a semi-transparent look
            blended = frame.astype(np.float32) * (1 - alpha * 0.5) + green_overlay.astype(np.float32) * (alpha * 0.5)
            blended_frame = blended.astype(np.uint8)
            
            # Write the resulting frame into the output video
            out.write(blended_frame)
            
    cap.release()
    out.release()
    print(f"Video inference completed. Saved output to: {opt.output_video}")

if __name__ == '__main__':
    main()
