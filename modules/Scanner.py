# modules/scanner.py

import cv2
from pyzbar.pyzbar import decode
import numpy as np

def decode_barcode_from_bytes(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    decoded_objects = decode(img)
    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None

class RealTimeBarcodeScanner:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def scan(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            return obj.data.decode('utf-8')
        return None

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
