import time
from config import (
    EPSILON_MIN, SPEED_DEFAULT,
    STATE_OBSTACLE
)
from robot import Robot
from q_learning import QLearningAgent


def test():
    robot = Robot()
    agent = QLearningAgent()

    loaded = agent.load_q_table()
    if not loaded:
        print("No trained Q-table found. Train the robot first.")
        return

    agent.epsilon = 0.0

    print("=== Testing Started (Autonomous Mode) ===")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            if robot.is_obstacle_detected():
                print("Obstacle! Running avoidance routine.")
                robot.avoid_obstacle()
                found = robot.find_line()
                if found:
                    print("Line re-acquired. Resuming RL policy.")
                else:
                    print("Line lost! Searching...")
                continue

            state = robot.get_state()

            if state == STATE_OBSTACLE:
                print("Obstacle in state! Avoiding.")
                robot.avoid_obstacle()
                robot.find_line()
                continue

            action = agent.choose_action(state)

            robot.execute_action(action, SPEED_DEFAULT)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nTesting stopped by user.")
    finally:
        robot.stop()
        print("Robot stopped.")


if __name__ == '__main__':
    test()
