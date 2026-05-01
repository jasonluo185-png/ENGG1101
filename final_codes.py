import cv2
import torch

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)

# Set confidence threshold
model.conf = 0.3

# Find phone class ID
phone_ids = []
for i, name in model.names.items():
    if "phone" in name.lower():
        phone_ids.append(i)

print("Phone class IDs:", phone_ids)

# Open camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip image (optional)
    frame = cv2.flip(frame, 1)

    # Run YOLO
    results = model(frame, size=320)
    detections = results.pandas().xyxy[0]

    # Loop through detections
    for _, det in detections.iterrows():
        if det['class'] in phone_ids and det['confidence'] > 0.4:

            x1, y1, x2, y2 = map(int, [det['xmin'], det['ymin'], det['xmax'], det['ymax']])

            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

            # Label
            label = f"Phone {det['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    # Show frame
    cv2.imshow("Phone Detection", frame)

    # Quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()








*****complete

import cv2
import torch
import time
from adafruit_servokit import ServoKit

# ---------------- SERVO SETUP ----------------
kit = ServoKit(channels=16)

# SG90 tuning (important)
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)

# Start at center
pan_angle = 90   # horizontal
tilt_angle = 90  # vertical

kit.servo[0].angle = pan_angle
kit.servo[1].angle = tilt_angle

# Sensitivity (tune this!)
STEP = 1

# ---------------- YOLO SETUP ----------------
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
model.conf = 0.3

# Find phone class ID
phone_ids = []
for i, name in model.names.items():
    if "phone" in name.lower():
        phone_ids.append(i)

print("Phone class IDs:", phone_ids)

# Camera
cap = cv2.VideoCapture(0)

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape
    center_x = w // 2
    center_y = h // 2

    # Draw center point
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

    results = model(frame, size=320)
    detections = results.pandas().xyxy[0]

    for _, det in detections.iterrows():
        if det['class'] in phone_ids and det['confidence'] > 0.4:

            x1, y1, x2, y2 = map(int, [det['xmin'], det['ymin'], det['xmax'], det['ymax']])

            # Box center
            obj_x = (x1 + x2) // 2
            obj_y = (y1 + y2) // 2

            # Draw box + center
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.circle(frame, (obj_x, obj_y), 5, (255, 0, 0), -1)

            # Error (difference from center)
            error_x = obj_x - center_x
            error_y = obj_y - center_y

            # -------- SERVO CONTROL --------
            # Horizontal (servo 0)
            if abs(error_x) > 20:
                if error_x > 0:
                    pan_angle += STEP
                else:
                    pan_angle -= STEP

            # Vertical (servo 1)
            if abs(error_y) > 20:
                if error_y > 0:
                    tilt_angle -= STEP
                else:
                    tilt_angle += STEP

            # Clamp angles (IMPORTANT)
            pan_angle = max(0, min(180, pan_angle))
            tilt_angle = max(0, min(180, tilt_angle))

            # Move servos
            kit.servo[0].angle = pan_angle
            kit.servo[1].angle = tilt_angle

            # Label
            label = f"Phone {det['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

            break  # track only one phone

    cv2.imshow("Phone Tracking", frame)

    # Quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
