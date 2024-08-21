from robot_controller import RobotController
from Joystick.gamepad import Gamepad , Axis , Button

if __name__ == "__main__":
    robot_controller = RobotController()
    robot_controller.start()
    gamepad = Gamepad()
    try:
        while(True):

            left_x = gamepad.get_axis(Axis.LEFT_X)
            left_y = gamepad.get_axis(Axis.LEFT_Y)
            right_x = gamepad.get_axis(Axis.RIGHT_X)
            right_y = gamepad.get_axis(Axis.RIGHT_Y)

            robot_controller.drive_robot_by_joystick(right_x , right_y)
            print(left_x)
    finally:
        robot_controller.stop()
