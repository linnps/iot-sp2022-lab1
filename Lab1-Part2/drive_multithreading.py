from pi_video_stream import PiVideoStream
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import argparse
import cv2
import os
import time
import picar_4wd as fc

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference
from advanced_mapping import Mapping
from path_finding import Path_finding_A_star


def main_drive():
    # Start updating frames in threaded manner
    default_model_dir = 'test'
    default_model = 'traffic_signs_recognition_edgetpu.tflite'
    default_labels = 'dict.txt'
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='.tflite model path',
                        default=os.path.join(default_model_dir, default_model))
    parser.add_argument('--labels', help='label file path',
                        default=os.path.join(default_model_dir, default_labels))
    parser.add_argument('--top_k', type=int, default=1,
                        help='number of categories with highest score to display')
    parser.add_argument('--camera_idx', type=int, help='Index of which video source to use. ', default=0)
    parser.add_argument('--threshold', type=float, default=0.1,
                        help='classifier score threshold')
    args = parser.parse_args()
    # load object detection model
    print('Loading {} with {} labels.'.format(args.model, args.labels))
    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()
    labels = read_label_file(args.labels)
    inference_size = input_size(interpreter)

    # open thread for camera
    thread_stream = PiVideoStream()
    thread_stream.start()
    time.sleep(2)

    # find directions of the route
    directions = get_directions()

    # Read frames
    while True:
        # Original image
        image = thread_stream.read()
        cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, inference_size)
        run_inference(interpreter, cv2_im_rgb.tobytes())
        objs = get_objects(interpreter, args.threshold)[:args.top_k]
        cv2_im = cv2.resize(image, (300, 300))
        obj = detect_traffic_objects(cv2_im, inference_size, objs, labels)

        fc.forward(10)
        current_dir = directions[0]
        for dir in directions:
            drive_dir(current_dir, dir)
            if obj is not None:
                if labels.get(objs[0].id, objs[0].id) == "Stop_Sign":
                    fc.forward(10)
                    time.sleep(0.5)
                    print("stop sign detected.")
                    fc.stop()
                    time.sleep(3)
                if labels.get(objs[0].id, objs[0].id) == "Red_Traffic_Light":
                    fc.forward(5)
                    time.sleep(0.07)
                    print("red traffic light detected.")
                    fc.stop()
                if labels.get(objs[0].id, objs[0].id) == "Green_Traffic_Light":
                    print("green traffic light detected.")
                    fc.forward(10)
                if labels.get(objs[0].id, objs[0].id) == "Person":
                    print("pedestrian detected.")
                    fc.stop()

        # Show computed image for debug
        cv2.imshow('Preview',cv2_im)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Close image window and thread
    cv2.destroyAllWindows()
    thread_stream.stop()

def detect_traffic_objects(cv2_im, inference_size, objs, labels):
    height, width, channels = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]
    detected_obj = None
    for obj in objs:
        percent = int(100 * objs[0].score)
        if percent > 85:
            bbox = obj.bbox.scale(scale_x, scale_y)
            x0, y0 = int(bbox.xmin), int(bbox.ymin)
            x1, y1 = int(bbox.xmax), int(bbox.ymax)

            label = '{}% {}'.format(percent, labels.get(objs[0].id, objs[0].id))

            detected_obj = obj
            cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
            cv2_im = cv2.putText(cv2_im, label, (x0, y0 + 30),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

    return detected_obj

def get_directions():
    # find route based on surroundings
    clearance = 10
    starting = (51, clearance + 1)
    destination = (80, 80)
    map_width = 101
    mapping = Mapping(map_width, clearance)
    map_grid = mapping.scan()
    path_finding = Path_finding_A_star(map_grid, starting, destination, clearance)
    path = path_finding.search()

    directions = []
    for i in range(len(path) - 1):
        x = path[i][0] - path[i + 1][0]
        y = path[i][1] - path[i + 1][1]
        directions.append((x, y))

    return directions

def drive_dir(curr_dir, new_dir):
    if(curr_dir == new_dir):
        fc.forward(10)
    elif(new_dir == (0,1)):
        fc.turn_right(10)
        curr_dir = new_dir
    elif(new_dir == (1,0)):
        fc.turn_left(10)
        curr_dir = new_dir

if __name__ == "__main__":
    main_drive()