from unittest import TestCase
from unittest.mock import Mock, patch, call, PropertyMock

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


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
    def test_manage_cleaning_system_battery_greater_than_ten_percent(self, mock_gpio_output: Mock, mock_charge: Mock):
        mock_charge.return_value = 11
        cleaning_robot = CleaningRobot()
        cleaning_robot.manage_cleaning_system()

        expected_recharge_led_pin_call = call(cleaning_robot.RECHARGE_LED_PIN, GPIO.LOW)
        expected_cleaning_system_call = call(cleaning_robot.CLEANING_SYSTEM_PIN, GPIO.HIGH)
        mock_gpio_output.assert_has_calls([expected_cleaning_system_call, expected_recharge_led_pin_call])
        self.assertTrue(cleaning_robot.cleaning_system_on)
        self.assertFalse(cleaning_robot.recharge_led_on)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "output")
    def test_manage_cleaning_system_battery_greater_than_ten_percent(self, mock_gpio_output: Mock, mock_charge: Mock):
        mock_charge.return_value = 9
        cleaning_robot = CleaningRobot()
        cleaning_robot.manage_cleaning_system()

        expected_recharge_led_pin_call = call(cleaning_robot.RECHARGE_LED_PIN, GPIO.HIGH)
        expected_cleaning_system_call = call(cleaning_robot.CLEANING_SYSTEM_PIN, GPIO.LOW)
        mock_gpio_output.assert_has_calls([expected_cleaning_system_call, expected_recharge_led_pin_call])
        self.assertFalse(cleaning_robot.cleaning_system_on)
        self.assertTrue(cleaning_robot.recharge_led_on)







