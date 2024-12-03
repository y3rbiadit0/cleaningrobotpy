from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class PositionStatus:
    pos_x: int
    pos_y: int
    heading: str
    obstacle_x: Optional[int]
    obstacle_y: Optional[int]

    def __init__(self, current_status: str):
        splitted = current_status.strip("(").strip(")").split(",")
        self.pos_x = int(splitted[0])
        self.pos_y = int(splitted[1])
        self.heading = splitted[2]
        self.obstacle_x = None
        self.obstacle_y = None

    def __str__(self):
        return f"({self.pos_x},{self.pos_y},{self.heading})"

    def get_tuple(self) -> Tuple[int, int, str]:
        return self.pos_x, self.pos_y, self.heading

    def get_tuple_with_obstacle(self) -> Tuple[int, int, str, Optional[int], Optional[int]]:
        return self.pos_x, self.pos_y, self.heading, self.obstacle_x, self.obstacle_y



class PositionStateMachineContext:
    _state = None

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def left_action(self, current_status: str) -> Tuple[int, int, str]:
        position_status = PositionStatus(current_status)
        return self._state.handle_left_action(position_status)

    def right_action(self, current_status: str) -> Tuple[int, int, str]:
        position_status = PositionStatus(current_status)
        return self._state.handle_right_action(position_status)

    def forward_action(self, current_status: str, has_obstacle_ahead: bool) -> Tuple[int, int, str, Optional[int], Optional[int]]:
        position_status = PositionStatus(current_status)
        return self._state.handle_forward_action(position_status, has_obstacle_ahead)


class State(ABC):

    @property
    def context(self) -> PositionStateMachineContext:
        return self._context

    @context.setter
    def context(self, context: PositionStateMachineContext) -> None:
        self._context = context

    @abstractmethod
    def handle_left_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        pass

    @abstractmethod
    def handle_right_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        pass

    @abstractmethod
    def handle_forward_action(self, position_status: PositionStatus, has_obstacle_ahead: bool) -> Tuple[int, int, str, Optional[int], Optional[int]]:
        pass


class NorthState(State):
    def handle_left_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(EastState())
        position_status.heading = "E"
        return position_status.get_tuple()

    def handle_right_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(WestState())
        position_status.heading = "W"
        return position_status.get_tuple()

    def handle_forward_action(self, position_status: PositionStatus, has_obstacle_ahead: bool) -> Tuple[int, int, str, Optional[int], Optional[int]]:
        if has_obstacle_ahead:
            position_status.obstacle_x = position_status.pos_x
            position_status.obstacle_y = position_status.pos_y + 1
        else:
            position_status.pos_y = position_status.pos_y + 1
        return position_status.get_tuple_with_obstacle()


class EastState(State):
    def handle_left_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(SouthState())
        position_status.heading = "S"
        return position_status.get_tuple()

    def handle_right_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(NorthState())
        position_status.heading = "N"
        return position_status.get_tuple()

    def handle_forward_action(self, position_status: PositionStatus, has_obstacle_ahead: bool) -> Tuple[int, int, str, Optional[int], Optional[int]]:
        if has_obstacle_ahead:
            position_status.obstacle_x = position_status.pos_x - 1
            position_status.obstacle_y = position_status.pos_y
        else:
            position_status.pos_x = position_status.pos_x - 1
        return position_status.get_tuple_with_obstacle()


class WestState(State):
    def handle_left_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(NorthState())
        position_status.heading = "N"
        return position_status.get_tuple()

    def handle_right_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(SouthState())
        position_status.heading = "S"
        return position_status.get_tuple()

    def handle_forward_action(self, position_status: PositionStatus, has_obstacle_ahead: bool) -> Tuple[int, int, str, Optional[int], Optional[int]]:
        if has_obstacle_ahead:
            position_status.obstacle_x = position_status.pos_x + 1
            position_status.obstacle_y = position_status.pos_y
        else:
            position_status.pos_x = position_status.pos_x + 1
        return position_status.get_tuple_with_obstacle()


class SouthState(State):
    def handle_left_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(NorthState())
        position_status.heading = "N"
        return position_status.get_tuple()

    def handle_right_action(self, position_status: PositionStatus) -> Tuple[
        int, int, str]:
        self.context.transition_to(SouthState())
        position_status.heading = "S"
        return position_status.get_tuple()

    def handle_forward_action(self, position_status: PositionStatus, has_obstacle_ahead: bool) -> Tuple[int, int, str, Optional[int], Optional[int]]:
        if has_obstacle_ahead:
            position_status.obstacle_x = position_status.pos_x
            position_status.obstacle_y = position_status.pos_y - 1
        else:
            position_status.pos_y = position_status.pos_y - 1

        return position_status.get_tuple_with_obstacle()
