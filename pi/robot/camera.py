import time
import cv2
import numpy as np
from imutils.video.pivideostream import PiVideoStream
import logging


class Camera(object):
    def __init__(self, flip=False):
        try:
            self.vs = PiVideoStream(resolution=(320, 240))
            self.vs.start()
        except:
            logging.error("Failed to start camera")

        self.flip = flip

    def _flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
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
