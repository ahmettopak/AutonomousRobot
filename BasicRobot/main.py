from robot_controller import RobotController
import time
if __name__ == "__main__":
    robot_controller = RobotController()
    robot_controller.start()
    try:
        while(True):

            time.sleep(1)
            #robot_controller.navigate(39.740807,32.809633)
    finally:
        robot_controller.stop_navigation()
        robot_controller.stop()
