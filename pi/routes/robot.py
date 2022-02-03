import logging
import os
import traceback

from tcp import Blueprint, ACTIONS

server = Blueprint(__file__)
try:
    from robot import Robot
    robot = Robot.instance()
except:
    pass
try:
    @server.on(ACTIONS.LIVESTREAM)
    def livestream(socket):
        liveimg = robot.get_liveimg()
        socket.send(action=ACTIONS.LIVESTREAM, msg=liveimg)

    @server.on(ACTIONS.SPEED)
    def speed(params):
        new_speed = int(params)
        robot.set_speed(new_speed)

    @server.on(ACTIONS.STEERING)
    def steering(params):
        new_steering = int(params)
        robot.set_steering(new_steering)
except:
    server.set_error(traceback.format_exc())
