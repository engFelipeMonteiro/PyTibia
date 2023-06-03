import pathlib
import pytest
from src.repositories.actionBar.locators import getLeftArrowsPosition, getRightArrowsPosition
from src.utils.image import loadFromRGBToGray
from tests.utils import file_to_gray_image

currentPath = pathlib.Path(__file__).parent.resolve()


def test_should_return_None_when_left_arrows_are_unlocked():
    screenshotImage = loadFromRGBToGray(f'{currentPath}/leftArrowsUnlocked.png')
    leftArrowsPosition = getLeftArrowsPosition(screenshotImage)
    expectedLeftArrowsPosition = None
    assert leftArrowsPosition == expectedLeftArrowsPosition


def test_should_get_left_arrows_position():
    screenshotImage = loadFromRGBToGray(f'{currentPath}/leftArrowsLocked.png')
    leftArrowsPosition = getLeftArrowsPosition(screenshotImage)
    expectedLeftArrowsPosition = (0, 392, 17, 34)
    assert leftArrowsPosition == expectedLeftArrowsPosition

def test_get_arrow_image_macos_fullscreen():
    img = file_to_gray_image('tests/data/screen_fullscreen.png', is_gray=True, is_rgba=False)
    leftArrowsPosition = getLeftArrowsPosition(img)
    rightArrowsPosition = getRightArrowsPosition(img)
    import pdb; pdb.set_trace()

def test_get_arrow_image_macos_windowed():
    img = file_to_gray_image('tests/data/screen_windowed.png', is_gray=True, is_rgba=False)
    template = file_to_gray_image('src/repositories/actionBar/images/arrows/left.png', is_gray=False, is_rgba=True)
    leftArrowsPosition = getLeftArrowsPosition(img)
    rightArrowsPosition = getRightArrowsPosition(img)
    import pdb; pdb.set_trace()

from src.utils.core import cacheObjectPosition, locate

img1 = file_to_gray_image('tests/data/screen_fullscreen.png', is_gray=False, is_rgba=False)
img2 = file_to_gray_image('tests/data/screen_windowed.png', is_gray=False, is_rgba=False)
img3 = file_to_gray_image('tests/unit/repositories/gameWindow/screenshot01.png', is_gray=False, is_rgba=False)

template1 = file_to_gray_image('src/repositories/actionBar/images/arrows/left.png', is_gray=False, is_rgba=True)
template2 = file_to_gray_image('src/repositories/actionBar/images/arrows/right.png', is_gray=False, is_rgba=True)
from itertools import product
import os
from tests.utils import result_pos_draw
cartesian_product = product([img1, img2], [template1, template2])
@pytest.mark.parametrize("ags", cartesian_product)
def test_locale(ags):
    test_name = os.environ['PYTEST_CURRENT_TEST'].split('::')[1].split(' ')[0]
    #import pdb; pdb.set_trace()
    
    result = locate(ags[0], ags[1])
    assert result
    result_pos_draw(ags[0],result, f"{test_name}.png")
