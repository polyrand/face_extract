#!/usr/bin/env python3

import numpy as np
import cv2

import argparse
import sys
import os

# printing help
red = '\033[91m'
end = '\033[0m'
info = '\033[33m[!]\033[0m'
que = '\033[34m[?]\033[0m'
bad = '\033[31m[-]\033[0m'
good = '\033[32m[+]\033[0m'
run = '\033[97m[~]\033[0m'


# load and resize / normalize the image
def detect_image(image_path, save_crop=False):
    image = cv2.imread(image_path)
    (h, w) = image.shape[:2] # image.shape = h, w, colors
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)) # https://www.pyimagesearch.com/2017/11/06/deep-learning-opencvs-blobfromimage-works/

    # pass the blob through the network
    print(run, f'Computing face detections... for image ==> {os.path.basename(image_path)}', end)
    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence associated with each detection
        confidence = detections[0, 0, i, 2]

        # filter out weak detections
        if confidence > args['confidence']:
            # compute x-y coordinates of the bounding box for the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype('int')

            if save_crop:
                face_roi = image[startY:endY, startX:endX]
                cv2.imwrite(f'face_{i} {os.path.basename(image_path)}', face_roi)
                print(good, f'Faces in image {os.path.basename(image_path)} saved', end)
            else:
                # draw the box with the associanted probability/confidence
                text = f'{confidence * 100}%'
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 10)
                cv2.putText(image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.45, (0, 0, 255), 2)

                # show output image
                cv2.namedWindow('image', cv2.WINDOW_NORMAL)
                cv2.imshow('Output', cv2.resize(image, (600, 600)))
                cv2.waitKey(0)
                break


def detect_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(tuple(ext)):
                detect_image(image_path=os.path.join(root, file), save_crop=True)
    print('\n', 'All Detected faces saved to current folder', '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--image',
                    help='path to input image')
    ap.add_argument('-p', '--prototxt', required=True,
                    help='path to Caffe "deploy" prototxt file')
    ap.add_argument('-m', '--model', required=True,
                    help='path to Caffe pre-trainer model')
    ap.add_argument('-c', '--confidence', type=float, default=0.5,
                    help='minimum probability to filter weak selections')
    ap.add_argument('-f', '--folder',
                    help='folder with images to extract faces from')
    args = vars(ap.parse_args())
    ext = ('.jpg', '.png', '.gif', '.tiff', '.jpeg')

    print(run, 'Loading model', end)
    print(red, f'Confidence={args["confidence"]}', end)
    # load model from disk
    net = cv2.dnn.readNetFromCaffe(args['prototxt'], args['model'])

    if args['folder'] is not None and args['image'] is None:
        detect_folder(folder=args['folder'])
    elif args['folder'] is None and args['image'] is not None:
        detect_image(image_path=args['image'])
    else:
        print(info, 'Something went wrong', end)
        sys.exit(1)
