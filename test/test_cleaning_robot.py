from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot
from src.position_state_manager import WestState


class TestCleaningRobot(TestCase):

    def setUp(self):
        self.cleaning_robot = CleaningRobot()

    def test_initialize_robot(self):
        expected_init_coordinates = "(0,0,N)"

        self.cleaning_robot.initialize_robot()

        status = self.cleaning_robot.robot_status()
        self.assertEqual(status, expected_init_coordinates)

    def test_robot_status(self):
        expected_init_coordinates = "(2,1,S)"

        self.cleaning_robot.pos_x = "2"
        self.cleaning_robot.pos_y = "1"
        self.cleaning_robot.heading = "S"
        status = self.cleaning_robot.robot_status()

        self.assertEqual(status, expected_init_coordinates)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_battery_lower_than_ten_percent(self,
                                                                   mock_gpio_output: Mock,
                                                                   mock_low_battery: Mock):
        mock_low_battery.return_value = 9

        self.cleaning_robot.manage_cleaning_system()

        expected_recharge_led_pin_call = call(self.cleaning_robot.RECHARGE_LED_PIN,
                                              GPIO.HIGH)
        expected_cleaning_system_call = call(self.cleaning_robot.CLEANING_SYSTEM_PIN,
                                             GPIO.LOW)
        mock_gpio_output.assert_has_calls(
            [expected_cleaning_system_call, expected_recharge_led_pin_call])
        self.assertFalse(self.cleaning_robot.cleaning_system_on)
        self.assertTrue(self.cleaning_robot.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_battery_greater_than_ten_percent(self,
                                                                     mock_gpio_output: Mock,
                                                                     mock_charged_battery: Mock):
        mock_charged_battery.return_value = 11

        self.cleaning_robot.manage_cleaning_system()

        expected_recharge_led_pin_call = call(self.cleaning_robot.RECHARGE_LED_PIN,
                                              GPIO.LOW)
        expected_cleaning_system_call = call(self.cleaning_robot.CLEANING_SYSTEM_PIN,
                                             GPIO.HIGH)
        mock_gpio_output.assert_has_calls(
            [expected_cleaning_system_call, expected_recharge_led_pin_call])
        self.assertTrue(self.cleaning_robot.cleaning_system_on)
        self.assertFalse(self.cleaning_robot.recharge_led_on)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_left(self, mock_charged_battery: Mock,
                                  mock_rotation_motor: Mock,
                                  mock_wheel_motor: Mock):
        mock_charged_battery.return_value = 90
        expected_new_status = "(0,0,E)"

        # Arrange status -> (0,0,N)
        self.cleaning_robot.pos_x = 0
        self.cleaning_robot.pos_y = 0
        self.cleaning_robot.heading = "N"

        command = self.cleaning_robot.LEFT
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_not_called()
        mock_rotation_motor.assert_called_once_with(command)
        self.assertEqual(new_status, expected_new_status)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(CleaningRobot, "activate_rotation_motor")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_right(self, mock_charged_battery: Mock,
                                   mock_rotation_motor: Mock,
                                   mock_wheel_motor: Mock):
        mock_charged_battery.return_value = 90
        expected_new_status = "(0,0,W)"

        self.cleaning_robot.initialize_robot()
        # Act
        command = self.cleaning_robot.RIGHT
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_not_called()
        mock_rotation_motor.assert_called_once_with(command)
        self.assertEqual(new_status, expected_new_status)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_forward_y_axis(self, mock_charged_battery: Mock,
                                            mock_wheel_motor: Mock):
        mock_charged_battery.return_value = 90
        expected_new_status = "(0,1,N)"

        self.cleaning_robot.initialize_robot()
        # Act
        command = self.cleaning_robot.FORWARD
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_forward_x_axis(self, mock_charged_battery: Mock,
                                            mock_wheel_motor: Mock):
        mock_charged_battery.return_value = 90
        expected_new_status = "(1,0,W)"

        self.cleaning_robot.initialize_robot()

        # Arrange state machine
        self.cleaning_robot.heading = "W"
        self.cleaning_robot.position_state_machine.transition_to(WestState())

        # Act
        command = self.cleaning_robot.FORWARD
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status)

    @patch.object(GPIO, "input")
    def test_obstacle_found(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True

        self.cleaning_robot.initialize_robot()
        obstacle_found = self.cleaning_robot.obstacle_found()
        # Assert
        infrared_sensor_mock.assert_called_once_with(self.cleaning_robot.INFRARED_PIN)
        self.assertTrue(obstacle_found)

    @patch.object(GPIO, "input")
    def test_obstacle_not_found(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = False

        self.cleaning_robot.initialize_robot()
        obstacle_found = self.cleaning_robot.obstacle_found()

        # Assert
        infrared_sensor_mock.assert_called_once_with(self.cleaning_robot.INFRARED_PIN)
        self.assertFalse(obstacle_found)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(GPIO, "input")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_forward_y_axis_with_obstacle(self,
                                                          mock_charged_battery: Mock,
                                                          infrared_sensor_mock: Mock,
                                                          mock_wheel_motor: Mock):
        mock_charged_battery.return_value = 90
        infrared_sensor_mock.return_value = True
        expected_new_status_with_obstacle = "(0,0,N)(0,1)"

        self.cleaning_robot.initialize_robot()

        # Act
        command = self.cleaning_robot.FORWARD
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status_with_obstacle)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(GPIO, "input")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_forward_x_axis_with_obstacle(self,
                                                          mock_charged_battery: Mock,
                                                          infrared_sensor_mock: Mock,
                                                          mock_wheel_motor: Mock):
        mock_charged_battery.return_value = 90
        infrared_sensor_mock.return_value = True
        expected_new_status_with_obstacle = "(0,0,W)(1,0)"

        self.cleaning_robot.initialize_robot()

        # Arrange state machine
        self.cleaning_robot.heading = "W"
        self.cleaning_robot.position_state_machine.transition_to(WestState())

        # Act
        command = self.cleaning_robot.FORWARD
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_called_once()
        self.assertEqual(new_status, expected_new_status_with_obstacle)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_no_battery_forward_action(self, mock_low_battery: Mock,
                                        mock_wheel_motor: Mock):
        mock_low_battery.return_value = 9
        expected_new_status_with_obstacle = "!(0,0,W)"

        self.cleaning_robot.initialize_robot()

        # Arrange state machine
        self.cleaning_robot.heading = "W"
        self.cleaning_robot.position_state_machine.transition_to(WestState())

        # Act
        command = self.cleaning_robot.FORWARD
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_not_called()
        self.assertEqual(new_status, expected_new_status_with_obstacle)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_no_battery_left_action(self, mock_low_battery: Mock,
                                                       mock_wheel_motor: Mock):
        mock_low_battery.return_value = 9
        expected_new_status_with_obstacle = "!(0,0,N)"

        # Arrange state machine
        self.cleaning_robot.initialize_robot()
        self.cleaning_robot.position_state_machine.transition_to(WestState())

        # Act
        command = self.cleaning_robot.LEFT
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_not_called()
        self.assertEqual(new_status, expected_new_status_with_obstacle)

    @patch.object(CleaningRobot, "activate_wheel_motor")
    @patch.object(IBS, "get_charge_left")
    def test_execute_command_no_battery_right_action(self, mock_low_battery: Mock,
                                                       mock_wheel_motor: Mock):
        mock_low_battery.return_value = 9
        expected_new_status_with_obstacle = "!(0,0,N)"

        # Arrange state machine
        self.cleaning_robot.initialize_robot()
        self.cleaning_robot.position_state_machine.transition_to(WestState())

        # Act
        command = self.cleaning_robot.RIGHT
        new_status = self.cleaning_robot.execute_command(command)

        # Assert
        mock_wheel_motor.assert_not_called()
        self.assertEqual(new_status, expected_new_status_with_obstacle)
