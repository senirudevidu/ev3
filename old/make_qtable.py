#!/usr/bin/env pybricks-micropython

import pickle


def main():
    with open('q_table.pkl', 'r') as f:
        src = f.read()
    namespace = {}
    exec('q_table = ' + src, namespace)
    q_table = namespace['q_table']
    with open('q_table.pkl', 'wb') as f:
        pickle.dump(q_table, f)
    print('saved', len(q_table), 'entries')


main()
