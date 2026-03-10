import serial
import argparse
import numpy as np
import cv2
import time

IMG_COL = 320
IMG_ROW = 180
IMG_COL_2 = IMG_COL // 2
IMG_SIZE = IMG_ROW * IMG_COL_2  # 28800 bytes

WINDOW_NAME = "UART Image Monitor"
DISPLAY_SCALE = 8  # Scale up for better visibility

def deserialize_pix2(data: bytes) -> np.ndarray:
    raw = np.frombuffer(data, dtype=np.uint8)
    p1 = raw & 0x0F         # lower nibble
    p2 = (raw >> 4) & 0x0F  # upper nibble
    # Interleave p1 and p2 to reconstruct full image row
    pixels = np.empty(len(raw) * 2, dtype=np.uint8)
    pixels[0::2] = p1
    pixels[1::2] = p2
    return pixels.reshape((IMG_ROW, IMG_COL))

def receive_image(ser: serial.Serial) -> np.ndarray | None:
    """Read IMG_SIZE bytes from serial and return deserialized image."""
    data = bytearray()
    remaining = IMG_SIZE
    
    while remaining > 0:
        chunk = ser.read(remaining)
        if len(chunk) == 0:
            # Timeout with no data - no frame available
            if len(data) == 0:
                return None
            # Partial frame received, keep waiting
            continue
        data.extend(chunk)
        remaining -= len(chunk)
    
    return deserialize_pix2(bytes(data))

def monitor(args):
    ser = serial.Serial(args.port, args.baudrate, timeout=1)
    print(f"Listening on {args.port} at {args.baudrate} baud...")
    print(f"Expecting {IMG_SIZE} bytes per image ({IMG_ROW}x{IMG_COL} @ 4bpp)")
    print("Press 'q' to quit, 's' to save current frame")
    
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, IMG_COL * DISPLAY_SCALE, IMG_ROW * DISPLAY_SCALE)
    
    frame_count = 0
    last_time = time.time()
    
    try:
        while True:
            image = receive_image(ser)
            
            if image is not None:
                frame_count += 1
                
                # Scale 4-bit (0-15) to 8-bit (0-255) for display
                display_img = (image * 17).astype(np.uint8)  # 255/15 ≈ 17
                
                # Calculate and display FPS
                current_time = time.time()
                fps = 1.0 / (current_time - last_time) if (current_time - last_time) > 0 else 0
                last_time = current_time
                
                # Add FPS overlay
                cv2.putText(display_img, f"FPS: {fps:.1f}", (10, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,), 1)
                
                cv2.imshow(WINDOW_NAME, display_img)
            
            # Handle key presses (1ms wait to keep UI responsive)
            # key = cv2.waitKey(1) & 0xFF
            # if key == ord('q'):
            #     print("Quit requested")
            #     break
            # elif key == ord('s') and image is not None:
            #     filename = f"frame_{frame_count:04d}.png"
            #     cv2.imwrite(filename, (image * 17).astype(np.uint8))
            #     print(f"Saved {filename}")
    
    finally:
        ser.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor serial port output.')
    parser.add_argument('port', help='Serial port to monitor (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('baudrate', help='Baud rate for the serial port (e.g., 921600)', default=921600, type=int)
    args = parser.parse_args()
    monitor(args)