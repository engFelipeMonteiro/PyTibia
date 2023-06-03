import pathlib
from src.repositories.battleList.locators import getContainerTopBarPosition, getContainerBottomBarPosition
from src.utils.image import loadFromRGBToGray


from tests.utils import result_pos_draw, file_to_gray_image

currentPath = pathlib.Path(__file__).parent.resolve()


# TODO: assert "locate" calls and params
def test_should_get_container_top_bar_pos():
    screenshotImage = loadFromRGBToGray(f'{currentPath}/screenshot.png')
    containerTopBarPos = getContainerTopBarPosition(screenshotImage)
    expectedContainerTopBarPos = (1572, 25, 81, 13)
    assert containerTopBarPos == expectedContainerTopBarPos


def test_should_get_container_top_bar_pos_mac_os():
    screenshotImage = file_to_gray_image('tests/data/screen_fullscreen.png')
    containerTopBarPos = getContainerTopBarPosition(screenshotImage, scale=2)
    result_pos_draw(screenshotImage, containerTopBarPos, 'test_should_get_container_top_bar_pos_mac_os.png')

def test_should_get_container_bottom_bar_pos_mac_os():
    screenshotImage = file_to_gray_image('tests/data/screen_fullscreen.png')
    containerTopBarPos = getContainerBottomBarPosition(screenshotImage, scale=2)
    result_pos_draw(screenshotImage, containerTopBarPos, 'test_should_get_container_bottom_bar_pos_mac_os.png')