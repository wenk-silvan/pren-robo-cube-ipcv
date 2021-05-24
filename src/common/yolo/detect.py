import argparse
import time
import numpy as np

import pyttsx3
import cv2
import torch

from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords
from utils.plots import colors, plot_one_box


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):

    '''
    From original yolo v5 repository
    '''
    # Resize and pad image while meeting stride-multiple constraints
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)


def detect():
    # Configuration
    weights = './weights/brick.pt'
    device = 'cpu'
    imgsz = 640
    conf_thres = 0.6
    iou_thres = 0.45
    save_img = True

    in_image_path = "./data/base.jpg"
    out_image_path = './data/outimage.jpg'

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names

    print("image size = {} and stride = {}\n".format(imgsz, stride))

    # Load Image
    cam = cv2.VideoCapture(0)
    cam.set(3, 1280)
    cam.set(4, 960)

    ret, im0s = cam.read()
    # Flip Horizontally + Vertically
    im0s = cv2.flip(im0s, -1)

    # For testing purpose
    im0s = cv2.imread(in_image_path)  # 1280 x 960
    print("img shape: {}".format(im0s.shape))
    img = letterbox(im0s, imgsz, stride)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    # Run inference
    t0 = time.time()
    img = torch.from_numpy(img).to(device)
    img = img.float()
    img /= 255.0  # 0 - 255 to 0.0 - 1.0

    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    pred = model(img, augment=False)[0]

    # Apply NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes=0, agnostic=None)

    coordinates = []

    # Process detections
    for i, det in enumerate(pred):  # detections per image

        s, p, im0, frame = "image", "./", im0s.copy(), 0
        s += '%gx%g ' % img.shape[2:]  # print string
        gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        imc = im0  # for opt.save_crop
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

            # Write results
            for *xyxy, conf, cls in reversed(det):

                # Print Box coordinates
                c1, c2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
                coordinates.append([c1, c2])
                print("Found corners: [{},{}]".format(c1, c2))

                if save_img:  # Add bbox to image
                    c = int(cls)  # integer class
                    label = f'{names[c]} {conf:.2f}'
                    plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_thickness=3)

        # Save results (image with detections)
        if save_img:
            cv2.imwrite(out_image_path, im0)

    print(f'\nDone. in {time.time() - t0:.3f}s')
    print(f'Found {len(coordinates)} Objects with coordinates: {coordinates}')
    return coordinates


if __name__ == '__main__':
    detect()
