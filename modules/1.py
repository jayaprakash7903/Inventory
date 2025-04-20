import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
import time  # <-- This was missing

class EAN13Scanner:
    def __init__(self, camera_index=0):
        """
        Initialize EAN-13 barcode scanner.
        
        Args:
            camera_index (int): Camera device index (default: 0)
        """
        self.camera_index = camera_index
        self.cap = None
        self.last_barcode = None
        self.scanning = False

    def start(self):
        """Initialize camera with optimized settings for EAN-13 scanning."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera!")
        
        # Optimized settings for EAN-13 scanning
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Higher width helps with EAN-13
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus for stability
        self.cap.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS for better exposure
        
        self.scanning = True
        print("EAN-13 Scanner ready. Press 'Q' to quit.")

    def stop(self):
        """Release camera resources."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self.scanning = False

    def preprocess_frame(self, frame):
        """
        Optimize frame for EAN-13 detection.
        - Convert to grayscale
        - Apply adaptive thresholding
        - Sharpen image
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding works well for EAN-13
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Sharpening kernel
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(thresh, -1, kernel)
        
        return sharpened

    def find_ean13(self, frame):
        """Detect EAN-13 barcodes in a frame."""
        processed = self.preprocess_frame(frame)
        barcodes = decode(processed, symbols=[ZBarSymbol.EAN13])
        
        if barcodes:
            return barcodes[0].data.decode('utf-8')
        return None

    def scan(self, timeout=10):
        """
        Scan for EAN-13 barcode with timeout.
        
        Args:
            timeout (int): Maximum scanning time in seconds
            
        Returns:
            str: Detected EAN-13 barcode or None
        """
        self.start()
        start_time = time.time()
        
        while self.scanning and (time.time() - start_time) < timeout:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Focus on center region where barcodes are typically placed
            h, w = frame.shape[:2]
            roi = frame[int(h*0.3):int(h*0.7), int(w*0.2):int(w*0.8)]
            
            # Detect EAN-13
            barcode = self.find_ean13(roi)
            
            # Visual feedback
            cv2.rectangle(frame, 
                         (int(w*0.2), int(h*0.3)),
                         (int(w*0.8), int(h*0.7)),
                         (0, 255, 0), 2)
            
            if barcode:
                cv2.putText(frame, f"EAN-13: {barcode}", 
                           (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2)
                self.last_barcode = barcode
                self.stop()
                return barcode
            else:
                cv2.putText(frame, "Scanning for EAN-13...", 
                           (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 0, 255), 2)
            
            cv2.imshow("EAN-13 Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.stop()
        return self.last_barcode

# Example Usage
if __name__ == "__main__":
    scanner = EAN13Scanner()
    
    try:
        print("Scan an EAN-13 barcode...")
        barcode = scanner.scan(timeout=30)
        
        if barcode:
            print(f"Success! Scanned EAN-13: {barcode}")
            # Validate EAN-13 check digit
            if len(barcode) == 13 and barcode.isdigit():
                print("Valid EAN-13 format")
            else:
                print("Warning: Doesn't match EAN-13 format")
        else:
            print("No EAN-13 barcode detected")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scanner.stop()