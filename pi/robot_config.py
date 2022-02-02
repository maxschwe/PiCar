in1_left = 23
in2_left = 24
en_left = 25

in1_right = 17
in2_right = 27
en_right = 22

servo = 5

MOTOR_CONTROL = [in1_left, in2_left, in1_right, in2_right]
OUTPUTS = MOTOR_CONTROL + [en_left, en_right]


MIN_SPEED = 30

MAX_STEERING_ANGLE = 35
SERVO_MIN = 90 - MAX_STEERING_ANGLE
SERVO_MAX = 90 + MAX_STEERING_ANGLE

SERVO_M = 1 / 20.8
SERVO_Y_INTERCEPT = 2.3
