# User Story #6 -- Add Temperature Safety Check

**Before executing a command to move the robot**, the robot checks its internal temperature using the temperature sensor. 
If the temperature exceeds the defined safe limit (70°C), the robot raises an exception to 
prevent damage (User Story #5) and it won't run any engine. 
In this case, the exception contains an error message indicating the current temperature. No further commands are executed until the issue is resolved.

---

## Requirement

Update the implementation of `CleaningRobot.execute_command(command: str) -> str` to include a temperature check before performing any action.

1. **If the temperature is within the safe range:**
    - Proceed with the normal execution of the command.

2. **If the temperature exceeds the threshold:**
    - Do nothing and Raise a `CleaningRobotError` with a descriptive message about the temperature issue.

---

## Example

Suppose the current temperature of the robot exceeds 70°C, and the status of the robot is `(2,3,E)`.
If the robot receives the command `f`, it stops all motors and raises an exception with the following message:  
`"Temperature exceeded safe limit! Current: 75°C"`

If the temperature is within the safe range, the command proceeds as usual.
