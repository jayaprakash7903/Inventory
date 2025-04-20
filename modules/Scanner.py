import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def decode_barcode_from_bytes(image_bytes):
    """
    Enhanced barcode decoder that handles mobile camera inputs better
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode with OpenCV
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding for mobile camera inputs
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Try decoding with different approaches
        for img_to_decode in [gray, thresh, img]:
            decoded = decode(
                img_to_decode,
                symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128, ZBarSymbol.QRCODE],
                # These parameters help with mobile camera images:
                try_harder=True,
                try_rotate=True
            )
            if decoded:
                return decoded[0].data.decode('utf-8')
        
        return None
        
    except Exception as e:
        logger.error(f"Decoding failed: {str(e)}")
        return None

class RealTimeBarcodeScanner:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open video device")

    def scan(self, max_attempts=5):
        """
        Enhanced real-time scanning with mobile compatibility
        """
        for _ in range(max_attempts):
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Convert frame to RGB (better for mobile)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Try multiple decoding strategies
            for img_to_decode in [frame, rgb_frame]:
                decoded = decode(
                    img_to_decode,
                    symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128],
                    try_harder=True
                )
                if decoded:
                    return decoded[0].data.decode('utf-8')
                
            # Optional: Add small delay between attempts
            cv2.waitKey(300)
            
        return None

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

# Mobile-specific helper function
def decode_mobile_image(image_bytes):
    """
    Specialized decoder for mobile camera photos
    """
    try:
        # Use PIL for better mobile image handling
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        img_array = np.array(img.convert('RGB'))
        
        # Mobile-specific processing
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        img_array = cv2.resize(img_array, (0,0), fx=1.5, fy=1.5)  # Upscale
        
        return decode(
            img_array,
            symbols=[ZBarSymbol.EAN13, ZBarSymbol.CODE128],
            try_harder=True,
            try_rotate=True
        )[0].data.decode('utf-8') if decode(img_array) else None
        
    except Exception as e:
        logger.error(f"Mobile decoding failed: {str(e)}")
        return None