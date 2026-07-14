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
        self.frames: dict[str, list[object]] = {}
        self.frame_indexes: dict[str, int] = {}
        self.last_drawn_state: str | None = None
        self._pygame: object | None = None
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
        # Small first step:
        # Build a dictionary like:
        #   self.frames["thinking"] = [image1, image2, image3]
        #
        # Expected result:
        # After load() runs, draw("thinking") can find thinking frames.
        return self.frames

    def _setup_display(self) -> None:
        """Prepare pygame for drawing face images.

        This helper is separated for students: Lesson 2 can first load images,
        then fill in the display setup, then fill in drawing.
        """
        try:
            import pygame

            pygame.init()
            self._pygame = pygame
            if self._screen is None:
                self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except Exception:
            # Tests and laptops may not have a real display. Keep loaded frames
            # usable so students can still test the code before moving to the Pi.
            self._pygame = None
            self._screen = None

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
        # Small first step:
        # Draw the first image for the state without animation.
        #
        # Real version idea:
        # 1. If the display is not ready yet, call self._setup_display().
        # 2. Look up the frame list for state.
        # 3. Keep a frame index for each state.
        # 4. Get the current frame.
        # 5. Call self._draw_with_pygame(frame).
        # 6. Move the frame index forward.
        # 7. Store self.last_drawn_state = state so your test can check it.
        #
        # Expected return value:
        # Nothing. The result appears on the display.
        pass

    def _draw_with_pygame(self, frame: object) -> None:
        """Draw one frame with pygame when a display is available."""
        # Lesson 2 helper: draw one already-loaded frame with pygame.
        #
        # Goal:
        # Take one image frame and show it on the pygame screen.
        #
        # Suggested steps:
        # 1. If self._pygame or self._screen is missing, return early.
        # 2. Read pygame events so the display stays responsive.
        # 3. Convert the frame into a pygame surface.
        # 4. Scale the surface to fit the screen.
        # 5. Blit the surface onto the screen.
        # 6. Call pygame.display.flip() to show the new frame.
        pass
