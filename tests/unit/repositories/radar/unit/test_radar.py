from src.repositories.radar.extractors import getRadarImage
from src.repositories.radar.locators import getRadarToolsPosition
from src.repositories.radar.core import getFloorLevel
from tests.utils import file_to_gray_image, result_pos_draw
from src.utils.core import  hashit

from src.utils.image import loadFromRGBToGray
from src.repositories.radar.config import floorsLevelsImgsHashes


#getFloorLevel
#getRadarToolsPosition
#getRadarImage

screenshotImage = file_to_gray_image('tests/data/screen_fullscreen.png')


def test_getRadarImage():
    screenshotImage = file_to_gray_image('tests/data/screen_fullscreen.png')
    getRadarImage(screenshotImage)


def test_getRadarToolsPosition():
    screenshotImage = file_to_gray_image('tests/data/screen_fullscreen.png')
    pos = getRadarToolsPosition(screenshotImage)
    result_pos_draw(screenshotImage, pos, 'test_getRadarToolsPosition.png')

def test_getFloorLevel_macos():
    screenshotImage = file_to_gray_image('tests/data/screen_fullscreen.png')
    pos = getFloorLevel(screenshotImage)
    import pdb; pdb.set_trace()
    result_pos_draw(screenshotImage, pos, 'test_getFloorLevel.png')

def test_getFloorLevel_windows():
    screenshotImage = loadFromRGBToGray('tests/data/screen_windows.png')
    floor = getFloorLevel(screenshotImage)
    assert floor == 7

def test_getFloorLevel_correlate():
    template = loadFromRGBToGray('src/repositories/radar/images/floorLevels/7.png')
    screenshotImage = file_to_gray_image('tests/data/screen_windows.png')

    tradicional_image = loadFromRGBToGray(
        'src/repositories/radar/images/floorLevels/7.png'),
    radarToolsPosition = getRadarToolsPosition(screenshotImage)
    radarToolsPositionIsEmpty = radarToolsPosition is None
    if radarToolsPositionIsEmpty:
        return None
    left, top, width, height = radarToolsPosition
    left = left + width + 8
    top = top - 7
    height = 67
    width = 2
    floorLevelImg = screenshotImage[top:top + height, left:left + width]
    floorImgHash = hashit(floorLevelImg)
    assert floorImgHash in floorsLevelsImgsHashes
    import pdb; pdb.set_trace()