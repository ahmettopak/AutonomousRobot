import pygame
from enum import Enum

class Axis(Enum):
    LEFT_X = 0
    LEFT_Y = 1
    RIGHT_X = 2
    RIGHT_Y = 3
    TRIGGER_LEFT = 4
    TRIGGER_RIGHT = 5

class Button(Enum):
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    LEFT_STICK = 8
    RIGHT_STICK = 9

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

    def get_axis(self, axis_enum):
        pygame.event.pump()
        if not isinstance(axis_enum, Axis):
            raise ValueError("Parameter must be an instance of Axis Enum")
        return self.normalize_axis(self.joystick.get_axis(axis_enum.value))

    def get_button(self, button_enum):
        pygame.event.pump()  # Event loop için gerekli, aksi takdirde pygame joystick çalışmayabilir
        if not isinstance(button_enum, Button):
            raise ValueError("Parameter must be an instance of Button Enum")
        return self.joystick.get_button(button_enum.value)
