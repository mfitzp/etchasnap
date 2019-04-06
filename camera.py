from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops
import cv2
import numpy as np
from io import BytesIO

from picamera import PiCamera

# Global camera instance.
camera = None


FILL_PATTERNS = [
    np.array([[1]]),
    1-np.eye(16),    
    1-np.eye(8),    
    1-np.eye(4),
]

def prepare():
    global camera
    camera = PiCamera()
    camera.resolution = 800,600


# Camera take picture.
def take_photo():
    global camera
    stream = BytesIO()
    camera.capture(stream, format='jpeg')
    camera.close()

    stream.seek(0)
    image = Image.open(stream).transpose(Image.ROTATE_180)
    return image


def crop_and_resize(image):
    # Etch-a-Sketch screen is 5:3 ratio (e.g. (25) 125x75, (24) 120x72, (23) 115x69, (20) 100x60)
    t_width, t_height = (100, 60)
    c_width, c_height = image.size

    wr, hr = t_width / c_width, t_height / c_height

    # Scale the smallest dimension
    ratio = wr if wr > hr else hr
    target = int(c_width * ratio), int(c_height * ratio)
    
    image_r = image.resize(target, Image.ANTIALIAS)

    c_width, c_height = image_r.size

    # Crop down to the ratio dimensions 600 x 400
    # Returns a rectangular region from this image. The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
    # Calculate middle of image
    hw, hh = c_width // 2, c_height // 2
    x, y = t_width // 2, t_height // 2

    return image_r.crop((hw - x, hh -y, hw + x, hh + y))

    
def find_edges(gray):
    ocv = np.array(gray) 
    threshold1 = 200
    threshold2 = 50
    edgec = cv2.Canny(ocv, threshold1, threshold2)
    edgec = Image.fromarray(edgec)
    return ImageOps.invert(edgec)


def pattern_fill(gray, expand=4):
    blur = ImageFilter.GaussianBlur(radius=2)
    gray = gray.filter(blur).convert('P', palette=Image.ADAPTIVE, colors=len(FILL_PATTERNS))

    data = np.array(gray)
    output = data.copy()

    width, height = data.shape

    for n, pattern in enumerate(FILL_PATTERNS):
        p_width, p_height = pattern.shape
    
        fill_image = np.tile(pattern * 255, (width // p_width + 1, height // p_height + 1))
        # Drop down to image dimensions, so we map straight through.
        fill_image = fill_image[:width, :height]
        mask = data == n
        output[mask] = fill_image[mask]
    
    return Image.fromarray(output)


def draw_border_box(img):
    draw = ImageDraw.Draw(img)
    t_width, t_height = img.size
    draw.line(((0, 0), (t_width-1, 0)), fill=0, width=1)
    draw.line(((t_width-1, 0), (t_width-1, t_height-1)), fill=0, width=1)
    draw.line(((t_width-1, t_height-1), (0, t_height-1)), fill=0, width=1)
    draw.line(((0, t_height-1), (0, 0)), fill=0, width=1)
    return img
    

def compose_images(*args):
    output = args[0]
    for i in args[1:]:
        output = ImageChops.multiply(output, i)
    
    return draw_border_box(output)


def gray_enhance(image):
    gray = image.convert('L')
    return ImageOps.autocontrast(gray)


def process_image(image, shader=False):
    """
    Process input image to a simple as possible line-drawing.
    """
    # Handle the resizing ourselves.
    image = crop_and_resize(image)

    gray = gray_enhance(image)
    edges = find_edges(gray)   
    
    # Optionally overlay the shader fill. 
    if shader:
        pattern = pattern_fill(gray)
        edges = compose_images(edges, pattern)

    composed_image = draw_border_box(edges)

    return composed_image


