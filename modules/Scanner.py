from pyzbar.pyzbar import decode
import cv2
import numpy as np

def decode_barcode_from_bytes(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    barcodes = decode(img)
    if barcodes:
        return barcodes[0].data.decode("utf-8")
    return None

def RealTimeBarcodeScanner():
    cap = cv2.VideoCapture(0)
    barcode_data = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        decoded = decode(frame)
        for obj in decoded:
            barcode_data = obj.data.decode("utf-8")
            cap.release()
            return barcode_data
        cv2.imshow("Scan Barcode", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return barcode_data
