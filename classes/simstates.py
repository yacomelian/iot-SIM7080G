

from __future__ import annotations
from abc import ABC, abstractmethod
from classes import simcom


class Context:
    """
    The Context defines the interface of interest to clients. It also maintains
    a reference to an instance of a State subclass, which represents the current
    state of the Context.
    """

    _state = None
    """
    A reference to the current state of the Context.
    """

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        """
        The Context allows changing the State object at runtime.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    """
    The Context delegates part of its behavior to the current State object.
    """
    def run(self):
        self._state.run()

    def request1(self):
        self._state.run()

    def request2(self):
        self._state.next()   


class State(ABC):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object,
    associated with the State. This backreference can be used by States to
    transition the Context to another State.
    """
    def __init__(self):
         self.sim = simcom(None)

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def next(self) -> None:
        pass

class powerOff(State):
    def run(self) -> None:
        print("powerOff run request1." + __name__)

    def next(self) -> None:
        print("ConcreteStateB handles request2.")
        print("ConcreteStateB wants to change the state of the context.")
        self.context.transition_to(powerOn())

class powerOn(State):
    def run(self) -> None:
        print("powerOn run request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(powerOff())

    def next(self) -> None:
        print("powerOn handles request2.")

class simUnlock(State):
    def run(self) -> None:
        print("powerOn handles request1.")
        print("ConcreteStateA wants to change the state of the context.")
        self.context.transition_to(powerOff())

    def next(self) -> None:
        print("powerOn handles request2.")

class simConnect(State):
    def run(self) -> None:
        print("Connect.")
        print("ConcreteStateA wants to change the state of the context.")
        def next(self) -> None:
            print("Idle - Waiting for commands")


if __name__ == "__main__":
    # The client code.
    context = Context(powerOff())
    context.request1()
    context.request2()