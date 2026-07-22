import time
from config import (
    MOTOR_LEFT_PORT, MOTOR_RIGHT_PORT,
    SPEED_DEFAULT, SPEED_SLOW, SPEED_FAST
)

try:
    from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent
    from ev3dev2.motor import MoveTank

    class Motors:
        def __init__(self):
            self.left_motor = LargeMotor(MOTOR_LEFT_PORT)
            self.right_motor = LargeMotor(MOTOR_RIGHT_PORT)
            self.tank = MoveTank(MOTOR_LEFT_PORT, MOTOR_RIGHT_PORT)

        def _clamp_speed(self, speed):
            return max(-100, min(100, speed))

        def move_forward(self, speed=SPEED_DEFAULT):
            s = self._clamp_speed(speed)
            self.left_motor.on(SpeedPercent(s))
            self.right_motor.on(SpeedPercent(s))

        def move_reverse(self, speed=SPEED_DEFAULT):
            s = self._clamp_speed(-speed)
            self.left_motor.on(SpeedPercent(s))
            self.right_motor.on(SpeedPercent(s))

        def turn_left(self, speed=SPEED_DEFAULT):
            s = self._clamp_speed(speed)
            self.left_motor.on(SpeedPercent(-s // 2))
            self.right_motor.on(SpeedPercent(s))

        def turn_right(self, speed=SPEED_DEFAULT):
            s = self._clamp_speed(speed)
            self.left_motor.on(SpeedPercent(s))
            self.right_motor.on(SpeedPercent(-s // 2))

        def stop(self):
            self.left_motor.stop(stop_action='brake')
            self.right_motor.stop(stop_action='brake')

except ImportError:
    import random

    class Motors:
        def __init__(self):
            self.left_speed = 0
            self.right_speed = 0
            print("[SIM] Motors initialized (simulation mode)")

        def _clamp_speed(self, speed):
            return max(-100, min(100, speed))

        def move_forward(self, speed=SPEED_DEFAULT):
            self.left_speed = self._clamp_speed(speed)
            self.right_speed = self._clamp_speed(speed)
            print(f"[SIM] Forward: L={self.left_speed}, R={self.right_speed}")

        def move_reverse(self, speed=SPEED_DEFAULT):
            self.left_speed = self._clamp_speed(-speed)
            self.right_speed = self._clamp_speed(-speed)
            print(f"[SIM] Reverse: L={self.left_speed}, R={self.right_speed}")

        def turn_left(self, speed=SPEED_DEFAULT):
            s = self._clamp_speed(speed)
            self.left_speed = -s // 2
            self.right_speed = s
            print(f"[SIM] Turn Left: L={self.left_speed}, R={self.right_speed}")

        def turn_right(self, speed=SPEED_DEFAULT):
            s = self._clamp_speed(speed)
            self.left_speed = s
            self.right_speed = -s // 2
            print(f"[SIM] Turn Right: L={self.left_speed}, R={self.right_speed}")

        def stop(self):
            self.left_speed = 0
            self.right_speed = 0
            print("[SIM] Stopped")
