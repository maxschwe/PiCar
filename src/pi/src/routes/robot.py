import logging
import os

from .blueprint import Blueprint
from .. import ACTION, RETURN, config

from ..robot import Robot

server = Blueprint()
robot = Robot.instance()


@server.on(ACTION.LIVESTREAM)
def livestream(socket):
    liveimg = robot.get_liveimg()
    socket.send(action=ACTION.LIVESTREAM, msg=liveimg)


@server.on(ACTION.SPEED)
def speed(msg):
    new_speed = int(msg)
    robot.set_speed(new_speed)


@server.on(ACTION.STEERING)
def steering(msg):
    new_steering = int(msg)
    robot.set_steering(new_steering)
