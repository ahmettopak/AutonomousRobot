from robot_controller import RobotController


if __name__ == "__main__":
    robot_controller = RobotController()
    robot_controller.start()
    try:
        robot_controller.navigate(39.740807,32.809633)
    finally:
        robot_controller.stop_navigation()
        robot_controller.stop()
