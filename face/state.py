from threading import Lock

from face import states


class FaceState:
    def __init__(self) -> None:
        """Create shared face state.

        Inputs:
        - None.

        Output:
        - None. Starts with the "idle" state.
        """
        self._state = states.IDLE
        self._lock = Lock()

    def set(self, state: str) -> None:
        """Set the current face state.

        Inputs:
        - state: face state name, such as "idle", "listening", or "thinking".

        Output:
        - None. The new state is stored inside this object.
        """
        with self._lock:
            self._state = state

    def get(self) -> str:
        """Get the current face state.

        Inputs:
        - None.

        Output:
        - The current face state as a string.
        """
        with self._lock:
            return self._state
