from .camera import Camera
from .servo import Servo
import RPi.GPIO as GPIO
import time


in1_left = 23
in2_left = 24
en_left = 25

in1_right = 17
in2_right = 27
en_right = 22

servo = 5

OUTPUTS = [in1_left, in2_left, en_left, in1_right, in2_right, en_right]

MIN_SPEED = 20
MAX_STEERING_ANGLE = 35
SERVO_MIN = 90 - MAX_STEERING_ANGLE
SERVO_MAX = 90 + MAX_STEERING_ANGLE


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
        print(f"Speed: {self.speed}")

    def set_steering(self, steering):
        self.steering = self._map_between(
            steering, -100, 100, SERVO_MIN, SERVO_MAX)
        self.servo.move(self.steering)

    def run(self):
        self.m_left.start(0)
        self.m_right.start(0)
        while True:
            if self.mov_type == "Stop":
                GPIO.output(in1_left, GPIO.LOW)
                GPIO.output(in2_left, GPIO.LOW)
                GPIO.output(in1_right, GPIO.LOW)
                GPIO.output(in2_right, GPIO.LOW)
            elif self.mov_type == "Backward":
                GPIO.output(in1_left, GPIO.LOW)
                GPIO.output(in2_left, GPIO.HIGH)
                GPIO.output(in1_right, GPIO.LOW)
                GPIO.output(in2_right, GPIO.HIGH)
            elif self.mov_type == "Forward":
                GPIO.output(in1_left, GPIO.HIGH)
                GPIO.output(in2_left, GPIO.LOW)
                GPIO.output(in1_right, GPIO.HIGH)
                GPIO.output(in2_right, GPIO.LOW)
            self.m_left.ChangeDutyCycle(self.speed)
            self.m_right.ChangeDutyCycle(self.speed)
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
