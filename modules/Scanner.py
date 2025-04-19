import cv2
from pyzbar.pyzbar import decode
import numpy as np

def BarcodeReader(image):
    # Read the image from file1
    img = cv2.imread(image)
    detectedBarcodes = decode(img)
    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
    else:
        for barcode in detectedBarcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(img, (x-10, y-10), (x+w+10, y+h+10), (255, 0, 0), 2)
            if barcode.data != b"":
                print("Barcode Data:", barcode.data.decode('utf-8'))
                print("Barcode Type:", barcode.type)
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def RealTimeBarcodeScanner():
    cap = cv2.VideoCapture(0)  # Change index if needed (e.g., 1 for second camera)
    if not cap.isOpened():
        print("Unable to open camera")
        return ""
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Pre-process: convert frame to grayscale for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Try to decode one or more barcodes in this frame
        barcodes = decode(gray)
        if barcodes:
            # For this function we return the first detected barcode:
            for barcode in barcodes:
                try:
                    barcode_data = barcode.data.decode('utf-8')
                except Exception as e:
                    barcode_data = "N/A"
                # Draw rectangle for visual feedback
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, barcode_data, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)
                # Show the result briefly before returning
                cv2.imshow("Real-Time Barcode Scanner", frame)
                cv2.waitKey(1000)
                cap.release()
                cv2.destroyAllWindows()
                return barcode_data

        cv2.imshow("Real-Time Barcode Scanner", frame)
        # Press 'q' to exit scan mode manually
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return ""

def main():
    # Ask for the number of items (excluding the header)
    try:
        n = int(input("Enter the number of items to scan (header will be scanned last): "))
    except:
        print("Invalid input.")
        return

    # We need to scan n items + 1 header = n+1 barcodes in total
    total_scans = n + 1
    results = []

    for i in range(total_scans):
        if i == n:
            print("\nScan the HEADER barcode now.")
        else:
            print(f"\nScan item {i+1} barcode:")
        barcode = RealTimeBarcodeScanner()
        results.append(barcode)
        # Optionally, let the user know what was scanned:
        print("Scanned barcode:", barcode)

    # Display the results with item numbers, marking the header separately
    print("\nFinal scanned results:")
    for idx, code in enumerate(results, start=1):
        if idx == len(results):
            print(f"Header: {code}")
        else:
            print(f"Item {idx}: {code}")

if __name__ == "__main__":
    main()
