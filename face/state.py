from threading import Lock

from face import states


class FaceState:
    def __init__(self):
        self._state = states.IDLE
        self._lock = Lock()

    def set(self, state: str):
        with self._lock:
            self._state = state

    def get(self) -> str:
        with self._lock:
            return self._state
