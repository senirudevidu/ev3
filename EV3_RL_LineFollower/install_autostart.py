import os
import sys
import shutil
import subprocess

SERVICE_NAME = "ev3-rl-linefollower.service"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_SRC = os.path.join(SCRIPT_DIR, SERVICE_NAME)
SERVICE_DST = os.path.join("/etc/systemd/system", SERVICE_NAME)

SERVICES_TO_DISABLE = ["brickman.service"]


def run_cmd(cmd, check=True):
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  Warning: command failed: {result.stderr.strip()}")
    return result


def install():
    print("=== Installing EV3 RL Line Follower Auto-Start ===\n")

    if os.geteuid() != 0:
        print("ERROR: This script must be run as root.")
        print("Please run: sudo python3 install_autostart.py")
        sys.exit(1)

    if not os.path.exists(SERVICE_SRC):
        print(f"ERROR: Service file not found: {SERVICE_SRC}")
        sys.exit(1)

    print("1. Stopping Brickman (EV3 default UI)...")
    for svc in SERVICES_TO_DISABLE:
        run_cmd(["systemctl", "stop", svc], check=False)
        run_cmd(["systemctl", "disable", svc], check=False)

    print("\n2. Installing service file...")
    shutil.copy2(SERVICE_SRC, SERVICE_DST)
    os.chmod(SERVICE_DST, 0o644)
    print(f"   Copied to {SERVICE_DST}")

    print("\n3. Reloading systemd...")
    run_cmd(["systemctl", "daemon-reload"])

    print("\n4. Enabling and starting service...")
    run_cmd(["systemctl", "enable", SERVICE_NAME])
    run_cmd(["systemctl", "start", SERVICE_NAME])

    print("\n=== Installation Complete ===")
    print("The EV3 RL Line Follower will now start automatically on every boot.")
    print("Use the EV3 buttons (Up/Down/Center/Back) to navigate the menu.")
    print()
    print("To disable auto-start later, run:")
    print("  sudo systemctl stop ev3-rl-linefollower.service")
    print("  sudo systemctl disable ev3-rl-linefollower.service")
    print("  sudo systemctl enable brickman.service")
    print("  sudo systemctl start brickman.service")
    print()
    print("To view logs: sudo journalctl -u ev3-rl-linefollower.service -f")


def uninstall():
    print("=== Uninstalling Auto-Start ===\n")

    if os.geteuid() != 0:
        print("ERROR: This script must be run as root.")
        sys.exit(1)

    print("1. Stopping service...")
    run_cmd(["systemctl", "stop", SERVICE_NAME], check=False)

    print("\n2. Disabling service...")
    run_cmd(["systemctl", "disable", SERVICE_NAME], check=False)

    print("\n3. Removing service file...")
    if os.path.exists(SERVICE_DST):
        os.remove(SERVICE_DST)
        print(f"   Removed {SERVICE_DST}")

    print("\n4. Reloading systemd...")
    run_cmd(["systemctl", "daemon-reload"])

    print("\n5. Restoring Brickman...")
    for svc in SERVICES_TO_DISABLE:
        run_cmd(["systemctl", "enable", svc], check=False)
        run_cmd(["systemctl", "start", svc], check=False)

    print("\n=== Uninstall Complete ===")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    else:
        install()
