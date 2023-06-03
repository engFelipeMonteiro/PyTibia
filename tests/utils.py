
import cv2
import pathlib

currentPath = pathlib.Path(__file__).parent.resolve()
import numpy as np
from src.utils.core import locate

from src.utils.image import GrayImage

def file_to_gray_image(img_path: str, is_gray=False, is_rgba=False) -> GrayImage:
    return cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if is_gray:
        return np.array(img)
    elif is_rgba:
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2GRAY)
    else:
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

def img_to_gray_image(img, src_type='RGBA'):
    pass


def result_pos_draw(image, result_position, name, color_bgr = (255, 255, 0), thickness=2):
    path = f"{currentPath}/validation_images/{name}"
    if result_position:
        x, y, width, height = result_position
        cv2.rectangle(image, (x, y), (x+width, y+height), color_bgr, thickness)
    cv2.imwrite(path, image)

def save_screenshoot(screenshot, template, path , confidence=0.85, scale=None):
    # from tests.utils import save_screenshoot; save_screenshoot(screenshot, config.images['tools'], 'getRadarToolsPosition.png', confidence=0.85, scale=2.0)
    pos = locate(screenshot, template, confidence=confidence, scale=scale)
    result_pos_draw(screenshot, pos, path)