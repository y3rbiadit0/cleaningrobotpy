import time
from typing import Optional

from .position_state_manager import PositionStateMachineContext, NorthState

DEPLOYMENT = False  # This variable is to understand whether you are deploying on the actual hardware

try:
    import RPi.GPIO as GPIO
    import board
    import IBS

    DEPLOYMENT = True
except:
    import mock.GPIO as GPIO
    import mock.board as board
    import mock.ibs as IBS


class CleaningRobot:
    RECHARGE_LED_PIN = 12
    CLEANING_SYSTEM_PIN = 13
    INFRARED_PIN = 15

    # Wheel motor pins
    PWMA = 16
    AIN2 = 18
    AIN1 = 22

    # Rotation motor pins
    BIN1 = 29
    BIN2 = 31
    PWMB = 32
    STBY = 33

    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'

    LEFT = 'l'
    RIGHT = 'r'
    FORWARD = 'f'

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN, GPIO.IN)
        GPIO.setup(self.RECHARGE_LED_PIN, GPIO.OUT)
        GPIO.setup(self.CLEANING_SYSTEM_PIN, GPIO.OUT)

        GPIO.setup(self.PWMA, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.PWMB, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.STBY, GPIO.OUT)

        ic2 = board.I2C()
        self.ibs = IBS.IBS(ic2)

        self.pos_x = None
        self.pos_y = None
        self.heading = None
        self.position_state_machine = PositionStateMachineContext(NorthState())

        self.recharge_led_on = False
        self.cleaning_system_on = False

    def initialize_robot(self) -> None:
        self.pos_x = "0"
        self.pos_y = "0"
        self.heading = "N"
        self.position_state_machine = PositionStateMachineContext(NorthState())

    def robot_status(self, obstacle_x: Optional[int] = None,
                     obstacle_y: Optional[int] = None) -> str:
        current_status = f"({self.pos_x},{self.pos_y},{self.heading})"
        if obstacle_x is not None and obstacle_y is not None:
            obstacle_pos = f"({obstacle_x},{obstacle_y})"
            return f"{current_status}{obstacle_pos}"
        return current_status

    def execute_command(self, command: str) -> str:
        current_status = self.robot_status()
        obstacle_x, obstacle_y = None, None

        if command == "f":
            has_obstacle_ahead = self.obstacle_found()
            self.activate_wheel_motor()
            self.pos_x, self.pos_y, self.heading, obstacle_x, obstacle_y = self.position_state_machine.forward_action(
                current_status, has_obstacle_ahead)
        elif command == "r":
            self.activate_rotation_motor(command)
            self.pos_x, self.pos_y, self.heading = self.position_state_machine.right_action(
                current_status)
        elif command == "l":
            self.activate_rotation_motor(command)
            self.pos_x, self.pos_y, self.heading = self.position_state_machine.left_action(
                current_status)

        return self.robot_status(obstacle_x=obstacle_x, obstacle_y=obstacle_y)

    def obstacle_found(self) -> bool:
        return GPIO.input(self.INFRARED_PIN)

    def manage_cleaning_system(self) -> None:
        charge_percentage = self.ibs.get_charge_left()
        if charge_percentage > 10:
            GPIO.output(self.CLEANING_SYSTEM_PIN, GPIO.HIGH)
            GPIO.output(self.RECHARGE_LED_PIN, GPIO.LOW)
            self.cleaning_system_on = True
            self.recharge_led_on = False
        else:
            GPIO.output(self.CLEANING_SYSTEM_PIN, GPIO.LOW)
            GPIO.output(self.RECHARGE_LED_PIN, GPIO.HIGH)
            self.cleaning_system_on = False
            self.recharge_led_on = True

    def activate_wheel_motor(self) -> None:
        """
        Let the robot move forward by activating its wheel motor
        """
        # Drive the motor clockwise
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        # Set the motor speed
        GPIO.output(self.PWMA, GPIO.HIGH)
        # Disable STBY
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)  # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.PWMA, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)

    def activate_rotation_motor(self, direction) -> None:
        """
        Let the robot rotate towards a given direction
        :param direction: "l" to turn left, "r" to turn right
        """
        if direction == self.LEFT:
            GPIO.output(self.BIN1, GPIO.HIGH)
            GPIO.output(self.BIN2, GPIO.LOW)
        elif direction == self.RIGHT:
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.HIGH)

        GPIO.output(self.PWMB, GPIO.HIGH)
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)  # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)
        GPIO.output(self.PWMB, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)


class CleaningRobotError(Exception):
    pass
