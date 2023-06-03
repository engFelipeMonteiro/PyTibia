
import pyautogui
import cv2
import numpy as np
import pathlib



class PyCamera():
    is_capturing = True
    cwd = pathlib.Path(__file__).parent.resolve()
    def get_latest_frame(self, path='screen.png', test=False):
        if test:
            return self.get_local_image(path)
        else:
            return self.get_frame(path)


    def get_frame(self, path):
        img = pyautogui.screenshot()
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2GRAY)
        if path:
            # import cv2; cv2.imwrite('screen_test.png', screenshot)
            cv2.imwrite(path, img)
        return img
    
    def get_local_image(self, path):
        from tests.utils import file_to_gray_image
        files = {
            'full': f'{self.cwd}/images/screen_fullscreen.png',
            'window': f'{self.cwd}/images/screen_windowed.png'
        }
        
        img = file_to_gray_image(files['full'])
        cv2.imwrite(path, img)
        return img
