import time
import random
from config import (
    SPEED_DEFAULT, SPEED_SLOW, OBSTACLE_THRESHOLD_CM,
    STATE_ON_LINE, STATE_OFF_LINE, STATE_OBSTACLE,
    ACTION_FORWARD, ACTION_REVERSE, ACTION_TURN_LEFT, ACTION_TURN_RIGHT
)
from motors import Motors
from sensors import Sensors


class Robot:
    def __init__(self):
        self.motors = Motors()
        self.sensors = Sensors()
        self.last_state = None
        self.last_action = None

    def forward(self, speed=SPEED_DEFAULT):
        self.motors.move_forward(speed)

    def reverse(self, speed=SPEED_DEFAULT):
        self.motors.move_reverse(speed)

    def left(self, speed=SPEED_DEFAULT):
        self.motors.turn_left(speed)

    def right(self, speed=SPEED_DEFAULT):
        self.motors.turn_right(speed)

    def stop(self):
        self.motors.stop()

    def get_state(self):
        return self.sensors.get_state()

    def execute_action(self, action, speed=SPEED_DEFAULT):
        if action == ACTION_FORWARD:
            self.forward(speed)
        elif action == ACTION_REVERSE:
            self.reverse(speed)
        elif action == ACTION_TURN_LEFT:
            self.left(speed)
        elif action == ACTION_TURN_RIGHT:
            self.right(speed)
        self.last_action = action
        time.sleep(0.3)
        self.stop()

    def calculate_reward(self, state):
        if state == STATE_OBSTACLE:
            return -100
        if state == STATE_ON_LINE:
            return 10
        if state == STATE_OFF_LINE:
            return -10
        return 0

    def is_obstacle_detected(self):
        dist = self.sensors.read_ultrasonic()
        return dist is not None and dist < OBSTACLE_THRESHOLD_CM

    def avoid_obstacle(self):
        self.stop()
        self.reverse(SPEED_SLOW)
        time.sleep(1)
        self.stop()

        turn_direction = random.choice([-1, 1])
        if turn_direction > 0:
            self.right(SPEED_SLOW)
        else:
            self.left(SPEED_SLOW)
        time.sleep(1.5)
        self.stop()

    def find_line(self):
        found = False
        for _ in range(12):
            state = self.get_state()
            if state != STATE_OFF_LINE:
                found = True
                break
            self.left(SPEED_SLOW)
            time.sleep(0.5)
            self.stop()
            time.sleep(0.2)

        if not found:
            for _ in range(12):
                state = self.get_state()
                if state != STATE_OFF_LINE:
                    found = True
                    break
                self.right(SPEED_SLOW)
                time.sleep(0.5)
                self.stop()
                time.sleep(0.2)

        return found
