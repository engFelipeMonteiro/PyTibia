from src.utils.camera import PyCamera
import time
def test_get_latest_frame():
    print('waiting 5 sec')
    time.sleep(5)
    camera = PyCamera()
    camera.get_latest_frame('screen.png')
