from abc import ABC, abstractmethod
from collections import deque
from enum import Enum


class Rank(Enum):
    """Enum to define employee ranks."""
    OPERATOR = 0
    SUPERVISOR = 1
    DIRECTOR = 2


class CallState(Enum):
    """Enum to define call states."""
    READY = 0
    IN_PROGRESS = 1
    COMPLETE = 2


class Call:
    """Represents a call object."""

    def __init__(self, rank: Rank):
        self.state: CallState = CallState.READY
        self.rank: Rank = rank
        self.employee: 'Employee' = None


class Employee(ABC):
    """Abstract base class for all employees."""

    def __init__(self, employee_id: int, name: str, rank: Rank, call_center: 'CallCenter'):
        self.employee_id = employee_id
        self.name = name
        self.rank = rank
        self.call: Call = None
        self.call_center = call_center

    def take_call(self, call: Call) -> None:
        """Assign the given call to this employee."""
        self.call = call
        self.call.employee = self
        self.call.state = CallState.IN_PROGRESS

    def complete_call(self) -> None:
        """Mark the current call as completed."""
        self.call.state = CallState.COMPLETE
        self.call_center.notify_call_completed(self.call)

    @abstractmethod
    def escalate_call(self) -> None:
        """Abstract method for escalating a call to higher rank."""
        pass

    def _escalate_call(self) -> None:
        """Internal method to escalate a call."""
        self.call.state = CallState.READY
        call = self.call
        self.call = None
        self.call_center.notify_call_escalated(call)


class Operator(Employee):
    """Represents an Operator, lowest rank of employee."""

    def __init__(self, employee_id: int, name: str, call_center: 'CallCenter'):
        super().__init__(employee_id, name, Rank.OPERATOR, call_center)

    def escalate_call(self) -> None:
        """Escalate the call to a Supervisor."""
        self.call.rank = Rank.SUPERVISOR
        self._escalate_call()


class Supervisor(Employee):
    """Represents a Supervisor, mid rank of employee."""

    def __init__(self, employee_id: int, name: str, call_center: 'CallCenter'):
        super().__init__(employee_id, name, Rank.SUPERVISOR, call_center)

    def escalate_call(self) -> None:
        """Escalate the call to a Director."""
        self.call.rank = Rank.DIRECTOR
        self._escalate_call()


class Director(Employee):
    """Represents a Director, highest rank of employee."""

    def __init__(self, employee_id: int, name: str, call_center: 'CallCenter'):
        super().__init__(employee_id, name, Rank.DIRECTOR, call_center)

    def escalate_call(self) -> None:
        """Directors cannot escalate calls further."""
        raise NotImplementedError('Directors must be able to handle any call')


class CallCenter:
    """Represents the Call Center with operators, supervisors, and directors."""

    def __init__(self, operators: list[Operator], supervisors: list[Supervisor], directors: list[Director]):
        self.operators = operators
        self.supervisors = supervisors
        self.directors = directors
        self.queued_calls: deque[Call] = deque()

    def dispatch_call(self, call: Call) -> None:
        """Route the call to the appropriate employee based on rank."""
        if call.rank not in (Rank.OPERATOR, Rank.SUPERVISOR, Rank.DIRECTOR):
            raise ValueError(f'Invalid call rank: {call.rank}')
        employee = self._dispatch_call_based_on_rank(call)
        if not employee:
            self.queued_calls.append(call)

    def _dispatch_call_based_on_rank(self, call: Call) -> 'Employee':
        """Find an available employee for the call based on its rank."""
        if call.rank == Rank.OPERATOR:
            return self._dispatch_to_available(call, self.operators)
        elif call.rank == Rank.SUPERVISOR:
            return self._dispatch_to_available(call, self.supervisors) or self._dispatch_to_available(call,
                                                                                                      self.operators)
        elif call.rank == Rank.DIRECTOR:
            return self._dispatch_to_available(call, self.directors) or self._dispatch_to_available(call,
                                                                                                    self.supervisors) or self._dispatch_to_available(
                call, self.operators)
        return None

    @staticmethod
    def _dispatch_to_available(call: Call, employees: list['Employee']) -> 'Employee':
        """Send the call to the first available employee in the list."""
        for employee in employees:
            if employee.call is None:
                employee.take_call(call)
                return employee
        return None

    def notify_call_escalated(self, call: Call) -> None:
        """Placeholder for actions to be taken when a call is escalated."""
        pass

    def notify_call_completed(self, call: Call) -> None:
        """Placeholder for actions to be taken when a call is completed."""
        pass

    def dispatch_queued_call_to_newly_freed_employee(self, call: Call, employee: 'Employee') -> None:
        """Placeholder for dispatching queued calls when an employee becomes available."""
        pass
