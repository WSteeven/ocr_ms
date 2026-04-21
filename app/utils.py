import cv2

def save_debug_image(img, name="debug.jpg"):
    cv2.imwrite(f"/tmp/{name}", img)
