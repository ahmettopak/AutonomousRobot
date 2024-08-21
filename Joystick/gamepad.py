import pygame
import time
from enum import Enum

# Enum sınıflarını tanımlayın
class Axis(Enum):
    LEFT_X = 0
    LEFT_Y = 1
    RIGHT_X = 2
    RIGHT_Y = 3

class Button(Enum):
    A = 0
    B = 1
    X = 2
    Y = 3
    LEFT_BUMPER = 4
    RIGHT_BUMPER = 5
    BACK = 6
    START = 7
    LEFT_STICK = 8
    RIGHT_STICK = 9

# Gamepad sınıfı
class Gamepad:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Gamepad: {self.joystick.get_name()}")
        else:
            raise Exception("Gamepad bulunamadı.")

    def normalize_axis(self, value):
        return int(value * 100)

    def handle_event(self, event):
        if event.type == pygame.JOYAXISMOTION:
            axis = Axis(event.axis) if event.axis in Axis._value2member_map_ else None
            value = self.normalize_axis(self.joystick.get_axis(event.axis))
            if axis:
                print(f"Axis {axis.name}: {value}")
            else:
                print(f"Unknown Axis {event.axis}: {value}")

        elif event.type == pygame.JOYBUTTONDOWN:
            button = Button(event.button) if event.button in Button._value2member_map_ else None
            if button:
                print(f"Button {button.name} DOWN")
            else:
                print(f"Unknown Button {event.button} DOWN")

        elif event.type == pygame.JOYBUTTONUP:
            button = Button(event.button) if event.button in Button._value2member_map_ else None
            if button:
                print(f"Button {button.name} UP")
            else:
                print(f"Unknown Button {event.button} UP")

# Main sınıfı
class GamepadListener:
    def __init__(self):
        self.gamepad = Gamepad()

    def run(self):
        try:
            while True:
                for event in pygame.event.get():
                    self.gamepad.handle_event(event)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Program sonlandırıldı.")
        finally:
            pygame.quit()

# Programı başlatın
if __name__ == "__main__":
    listener = GamepadListener()
    listener.run()
