# EV3 RL Line Follower

A reinforcement learning (Q-learning) line-following robot for LEGO Mindstorms EV3.

## Project Structure

```
EV3_RL_LineFollower/
├── main.py                       # Main menu with EV3 button navigation
├── robot.py                      # High-level Robot class
├── motors.py                     # Motor control (differential drive)
├── sensors.py                    # Sensor reading and state encoding
├── q_learning.py                 # Q-learning algorithm
├── train.py                      # Training program
├── test.py                       # Autonomous testing
├── config.py                     # Configuration constants
├── ev3-rl-linefollower.service   # Systemd unit for auto-start
├── install_autostart.py          # One-time setup script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Hardware Setup

- **Motors**: Two Large Motors on ports B (left) and C (right)
- **Color Sensor**: One EV3 Color Sensor on port IN-1, mode COL-REFLECT
- **Ultrasonic Sensor**: One EV3 Ultrasonic Sensor on port IN-2

### Sensor Placement

```
        Direction →

          [Sensor]

          BLACK LINE

       Wheel     Wheel
```

The color sensor is positioned directly over the black line.

## SD Card Setup

### 1. Prepare the SD Card

Format a microSD card as **FAT32**. The EV3 boots ev3dev from this card.

### 2. SD Card Structure

Copy all files so the SD card root looks like this:

```
SD_CARD_ROOT/
├── boot.scr                       # EV3 bootloader
├── u-boot.bin                     # EV3 bootloader
├── uEnv.txt                       # Boot configuration
└── EV3_RL_LineFollower/           # Python project
    ├── main.py
    ├── robot.py
    ├── motors.py
    ├── sensors.py
    ├── q_learning.py
    ├── train.py
    ├── test.py
    ├── config.py
    ├── ev3-rl-linefollower.service
    ├── install_autostart.py
    ├── requirements.txt
    └── README.md
```

The boot files (`uEnv.txt`, `boot.scr`, `u-boot.bin`) must be at the root. The `EV3_RL_LineFollower/` folder goes alongside them.

### 3. Insert & Boot

1. Insert the SD card into the EV3 brick.
2. Power on the EV3.
3. ev3dev Linux boots automatically from the SD card.
4. By default, the Brickman UI appears. You'll need a one-time setup (see below).

### 4. One-Time Setup (SSH over USB required)

After first boot, connect your PC to the EV3 via **USB cable** and SSH in:

```bash
ssh robot@192.168.10.1
```
Default password: `maker`

#### a. Install dependencies

```bash
sudo apt-get update
sudo apt-get install python3-ev3dev2 python3-numpy
```

#### b. Install auto-start

```bash
cd EV3_RL_LineFollower
sudo python3 install_autostart.py
```

This does three things:
1. Stops and disables **Brickman** (the default EV3 UI) to avoid screen conflicts
2. Installs `ev3-rl-linefollower.service` as a systemd service
3. Enables and starts the service

**After this, the menu launches automatically on every boot.**

## Usage

### Auto-Start (Normal Operation)

1. Insert SD card → power on
2. The program starts automatically
3. EV3 screen shows the menu:

```
EV3 RL Line Follower
============================
 > 1. Train
   2. Test
   3. Exit
```

4. Navigate with the EV3 buttons:

| Button   | Action          |
|----------|-----------------|
| Up       | Move selection up |
| Down     | Move selection down |
| Center   | Confirm selection  |
| Back     | Exit program       |

### Training

Select **1. Train**. The robot runs 200 episodes, learning by trial and error. Status shows on the screen. The Q-table is saved to `qtable.json`.

### Testing

Select **2. Test**. Loads `qtable.json`, disables exploration (epsilon = 0), and runs autonomously.

### Manual Run (via SSH)

```bash
cd EV3_RL_LineFollower
python3 test.py       # test only
python3 train.py      # train only
python3 main.py       # full menu (keyboard input mode)
```

### Disabling Auto-Start

To restore the original Brickman UI:

```bash
sudo python3 install_autostart.py uninstall
```

## How It Works

### Q-Learning

- **States** (3): On line, off line, obstacle detected
- **Actions** (4): Forward, Reverse, Turn Left, Turn Right
- **Rewards**: Positive for staying on line and correct turns, negative for losing line or collision

The robot learns through trial and error, updating its Q-table after each action.

### Obstacle Avoidance

Obstacle detection uses the ultrasonic sensor (non-RL logic):
1. If obstacle detected, robot reverses
2. Rotates in a random direction
3. Searches for the black line
4. Returns control to RL policy

## Configuration

Edit `config.py` to adjust:
- Motor ports and sensor ports
- Speed settings
- Learning parameters (alpha, gamma, epsilon)
- Training episodes
- Reward values
