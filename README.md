# cleaningrobotpy
_cleaningrobotpy_ is cleaning robot, which moves in a room and cleans the dust on the floor along the way. To clean the dust, the robot is equipped with a cleaning system placed below it, consisting of two rotating brushes. When the robot is turned on, it turns on the cleaning system.

The robot moves thanks to two DC motors, one controlling its wheels and one controlling its rotation. The robot's movements are contolled by a Route Management System (RMS), which sends commands to the robot. While moving in the room, the robot can encounter obstacles; these can be detected thanks to an infrared distance sensor placed in the front of it.

The robot checks the charge left in its internal battery. To do so, it is equipped with an Intelligent Battery Sensor (IBS). Furthermore, a recharging LED is mounted on the top of the robot to signal that it needs to be recharged.

The room, where the robot moves, is represented as a rectangular grid with _x_ and _y_ coordinates. The origin cell of the grid – i.e., _(0,0)_ – is located at the bottom-left corner. A cell of the grid may contain or not an obstacle. The RMS keeps track of the room layout, including the last known positions of the obstacles in the room.

To recap, the following sensors, actuators, and systems are present:
* A DC motor to control the wheels in order to move the robot forward.
* A DC motor to control the rotation of the body of the robot, in order to make it rotate left or right.
* An RMS, sending commands to the robot.
* An infrared distance sensor used to detect obstacles.
* An IBS to determine the battery charge left.
* A recharge LED.
* A cleaning system, consisting of two rotating brushes.

The communication between the main board and the other components happens via GPIO pins (BOARD mode).

## Instructions for You
* FORK this project and make sure your forked repository is PUBLIC. Then, IMPORT the forked project into PyCharm.
* You are asked to develop _cleaningrobotpy_ by following TDD.
* You DO NOT need to develop a GUI.
* You CANNOT change the signature of the provided methods, move the provided methods to other classes, or change the name of the provided classes. However, you CAN add fields, methods (e.g., methods used by tests to set up the fixture or methods used by the provided methods), or even classes (including other test classes), as long as you comply with the provided API.
* You CAN use the internet to consult Python APIs or QA sites (e.g., StackOverflow).
* You CANNOT use AI tools (e.g., ChatGPT).
* You CANNOT interact with your colleagues. Work alone and do your best!
* The _cleaningrobotpy_ requirements are divided into a set of USER STORIES, which serve as a to-do list (see the _Issues_ session).
* You should be able to incrementally develop _cleaningrobotpy_ without an upfront comprehension of all its requirements. DO NOT read ahead, and handle the requirements (i.e., specified in the user stories) one at a time in the provided order. Develop _cleaningrobotpy_ by starting from the first story’s requirement. When a story is IMPLEMENTED, move on to the NEXT one. A story is implemented when you are confident that your program correctly implements the functionality stipulated by the story's requirement. This implies that all your test cases for that story and all the test cases for the previous stories pass. You may need to review your program as you progress toward more advanced requirements.
Each time you end a TDD phase, COMMIT.
If you need to handle error situations (including situations unspecified by the user stories), throw a ```CleaningRobotError```.

## API Usage
Take some minutes to understand, in broad terms, how the API works (i.e., see the provided classes). If you do not fully understand the API, do not worry because further details will be given in the user stories (see the _Issues_ session).

