import time
import cv2
import numpy as np
from imutils.video.pivideostream import PiVideoStream


class Camera(object):
    def __init__(self, flip=False):
        self.vs = PiVideoStream().start()
        self.flip = flip
        time.sleep(2.0)

    def _flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def _get_frame(self):
        frame = self._flip_if_needed(self.vs.read())
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def gen_videostream(self):
        while True:
            frame = self._get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def __del__(self):
        self.vs.stop()
