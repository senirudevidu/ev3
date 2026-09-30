#!/usr/bin/env pybricks-micropython
"""Bounded baseline and warm-start training. See SESSION_NOTES.md."""
import os
import pickle
import random
from pybricks.ev3devices import ColorSensor, InfraredSensor, Motor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button, Port
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait

# Sensor calibration and motor direction verified on the live brick.
# Wheel geometry remains nominal; validate before increasing speed or duration.
HARDWARE_CALIBRATED = True
TRAINING = False
# Measured dark=3..4, edge=22..23, yellow=34..35; target the tape edge.
WHITE_VALUE, BLACK_VALUE = 28, 13
WHEEL_DIAMETER, AXLE_TRACK = 40, 50  # Still awaiting physical measurements.
ALPHA, GAMMA, EXPLORATION = 0.1, 0.9, 0.10
SESSION_MS, MAX_TRAINING_STEPS = 86400000, 1000000
TURN_TIMEOUT_MS = None  # Turns continue until the sensor state changes or Center is pressed.
FORWARD_SPEED, TURN_RATE = 30, 55
INPUT_TABLE = 'q_table.pkl'
TRAINED_TABLE = 'q_table_candidate.pkl'
ACTIONS = ('forward', 'turn_left', 'turn_right')
LIGHTS = ('WHITE', 'MIDDLE', 'BLACK')
M_X = (('MIDDLE', 'turn_right', 'WHITE'), ('WHITE', 'turn_left', 'MIDDLE'),
       ('MIDDLE', 'turn_left', 'BLACK'), ('BLACK', 'turn_right', 'MIDDLE'))
M_Y = (('MIDDLE', 'turn_right', 'BLACK'), ('BLACK', 'turn_left', 'MIDDLE'),
       ('MIDDLE', 'turn_left', 'WHITE'), ('WHITE', 'turn_right', 'MIDDLE'))


class SessionStopped(Exception):
    pass


class ObstacleDetected(Exception):
    pass


def load_table():
    with open(INPUT_TABLE, 'rb') as source:
        table = pickle.load(source)
    expected = [(m, s, a) for m in (True, False) for s in LIGHTS for a in ACTIONS]
    if len(table) != 18 or any(key not in table for key in expected):
        raise ValueError('Q table must contain all 18 expected entries')
    for value in table.values():
        if not isinstance(value, (int, float)) or not -float('inf') < value < float('inf'):
            raise ValueError('Q values must be finite numbers')
    return table


def save_table(table):
    with open(TRAINED_TABLE + '.tmp', 'wb') as target:
        pickle.dump(table, target)
    os.rename(TRAINED_TABLE + '.tmp', TRAINED_TABLE)


def best_action(table, mode, state):
    return max(ACTIONS, key=lambda action: table[(mode, state, action)])


def next_mode(mode, state, action, new_state):
    transition = (state, action, new_state)
    if transition in M_X:
        return True
    if transition in M_Y:
        return False
    return mode


class Controller:
    def __init__(self):
        self.ev3 = EV3Brick()
        self.left = Motor(Port.A)
        self.right = Motor(Port.D)
        self.sensor = ColorSensor(Port.S1)
        self.ir = InfraredSensor(Port.S4)
        self.robot = DriveBase(self.left, self.right,
                               wheel_diameter=WHEEL_DIAMETER, axle_track=AXLE_TRACK)
        self.clock = None

    def stop(self):
        try:
            self.robot.stop()
        finally:
            try:
                self.left.brake()
            finally:
                self.right.brake()

    def state(self):
        value = self.sensor.reflection()
        if value >= WHITE_VALUE:
            return 'WHITE'
        if value <= BLACK_VALUE:
            return 'BLACK'
        return 'MIDDLE'

    def check_stop(self):
        if Button.CENTER in self.ev3.buttons.pressed():
            raise SessionStopped('Center button pressed')
        if self.clock is not None and self.clock.time() >= SESSION_MS:
            raise SessionStopped('Session time limit reached')
        # Pybricks IR distance is relative 0..100, not centimetres.
        if self.ir.distance() < 15:
            raise ObstacleDetected('Obstacle detected')

    def avoid_obstacle(self, mode):
        """Deterministic obstacle bypass; resume when tape/edge is reacquired."""
        direction = -TURN_RATE if mode else TURN_RATE
        try:
            self.robot.drive(-20, 0)
            wait(350)
            stable = 0
            while True:
                if Button.CENTER in self.ev3.buttons.pressed():
                    raise SessionStopped('Center button pressed')
                current = self.state()
                # Yellow tape (WHITE) and its edge (MIDDLE) are both valid
                # path readings; BLACK is the background. Require two stable
                # readings after the obstacle clears to avoid false recovery.
                if self.ir.distance() >= 15 and current in ('WHITE', 'MIDDLE'):
                    stable += 1
                    if stable >= 2:
                        self.ev3.speaker.beep()
                        print('obstacle_reacquired_path', mode, current)
                        return mode, current
                else:
                    stable = 0
                self.robot.drive(0, direction)
                wait(30)
        finally:
            self.stop()

    def action(self, action, state):
        timer = StopWatch()
        try:
            self.check_stop()
            if action == 'forward':
                self.robot.drive(FORWARD_SPEED, 0)
                while timer.time() < 250:
                    self.check_stop()
                    wait(20)
            else:
                rate = -TURN_RATE if action == 'turn_left' else TURN_RATE
                while self.state() == state:
                    self.check_stop()
                    self.robot.drive(0, rate)
                    wait(20)
        finally:
            self.stop()

    def arm(self):
        self.ev3.screen.clear()
        self.ev3.screen.print('TRAIN' if TRAINING else 'BASELINE')
        self.ev3.screen.print('Center: start/stop')
        print('Waiting for center-button press and release on the brick')
        while Button.CENTER not in self.ev3.buttons.pressed():
            wait(20)
        while Button.CENTER in self.ev3.buttons.pressed():
            wait(20)
        self.clock = StopWatch()

    def session(self, table):
        mode, state = True, self.state()
        self.action('turn_right', state)
        new_state = self.state()
        mode = next_mode(mode, state, 'turn_right', new_state)
        state = new_state
        iterations = 0
        while not TRAINING or iterations < MAX_TRAINING_STEPS:
            try:
                self.check_stop()
            except ObstacleDetected:
                self.ev3.speaker.beep()
                print('obstacle_detected', mode, state)
                mode, state = self.avoid_obstacle(mode)
                continue
            action = best_action(table, mode, state)
            if TRAINING and random.uniform(0, 1) < EXPLORATION:
                action = random.choice(ACTIONS)
            try:
                self.action(action, state)
            except ObstacleDetected:
                self.ev3.speaker.beep()
                print('obstacle_detected', mode, state)
                mode, state = self.avoid_obstacle(mode)
                continue
            new_state = self.state()
            new_mode = next_mode(mode, state, action, new_state)
            reward = 10 if new_state == 'MIDDLE' else -10
            if TRAINING:
                key = (mode, state, action)
                next_best = best_action(table, new_mode, new_state)
                target = reward + GAMMA * table[(new_mode, new_state, next_best)]
                table[key] += ALPHA * (target - table[key])
            print(iterations, mode, state, action, new_state, reward)
            mode, state = new_mode, new_state
            iterations += 1
            if TRAINING and iterations % 25 == 0:
                save_table(table)


def main():
    if not HARDWARE_CALIBRATED:
        raise ValueError('Verify ports, motor directions, geometry and thresholds; then set HARDWARE_CALIBRATED=True')
    if not 0 <= BLACK_VALUE < WHITE_VALUE <= 100:
        raise ValueError('Invalid reflection thresholds')
    table = load_table()
    controller = Controller()
    started = False
    try:
        controller.arm()
        started = True
        controller.session(table)
    except SessionStopped as exc:
        print('Stopped:', exc)
    except KeyboardInterrupt:
        print('Stopped by operator')
    finally:
        controller.stop()
        if TRAINING and started:
            save_table(table)
            print('Saved candidate to', TRAINED_TABLE)


if __name__ == '__main__':
    main()
