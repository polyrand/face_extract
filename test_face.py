#!/usr/bin/env python3

import numpy as np
import cv2

import argparse
import sys
import os
import matplotlib.pyplot as plt

# colors
white = '\033[97m'
green = '\033[92m'
red = '\033[91m'
yellow = '\033[93m'
end = '\033[0m'
back = '\033[7;91m'
info = '\033[33m[!]\033[0m'
que = '\033[34m[?]\033[0m'
bad = '\033[31m[-]\033[0m'
good = '\033[32m[+]\033[0m'
run = '\033[97m[~]\033[0m'

net = cv2.dnn.readNetFromCaffe(f'{os.getcwd()}/deploy.prototxt.txt', f'{os.getcwd()}/res10_300x300_ssd_iter_140000.caffemodel')


image_path = f'{os.getcwd()}/input/test.jpg'
# load and resize / normalize the image
image = cv2.imread(image_path)
plt.imshow(image)
#image = cv2.imread(img)
(h, w) = image.shape[:2] # image.shape = h, w, colors
print("h ===", h)
print("w ===", w)
blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)) # https://www.pyimagesearch.com/2017/11/06/deep-learning-opencvs-blobfromimage-works/

# pass the blob through the network
print(run, green, f"Computing face detections... for image ==> {os.path.basename(image_path)}")
net.setInput(blob)
detections = net.forward()

detections.shape
detections[0, 0, 1, 2]
a = detections[0, 0, 1, 3:7]
b = np.array([w, h, w, h])
print(a, '\n', '\n', b)
mult = a * b
print(mult)
mult_int = mult.astype('int')
print(mult_int)

save_crop = True
# loop over the detections
for i in range(0, detections.shape[2]):
    # extract the confidence associated with each detection
    confidence = detections[0, 0, i, 2]

    # filter out weak detections
    if confidence > 0.5:
        # compute x-y coordinates of the bounding box for the object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        if save_crop:
            face_roi = image[startY:endY, startX:endX]
            cv2.imwrite(f'face_{i} {os.path.basename(image_path)}', face_roi)
            print('img saved')




    # show output image
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.imshow("Output", cv2.resize(image, (600, 600)))
    cv2.waitKey(0)


def detect_folder(folder):
    print('starting')
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(tuple(ext)):
                print('saving image')
                detect_image(image_path=os.path.join(root, file), save_crop=True)
    print('DONE!!!!')

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image",
        help="path to input image")
    ap.add_argument("-p", "--prototxt", required=True,
        help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", required=True,
        help="path to Caffe pre-trainer model")
    ap.add_argument("-c", "--confidence", type=float, default=0.5,
        help="minimum probability to filter weak selections")
    ap.add_argument("-f", "--folder",
        help="minimum probability to filter weak selections")
    args = vars(ap.parse_args())
    ext = (".jpg", ".png", ".gif", ".tiff", ".jpeg")

    print(run, green, "Loading model", end)
    print(red, f'Confidence={args["confidence"]}', end)
    # load model from disk
    net = cv2.dnn.readNetFromCaffe(r'/Users/r/Projects/Python/opencv/Crash_Course/face_extractor/deploy.prototxt.txt', r'/Users/r/Projects/Python/opencv/Crash_Course/face_extractor/res10_300x300_ssd_iter_140000.caffemodel')
    print(args)
    if args['folder'] is not None and args['image'] is None:
        detect_folder(folder=args['folder'])
    elif args['folder'] is None and args['image'] is not None:
        detect_image(image_path=args['image'])
    else:
        print('Bye')
        sys.exit(1)
