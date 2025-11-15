from PIL import Image
import os

def resize_image(image_path, size=(800, 800)):
    img = Image.open(image_path)
    img = img.convert("RGB")
    img = img.resize(size)
    img.save(image_path, optimize=True, quality=85)  
