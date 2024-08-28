from robot_controller import RobotController
from Joystick.gamepad import Gamepad , Axis , Button
import asyncio

async def main():
    robot_controller = RobotController()
    gamepad = Gamepad()
    
    await robot_controller.start()
    
    try:
        while True:
            left_x = gamepad.get_axis(Axis.LEFT_X)
            left_y = gamepad.get_axis(Axis.LEFT_Y)
            right_x = gamepad.get_axis(Axis.RIGHT_X)
            right_y = gamepad.get_axis(Axis.RIGHT_Y)
            
            await robot_controller.navigate(5, 3)
            #await robot_controller.drive_robot_by_joystick(right_x, right_y)
            
            await asyncio.sleep(0.1)  # Stabilite için uyuma süresi
    except KeyboardInterrupt:
        # Program kesildiğinde robotu durdurma
        pass
    finally:
        robot_controller.stop()

# Asenkron fonksiyonu çalıştır
asyncio.run(main())