#!/usr/bin/env pybricks-micropython
"""Convert the trusted plain-text simulator table to EV3 MicroPython pickle.
Run on the brick from the folder containing q_table_simulated.txt and main.py.
"""
import pickle

SOURCE = 'q_table_simulated.txt'
OUTPUT = 'q_table.pkl'
EXPECTED_ENTRIES = 18

with open(SOURCE, 'r') as source_file:
    source_text = source_file.read()
namespace = {}
exec('q_table = ' + source_text, namespace)
q_table = namespace['q_table']
if len(q_table) != EXPECTED_ENTRIES:
    raise ValueError('Expected 18 Q-table entries; found %d' % len(q_table))
for key, value in q_table.items():
    if len(key) != 3 or key[0] not in (True, False):
        raise ValueError('Invalid Q-table key: %r' % (key,))
    if key[1] not in ('WHITE', 'MIDDLE', 'BLACK'):
        raise ValueError('Invalid sensor state: %r' % (key,))
    if key[2] not in ('forward', 'turn_left', 'turn_right'):
        raise ValueError('Invalid action name: %r' % (key,))
    if not isinstance(value, (int, float)):
        raise ValueError('Q-value must be numeric: %r' % (value,))
with open(OUTPUT, 'wb') as output_file:
    pickle.dump(q_table, output_file)
print('Saved %d entries to %s' % (len(q_table), OUTPUT))
