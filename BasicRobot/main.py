from robot_controller import RobotController

if __name__ == "__main__":
    robot_controller = RobotController()
    robot_controller.start()

    try:
        robot_controller.drive_robot_by_joystick(0 , 1)
    finally:
        robot_controller.stop()
