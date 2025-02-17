from src.shared.typings import BBox, GrayImage
from .config import barSize


# TODO: add unit tests
# TODO: add perf
def getHpBar(screenshot: GrayImage, heartPos: BBox) -> GrayImage:
    (left, top, _, _) = heartPos
    y0 = top + 5
    y1 = y0 + 1
    x0 = left + 13
    x1 = x0 + barSize
    bar = screenshot[y0:y1, x0:x1][0]
    return bar


# TODO: add unit tests
# TODO: add perf
def getManaBar(screenshot: GrayImage, heartPos: BBox) -> GrayImage:
    (left, top, _, _) = heartPos
    y0 = top + 5
    y1 = y0 + 1
    x0 = left + 14
    x1 = x0 + barSize
    bar = screenshot[y0:y1, x0:x1][0]
    return bar
