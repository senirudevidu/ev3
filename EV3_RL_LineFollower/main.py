import sys
import time
from train import train
from test import test

try:
    from ev3dev2.button import Button
    from ev3dev2.display import Display
    from ev3dev2.fonts import load

    class EV3Menu:
        def __init__(self):
            self.btn = Button()
            self.disp = Display()
            self.selected = 0
            self.status = ""

        def draw_menu(self):
            self.disp.clear()
            self.disp.text_pixels("EV3 RL Line Follower", x=10, y=5, font='helvR10')
            self.disp.text_pixels("=" * 28, x=10, y=18, font='helvR10')
            items = ["1. Train", "2. Test", "3. Exit"]
            for i, item in enumerate(items):
                y = 40 + i * 20
                prefix = ">" if i == self.selected else " "
                self.disp.text_pixels(f"{prefix} {item}", x=20, y=y, font='helvR12')
            if self.status:
                self.disp.text_pixels(self.status, x=10, y=110, font='helvR10')
            self.disp.update()

        def show_status(self, text):
            self.status = text
            self.draw_menu()

        def run(self):
            while True:
                self.draw_menu()
                button = self.btn.wait_for_bump(['up', 'down', 'enter', 'backspace'])
                if button == 'up':
                    self.selected = (self.selected - 1) % 3
                    self.status = ""
                elif button == 'down':
                    self.selected = (self.selected + 1) % 3
                    self.status = ""
                elif button == 'enter':
                    if self.selected == 0:
                        self.show_status("Training...")
                        train()
                        self.show_status("Training done!")
                    elif self.selected == 1:
                        self.show_status("Testing...")
                        test()
                        self.show_status("Test done!")
                    elif self.selected == 2:
                        self.disp.clear()
                        self.disp.text_pixels("Goodbye!", x=45, y=55, font='helvR14')
                        self.disp.update()
                        time.sleep(1.5)
                        self.disp.clear()
                        self.disp.update()
                        return
                elif button == 'backspace':
                    self.disp.clear()
                    self.disp.update()
                    return

    def main():
        menu = EV3Menu()
        menu.run()

except ImportError:
    EV3_MENU_AVAILABLE = False

    def show_menu():
        print("\n" + "=" * 40)
        print("  EV3 RL Line Follower Robot")
        print("=" * 40)
        print("  1. Train robot")
        print("  2. Test trained robot")
        print("  3. Exit")
        print("=" * 40)

    def main():
        while True:
            show_menu()
            choice = input("Select option (1-3): ").strip()
            if choice == '1':
                print("\nStarting training...\n")
                train()
                print("\nTraining finished!\n")
            elif choice == '2':
                print("\nStarting test...\n")
                test()
                print("\nTest finished!\n")
            elif choice == '3':
                print("Exiting. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid option. Please enter 1, 2, or 3.")


if __name__ == '__main__':
    main()
