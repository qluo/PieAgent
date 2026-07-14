import time

import pytest

from face.controller import FaceController
from face.state import FaceState


class RecordingRenderer:
    def __init__(self):
        self.load_calls = 0
        self.drawn_states = []

    def load(self):
        self.load_calls += 1

    def draw(self, state):
        self.drawn_states.append(state)


def test_controller_run_loads_once_and_draws_before_sleep(monkeypatch):
    renderer = RecordingRenderer()
    controller = FaceController(FaceState(), renderer=renderer)

    def stop_after_one_frame(_seconds):
        raise StopIteration

    monkeypatch.setattr(time, "sleep", stop_after_one_frame)

    with pytest.raises(StopIteration):
        controller.run(sleep_seconds=0.1)

    assert renderer.load_calls == 1
    assert len(renderer.drawn_states) == 1
