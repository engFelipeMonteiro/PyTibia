from src.utils.core import getScreenshot, getScreenshot_osx
from ...typings import Context


# TODO: add unit tests
def setScreenshot(gameContext: Context, is_osx=False) -> Context:
    if is_osx:
        gameContext['screenshot'] = getScreenshot_osx()
    else:
       gameContext['screenshot'] = getScreenshot()
    return gameContext
