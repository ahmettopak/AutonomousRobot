import pygame
import time
import threading
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
    def __init__(self, debug=False):
        pygame.init()
        pygame.joystick.init()
        self.debug = debug
        self.joystick = None
        self.connect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 10 # in seconds
        self.reconnect_interval = 5  # seconds between each reconnect attempt
        self.running = True
        self.reconnect_thread = threading.Thread(target=self.reconnect_loop)
        self.reconnect_thread.start()
        self.init_joystick()

    def log(self, message):
        if self.debug:
            print(message)

    def init_joystick(self):
        try:
            self.joystick_count = pygame.joystick.get_count()
            if self.joystick_count > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.log(f"Gamepad connected: {self.joystick.get_name()}")
            else:
                raise RuntimeError("Gamepad not found.")
        except Exception as e:
            self.log(f"Connection error: {e}")
            self.joystick = None

    def reconnect_loop(self):
        while self.running:
            if self.joystick is None:
                self.connect_attempts = 0
                while self.joystick is None and self.connect_attempts < self.max_reconnect_attempts:
                    try:
                        self.joystick_count = pygame.joystick.get_count()
                        if self.joystick_count > 0:
                            self.joystick = pygame.joystick.Joystick(0)
                            self.joystick.init()
                            self.log(f"Gamepad connected: {self.joystick.get_name()}")
                        else:
                            raise RuntimeError("Gamepad not found.")
                    except Exception as e:
                        self.log(f"Connection error: {e}")
                        self.connect_attempts += 1
                        self.log(f"Retry attempt {self.connect_attempts}/{self.max_reconnect_attempts}...")
                        time.sleep(self.reconnect_delay)
            
            time.sleep(self.reconnect_interval)

    def check_joystick(self):
        return self.joystick is not None

    def normalize_axis(self, value):
        return int(value * 100)

    def get_axis(self, axis_enum):
        if not self.check_joystick():
            self.log("Gamepad is not initialized or not found.")
            return None
        if not isinstance(axis_enum, Axis):
            self.log("Parameter must be an instance of Axis Enum")
            return None
        pygame.event.pump()
        return self.normalize_axis(self.joystick.get_axis(axis_enum.value))

    def get_button(self, button_enum):
        if not self.check_joystick():
            self.log("Gamepad is not initialized or not found.")
            return None
        if not isinstance(button_enum, Button):
            self.log("Parameter must be an instance of Button Enum")
            return None
        pygame.event.pump()
        return self.joystick.get_button(button_enum.value)

    def quit(self):
        self.running = False
        self.reconnect_thread.join()
        if self.check_joystick():
            self.joystick.quit()
        pygame.joystick.quit()
        pygame.quit()
