from robot_controller import RobotController
import time
if __name__ == "__main__":
    robot_controller = RobotController()
    robot_controller.start()
    try:
        while(True):
            time.sleep(1)
    finally:
        robot_controller.stop_navigation()
        robot_controller.stop()
