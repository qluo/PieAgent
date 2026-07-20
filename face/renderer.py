from pathlib import Path

from PIL import Image
import pygame


class FaceRenderer:
    def __init__(self, faces_dir: str = "faces") -> None:
        """Create the face renderer.

        Inputs:
        - faces_dir: top-level folder that contains one subfolder per face
          state, such as faces/idle and faces/thinking. Change this only when
          your face image folders live somewhere other than faces/.

        Output:
        - None. Starts with no loaded frames.
        """
        # This tells load() where to look for the state picture folders.
        self.faces_dir = faces_dir
        # load() fills this with a list of image frames for each state name.
        self.frames: dict[str, list[object]] = {}
        # draw() uses these positions to show each state's frames in order.
        self.frame_indexes: dict[str, int] = {}
        # Tests and debugging can inspect the most recently requested state.
        self.last_drawn_state: str | None = None
        # _setup_display() stores the pygame module here when display setup works.
        self._pygame: object | None = None
        # _setup_display() stores pygame's fullscreen window here for drawing.
        self._screen: object | None = None

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
        # Lesson 2: Face Renderer
        #
        # Goal:
        # Load the Mini panda bot PNG files from the faces/ folders.
        #
        # Suggested packages:
        # - pathlib: find image files in folders.
        # - Pillow: load PNG files if you render with Pillow/Tkinter.
        # - pygame: load PNG files if you render with pygame.
        #
        # Concept to learn:
        # Each folder name is a face state. Each PNG inside that folder is one
        # animation frame for that state.
        #
        # Implementation guide:
        # 1. Turn self.faces_dir into a Path so Python can inspect the folders.
        # 2. Start with empty self.frames and self.frame_indexes dictionaries.
        # 3. Visit each subfolder inside the faces directory. The folder name is
        #    the state name, for example "idle" or "thinking".
        # 4. Find that folder's PNG files and sort them so animation always
        #    starts in the same order.
        # 5. Open each PNG with Pillow and convert it to RGBA so pygame can
        #    draw it later.
        # 6. Save the list of frames under self.frames[state_name], and set
        #    self.frame_indexes[state_name] to 0.
        # 7. Set up the display once, then return self.frames.
        #
        # Expected result:
        # After load() runs, draw("thinking") can find thinking frames.
        return


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
        # Lesson 2: Face Renderer
        #
        # Goal:
        # Show the next PNG frame for the requested state.
        #
        # Suggested package:
        # - pygame: good for fullscreen display on Raspberry Pi.
        #
        # Concept to learn:
        # Animation is just showing images in order:
        # frame 1, frame 2, frame 3, then back to frame 1.
        #
        # Implementation guide:
        # 1. Load frames first when self.frames is empty.
        # 2. Look up the requested state's frames and report a useful error
        #    when the state has no images.
        # 3. Use the state's current frame index, then draw that frame with the
        #    provided _draw_with_pygame() helper when a display is available.
        # 4. Advance the index with modulo so it wraps after the last frame.
        # 5. Store self.last_drawn_state = state for tests and debugging.
        #
        # Expected return value:
        # Nothing. The result appears on the display.
        return


    def _draw_with_pygame(self, frame: object) -> None:
        """Draw one frame with pygame when a display is available."""
        # Lesson 2 helper: draw one already-loaded frame with pygame.
        #
        # Goal:
        # Take one image frame and show it on the pygame screen.
        #
        # This provided helper keeps the pygame window responsive, turns a
        # Pillow image into a pygame surface, centers it on the screen, and
        # flips the display so the new face becomes visible.
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
        return

    def _setup_display(self) -> None:
        """Prepare pygame for drawing face images.

        This helper is separated for students: Lesson 2 can first load images,
        then fill in the display setup, then fill in drawing.
        """
        try:
            pygame.init()
            self._pygame = pygame
            if self._screen is None:
                self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except Exception:
            # Tests and laptops may not have a real display. Keep loaded frames
            # usable so students can still test the code before moving to the Pi.
            self._pygame = None
            self._screen = None
        return
