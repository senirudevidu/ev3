import time
from config import (
    EPISODES, EPISODE_TIMEOUT, SPEED_DEFAULT,
    STATE_OBSTACLE, STATE_ON_LINE,
    REWARD_COLLISION
)
from robot import Robot
from q_learning import QLearningAgent


def train():
    robot = Robot()
    agent = QLearningAgent()

    agent.load_q_table()

    print("=== Training Started ===")

    for episode in range(1, EPISODES + 1):
        robot.stop()
        time.sleep(1)

        total_reward = 0
        step_count = 0
        done = False

        state = robot.get_state()

        start_time = time.time()

        while not done:
            if robot.is_obstacle_detected():
                print("  Obstacle detected! Avoiding...")
                robot.avoid_obstacle()
                robot.find_line()
                agent.update_q_table(state, agent.choose_action(state),
                                     REWARD_COLLISION, robot.get_state())
                state = robot.get_state()
                continue

            action = agent.choose_action(state)
            robot.execute_action(action, SPEED_DEFAULT)

            next_state = robot.get_state()
            reward = robot.calculate_reward(next_state)
            total_reward += reward

            agent.update_q_table(state, action, reward, next_state)

            state = next_state
            step_count += 1

            elapsed = time.time() - start_time
            if elapsed > EPISODE_TIMEOUT:
                done = True

            if state == STATE_ON_LINE and step_count > 5:
                if total_reward > 0:
                    done = True

            if state == STATE_OBSTACLE:
                done = True

        agent.decay_epsilon()

        if episode % 10 == 0 or episode == 1 or episode == EPISODES:
            print(f"Episode {episode}/{EPISODES}")
            print(f"  Total Reward: {total_reward}")
            print(f"  Steps: {step_count}")
            print(f"  Epsilon: {agent.epsilon:.4f}")
            print()

    agent.save_q_table()
    print("=== Training Complete ===")
    return agent


if __name__ == '__main__':
    train()
