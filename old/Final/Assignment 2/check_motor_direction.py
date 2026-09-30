#!/usr/bin/env pybricks-micropython
"""Lift wheels first. Center starts a single 300 ms pulse on each motor."""
from pybricks.ev3devices import Motor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button, Port, Stop
from pybricks.tools import wait

brick = EV3Brick()
left, right = Motor(Port.A), Motor(Port.D)
try:
    for label, motor in (('A: expected LEFT', left), ('D: expected RIGHT', right)):
        brick.screen.clear()
        brick.screen.print('LIFT BOTH WHEELS')
        brick.screen.print(label)
        brick.screen.print('Center: 0.3s pulse')
        print('Lift wheels;', label, '; press/release Center to pulse forward')
        while Button.CENTER not in brick.buttons.pressed():
            wait(20)
        while Button.CENTER in brick.buttons.pressed():
            wait(20)
        motor.run_time(120, 300, then=Stop.BRAKE)
        brick.speaker.beep()
    brick.screen.clear()
    brick.screen.print('Motor check ended')
    print('MOTOR_CHECK_COMPLETE: report physical sides and forward directions')
finally:
    try:
        left.brake()
    finally:
        right.brake()
