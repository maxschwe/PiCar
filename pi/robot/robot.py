from .camera import Camera
from .servo import Servo
from .robot_config import Config
import RPi.GPIO as GPIO
import time


MOTOR_CONTROL_VECTOR = {"forward": [GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW],
                        "backward": [GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH],
                        "stop": 4 * [GPIO.LOW]}


class Robot:
    _instance = 0

    def __init__(self):
        print("ok")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.mov_type = "stop"
        self.manual = False
        self.camera = Camera()
        self.servo = Servo(Config.servo, init_pos=90)

        for out in Config.OUTPUTS:
            GPIO.setup(out, GPIO.OUT)
            GPIO.output(out, GPIO.LOW)

        self.m_left = GPIO.PWM(Config.en_left, 120)
        self.m_right = GPIO.PWM(Config.en_right, 120)
        self.set_speed(0)
        self.set_steering(0)

    def get_liveimg(self):
        return self.camera.get_frame()

    def set_speed(self, speed):
        if speed == 0:
            self.speed = 0
            self.mov_type = 'stop'
        else:
            self.mov_type = 'backward' if speed < 0 else 'forward'
            self.speed = round(self._map_between(
                abs(speed), 0, 100, Config.MIN_SPEED, 100), 2)

        for pin, val in zip(Config.MOTOR_CONTROL, MOTOR_CONTROL_VECTOR[self.mov_type]):
            GPIO.output(pin, val)

        self.m_left.ChangeDutyCycle(self.speed)
        self.m_right.ChangeDutyCycle(self.speed)

    def set_steering(self, steering):
        self.steering = self._map_between(
            steering, -100, 100, Config.SERVO_MIN, Config.SERVO_MAX)
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

    @classmethod
    def instance(cls):
        if cls._instance == 0:
            cls._instance = cls()
            print("oh man")
        return cls._instance
