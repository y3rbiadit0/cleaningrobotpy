from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot
from src.position_state_manager import WestState


class TestCleaningRobot(TestCase):

    def test_initialize_robot(self):
        expected_init_coordinates = "(0,0,N)"
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()

        status = cleaning_robot.robot_status()
        self.assertEqual(status, expected_init_coordinates)

    def test_robot_status(self):
        expected_init_coordinates = "(2,1,S)"

        cleaning_robot = CleaningRobot()
        cleaning_robot.pos_x = "2"
        cleaning_robot.pos_y = "1"
        cleaning_robot.heading = "S"
        status = cleaning_robot.robot_status()

        self.assertEqual(status, expected_init_coordinates)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_battery_greater_than_ten_percent(self,
                                                                     mock_gpio_output: Mock,
                                                                     mock_charge: Mock):
        mock_charge.return_value = 11
        cleaning_robot = CleaningRobot()
        cleaning_robot.manage_cleaning_system()

        expected_recharge_led_pin_call = call(cleaning_robot.RECHARGE_LED_PIN, GPIO.LOW)
        expected_cleaning_system_call = call(cleaning_robot.CLEANING_SYSTEM_PIN,
                                             GPIO.HIGH)
        mock_gpio_output.assert_has_calls(
            [expected_cleaning_system_call, expected_recharge_led_pin_call])
        self.assertTrue(cleaning_robot.cleaning_system_on)
        self.assertFalse(cleaning_robot.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_battery_lower_than_ten_percent(self,
                                                                   mock_gpio_output: Mock,
                                                                   mock_charge: Mock):
        mock_charge.return_value = 9
        cleaning_robot = CleaningRobot()
        cleaning_robot.manage_cleaning_system()

        expected_recharge_led_pin_call = call(cleaning_robot.RECHARGE_LED_PIN,
                                              GPIO.HIGH)
        expected_cleaning_system_call = call(cleaning_robot.CLEANING_SYSTEM_PIN,
                                             GPIO.LOW)
        mock_gpio_output.assert_has_calls(
            [expected_cleaning_system_call, expected_recharge_led_pin_call])
        self.assertFalse(cleaning_robot.cleaning_system_on)
        self.assertTrue(cleaning_robot.recharge_led_on)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "activate_rotation_motor")
    def test_execute_command_left(self, mock_rotation_motor: Mock,
                                  mock_wheel_motor: Mock):
        expected_new_status = "(0,0,E)"
        cleaning_robot = CleaningRobot()

        # Arrange status -> (0,0,N)
        cleaning_robot.pos_x = 0
        cleaning_robot.pos_y = 0
        cleaning_robot.heading = "N"

        command = cleaning_robot.LEFT
        new_status = cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_not_called()
        mock_rotation_motor.assert_called_once_with(command)
        self.assertEqual(new_status, expected_new_status)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "activate_rotation_motor")
    def test_execute_command_right(self, mock_rotation_motor: Mock,
                                   mock_wheel_motor: Mock):
        expected_new_status = "(0,0,W)"
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()
        # Act
        command = cleaning_robot.RIGHT
        new_status = cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_not_called()
        mock_rotation_motor.assert_called_once_with(command)
        self.assertEqual(new_status, expected_new_status)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    def test_execute_command_forward_y_axis(self, mock_wheel_motor: Mock):
        expected_new_status = "(0,1,N)"
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()
        # Act
        command = cleaning_robot.FORWARD
        new_status = cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    def test_execute_command_forward_x_axis(self, mock_wheel_motor: Mock):
        expected_new_status = "(1,0,W)"
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()

        # Arrange state machine
        cleaning_robot.heading = "W"
        cleaning_robot.position_state_machine.transition_to(WestState())

        # Act
        command = cleaning_robot.FORWARD
        new_status = cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status)

    @patch.object(GPIO, "input")
    def test_obstacle_found(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()
        obstacle_found = cleaning_robot.obstacle_found()
        # Assert
        infrared_sensor_mock.assert_called_once_with(cleaning_robot.INFRARED_PIN)
        self.assertTrue(obstacle_found)

    @patch.object(GPIO, "input")
    def test_obstacle_not_found(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = False
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()
        obstacle_found = cleaning_robot.obstacle_found()

        # Assert
        infrared_sensor_mock.assert_called_once_with(cleaning_robot.INFRARED_PIN)
        self.assertFalse(obstacle_found)


    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(GPIO, "input")
    def test_execute_command_forward_y_axis_with_obstacle(self, infrared_sensor_mock: Mock, mock_wheel_motor: Mock):
        infrared_sensor_mock.return_value = True
        expected_new_status_with_obstacle = "(0,0,N)(0,1)"
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()

        # Act
        command = cleaning_robot.FORWARD
        new_status = cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status_with_obstacle)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(GPIO, "input")
    def test_execute_command_forward_x_axis_with_obstacle(self, infrared_sensor_mock: Mock, mock_wheel_motor: Mock):
        infrared_sensor_mock.return_value = True
        expected_new_status_with_obstacle = "(0,0,W)(1,0)"
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()

        # Arrange state machine
        cleaning_robot.heading = "W"
        cleaning_robot.position_state_machine.transition_to(WestState())

        # Act
        command = cleaning_robot.FORWARD
        new_status = cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status_with_obstacle)