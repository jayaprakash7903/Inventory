from pyzbar.pyzbar import decode
from PIL import Image
import io
import logging

def decode_barcode_from_bytes(image_bytes):
    """Decode barcode from image bytes with error handling"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        decoded_objects = decode(img)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception as e:
        logging.error(f"Barcode decoding failed: {str(e)}")
        return None