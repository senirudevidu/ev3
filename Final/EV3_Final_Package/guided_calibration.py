#!/usr/bin/env pybricks-micropython
"""Measure three surfaces at normal sensor height; no motors are initialized."""
import json
from pybricks.ev3devices import ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button, Port
from pybricks.tools import wait

brick = EV3Brick()
sensor = ColorSensor(Port.S1)
results = {}
for label in ('dark_background', 'yellow_tape', 'tape_edge'):
    brick.screen.clear()
    brick.screen.print(label)
    brick.screen.print('Position sensor')
    brick.screen.print('Center to sample')
    print('PLACE SENSOR:', label)
    while Button.CENTER not in brick.buttons.pressed():
        wait(20)
    while Button.CENTER in brick.buttons.pressed():
        wait(20)
    wait(300)
    samples = []
    for i in range(20):
        samples.append(sensor.reflection())
        wait(100)
    ordered = sorted(samples)
    results[label] = {'samples': samples, 'min': min(samples),
                      'max': max(samples), 'median': (ordered[9] + ordered[10]) / 2}
    print(label, results[label])
    brick.speaker.beep()
with open('calibration.json', 'w') as target:
    json.dump(results, target)
brick.screen.clear()
brick.screen.print('Calibration saved')
print('CALIBRATION_COMPLETE', results)
