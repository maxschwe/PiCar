import RPi.GPIO as GPIO
import time
from ..configuration.robot_config import SERVO_Y_INTERCEPT, SERVO_M


class Servo:
    def __init__(self, pin, init_pos=0):
        self.pin = pin
        self.cur_angle = init_pos
        GPIO.setup(self.pin, GPIO.OUT)
        self.out = GPIO.PWM(self.pin, 50)
        self.init(init_pos)

    def _conv_deg_duty(self, deg):
        return SERVO_Y_INTERCEPT + deg * SERVO_M

    def init(self, deg):
        self.out.start(0)
        self.move(deg, delay=1)

    def move(self, deg, delay=None):
        if delay is None:
            delay = abs(deg - self.cur_angle) / 180
        duty = self._conv_deg_duty(deg)
        self.out.ChangeDutyCycle(duty)
        time.sleep(delay)
        self.out.ChangeDutyCycle(0)
        self.cur_angle = deg

    def test(self):
        for i in range(180):
            self.move(i)
