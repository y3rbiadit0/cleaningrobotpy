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


