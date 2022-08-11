import os
import cv2
import time
import argparse
import numpy as np
from openvino.inference_engine import ie_api as ie

parser = argparse.ArgumentParser(description="Generate OpenVINO ref results for layers\n")
parser.add_argument('xml', type=str, help='Network xml/blob file')
parser.add_argument('-d', '--device', nargs='?', type=str, help='Device')
args = parser.parse_args()

model_path, model_name = os.path.split(os.path.abspath(args.xml))
bin = model_path + "/" + os.path.splitext(model_name)[0] + ".bin"

def get_depth(depth, bits=1):
    depth_min = depth.min()
    depth_max = depth.max()
    max_val = (2**(8*bits))-1

    if depth_max - depth_min > np.finfo("float").eps:
        out = max_val * (depth - depth_min) / (depth_max - depth_min)
    else:
        out = np.zeros(depth.shape, dtype=depth.type)

    if bits == 1:
        out = out.astype("uint8")
    elif bits == 2:
        out = out.astype("uint16")

    return out

# CV
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Timer
t = 0.0

# Load IE
core = ie.IECore()

net = core.read_network(model=args.xml, weights=bin)

exec_net = core.load_network(net, device_name=args.device, num_requests=1)

input_blob = next(iter(net.input_info))
out_blob = next(iter(net.outputs))
input_info = exec_net.input_info
assert (len(input_info) == 1)
input_name = next(iter(input_info))

# Get model input shape
n, c, h, w = input_info[input_name].input_data.shape
print(f"Network input size: {n} x {c} x {h} x {w}")

mean = [123.675, 116.28, 103.53]
std = [58.395, 57.12, 57.375]

while(True):
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    image = cv2.resize(frame, (w, h), interpolation=cv2.INTER_CUBIC)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # BGR to RGB
    # image = image.astype('float32')
    image = (image.astype('float32') - mean) / std
    image = image.transpose((2, 0, 1))

    start = time.perf_counter()
    # Inference
    req = exec_net.requests[0]
    req.infer(inputs={input_blob: image})
    end = (time.perf_counter() - start) * 1000
    t += end
    print('\rInference times: %.2f ms' % end, end='')

    ori_width = frame.shape[1]
    ori_height = frame.shape[0]

    res = req.output_blobs
    output_data = res[next(iter(res))].buffer.squeeze()
    output_data = cv2.resize(output_data, (ori_width, ori_height), interpolation=cv2.INTER_CUBIC)
    depth = get_depth(output_data, 1)

    cv2.imshow("DetectionResults", depth)

    # ESC key
    key = cv2.waitKey(1)
    if key == 27:
        break

print(f"\nAverage inference time: {t:.2f}ms\n")