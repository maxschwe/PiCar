from .camera import Camera
from .servo import Servo
from ..configuration.robot_config import *
import RPi.GPIO as GPIO
import time


MOTOR_CONTROL_VECTOR = {"forward": [GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW],
                        "backward": [GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH],
                        "stop": 4 * [GPIO.LOW]}


class InstanceBuffer:
    instance = 0


class Robot:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.mov_type = "Stop"
        self.camera = Camera()
        self.servo = Servo(servo, init_pos=90)

        for out in OUTPUTS:
            GPIO.setup(out, GPIO.OUT)
            GPIO.output(out, GPIO.LOW)

        self.m_left = GPIO.PWM(en_left, 120)
        self.m_right = GPIO.PWM(en_right, 120)
        self.set_speed(0)
        self.set_steering(0)

    def get_liveimg(self):
        return self.camera.get_frame()

    def set_speed(self, speed):
        if speed == 0:
            self.speed = 0
            self.mov_type = 'Stop'
        else:
            self.mov_type = 'Backward' if speed < 0 else 'Forward'
            self.speed = round(self._map_between(
                abs(speed), 0, 100, MIN_SPEED, 100), 2)

        for pin, val in zip(MOTOR_CONTROL, MOTOR_CONTROL_VECTOR[self.mov_type]):
            GPIO.out(pin, val)

        self.m_left.ChangeDutyCycle(self.speed)
        self.m_right.ChangeDutyCycle(self.speed)

    def set_steering(self, steering):
        self.steering = self._map_between(
            steering, -100, 100, SERVO_MIN, SERVO_MAX)
        self.servo.move(self.steering)

    def run(self):
        self.m_left.start(0)
        self.m_right.start(0)
        while True:

            time.sleep(0.2)

    def test(self):
        self.servo.test()

    def _map_between(self, val, min_in, max_in, min_out, max_out):
        if not (min_in <= val <= max_in):
            print(f"The inputted value {val} is not in [{min_in}, {max_in}]")
            return None
        return min_out + (val - min_in) / (max_in - min_in) * (max_out - min_out)

    @ staticmethod
    def instance():
        if InstanceBuffer.instance == 0:
            InstanceBuffer.instance = Robot()
        return InstanceBuffer.instance
