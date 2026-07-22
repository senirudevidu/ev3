import json
import random
import numpy as np
from config import (
    ALPHA, GAMMA, EPSILON, EPSILON_MIN, EPSILON_DECAY,
    NUM_STATES, NUM_ACTIONS, QTABLE_FILE
)


class QLearningAgent:
    def __init__(self):
        self.alpha = ALPHA
        self.gamma = GAMMA
        self.epsilon = EPSILON
        self.epsilon_min = EPSILON_MIN
        self.epsilon_decay = EPSILON_DECAY
        self.num_states = NUM_STATES
        self.num_actions = NUM_ACTIONS

        self.q_table = np.zeros((self.num_states, self.num_actions))

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        else:
            return int(np.argmax(self.q_table[state]))

    def update_q_table(self, state, action, reward, next_state):
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + self.alpha * (
            reward + self.gamma * max_next_q - current_q
        )
        self.q_table[state, action] = new_q

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save_q_table(self, filepath=QTABLE_FILE):
        data = {
            'q_table': self.q_table.tolist(),
            'alpha': self.alpha,
            'gamma': self.gamma,
            'epsilon': self.epsilon
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Q-table saved to {filepath}")

    def load_q_table(self, filepath=QTABLE_FILE):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.q_table = np.array(data['q_table'])
            self.alpha = data.get('alpha', ALPHA)
            self.gamma = data.get('gamma', GAMMA)
            self.epsilon = data.get('epsilon', EPSILON_MIN)
            print(f"Q-table loaded from {filepath}")
            return True
        except FileNotFoundError:
            print(f"No Q-table found at {filepath}. Starting fresh.")
            return False
        except Exception as e:
            print(f"Error loading Q-table: {e}. Starting fresh.")
            return False
