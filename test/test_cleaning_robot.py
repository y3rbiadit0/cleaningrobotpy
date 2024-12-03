from unittest import TestCase
from unittest.mock import Mock, patch, call, PropertyMock

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


class TestCleaningRobot(TestCase):

    @patch.object(GPIO, "input")
    def test_initialize_robot(self, mock_object: Mock):

        expected_init_coordinates = "(0,0,N)"
        cleaning_robot = CleaningRobot()
        cleaning_robot.initialize_robot()

        status = cleaning_robot.robot_status()
        self.assertEqual(status, expected_init_coordinates)


