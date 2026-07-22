from config import (
    SENSOR_COLOR_PORT, SENSOR_ULTRASONIC_PORT,
    LINE_THRESHOLD, OBSTACLE_THRESHOLD_CM,
    STATE_ON_LINE, STATE_OFF_LINE, STATE_OBSTACLE
)

try:
    from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor

    class Sensors:
        def __init__(self):
            self.color_sensor = ColorSensor(SENSOR_COLOR_PORT)
            self.ultrasonic = UltrasonicSensor(SENSOR_ULTRASONIC_PORT)
            self.color_sensor.mode = 'COL-REFLECT'

        def read_color_sensor(self):
            return self.color_sensor.reflected_light_intensity

        def read_ultrasonic(self):
            return self.ultrasonic.distance_centimeters

        def get_state(self):
            dist = self.read_ultrasonic()
            if dist is not None and dist < OBSTACLE_THRESHOLD_CM:
                return STATE_OBSTACLE

            val = self.read_color_sensor()
            if val is not None and val < LINE_THRESHOLD:
                return STATE_ON_LINE
            else:
                return STATE_OFF_LINE

except ImportError:
    import random

    class Sensors:
        def __init__(self):
            self._color = 100
            self._ultrasonic = 100
            print("[SIM] Sensors initialized (simulation mode)")

        def read_color_sensor(self):
            return self._color

        def read_ultrasonic(self):
            return self._ultrasonic

        def get_state(self):
            self._ultrasonic = random.randint(5, 50)
            if self._ultrasonic < OBSTACLE_THRESHOLD_CM:
                return STATE_OBSTACLE

            self._color = random.randint(0, 100)
            if self._color < LINE_THRESHOLD:
                return STATE_ON_LINE
            else:
                return STATE_OFF_LINE

        def set_sim_values(self, color, ultrasonic=100):
            self._color = color
            self._ultrasonic = ultrasonic
