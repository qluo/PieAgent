from pathlib import Path

from PIL import Image


class FaceRenderer:
    def __init__(self, faces_dir: str = "faces") -> None:
        """Create the face renderer.

        Inputs:
        - faces_dir: folder that contains one subfolder per face state.

        Output:
        - None. Starts with no loaded frames.
        """
        self.faces_dir = faces_dir
        self.frames: dict[str, list[object]] = {}
        self.frame_indexes: dict[str, int] = {}
        self.last_drawn_state: str | None = None
        self._pygame = None
        self._screen = None

    def load(self) -> dict[str, list[object]]:
        """Load face assets from disk.

        Inputs:
        - None. Reads image files from self.faces_dir.

        Output:
        - A dictionary mapping each face state to a list of loaded frames.
          Example: {"idle": [frame1, frame2]}.

        Side effects:
        - Stores the same dictionary on self.frames.
        """
        faces_path = Path(self.faces_dir)
        self.frames = {}
        self.frame_indexes = {}

        for state_dir in sorted(path for path in faces_path.iterdir() if path.is_dir()):
            frames = [
                Image.open(png_path).convert("RGBA")
                for png_path in sorted(state_dir.glob("*.png"))
            ]
            if frames:
                self.frames[state_dir.name] = frames
                self.frame_indexes[state_dir.name] = 0

        self._setup_display()
        return self.frames

    def draw(self, state: str) -> None:
        """Draw the next frame for a face state.

        Inputs:
        - state: face state name, such as "idle", "thinking", or "speaking".

        Output:
        - None. The result appears on the display.

        Side effects:
        - Draws one frame.
        - Usually updates self.last_drawn_state and a frame index.
        """
        if not self.frames:
            self.load()

        frames = self.frames.get(state)
        if not frames:
            raise ValueError(f"No face frames loaded for state: {state}")

        frame_index = self.frame_indexes.get(state, 0)
        frame = frames[frame_index]
        self.frame_indexes[state] = (frame_index + 1) % len(frames)
        self.last_drawn_state = state

        if self._screen is not None and self._pygame is not None:
            self._draw_with_pygame(frame)

    def _setup_display(self) -> None:
        if self._screen is not None:
            return

        try:
            import pygame

            pygame.init()
            display_info = pygame.display.Info()
            width = display_info.current_w or 800
            height = display_info.current_h or 480
            self._screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
            pygame.display.set_caption("PiAgent")
            self._pygame = pygame
        except Exception:
            self._pygame = None
            self._screen = None

    def _draw_with_pygame(self, frame: Image.Image) -> None:
        pygame = self._pygame
        screen = self._screen
        if pygame is None or screen is None:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen_width, screen_height = screen.get_size()
        image = frame.copy()
        image.thumbnail((screen_width, screen_height), Image.Resampling.LANCZOS)
        surface = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
        x = (screen_width - image.width) // 2
        y = (screen_height - image.height) // 2
        screen.fill((0, 0, 0))
        screen.blit(surface, (x, y))
        pygame.display.flip()
