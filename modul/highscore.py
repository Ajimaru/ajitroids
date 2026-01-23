"""Highscore persistence and UI helpers."""

import json
import os
import random
import pygame
import modul.constants as C
try:
    from modul.i18n import gettext
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback when i18n unavailable
    def gettext(key):
        """
        Return the translation for the given key using a fallback that returns the key unchanged when i18n is unavailable.
        
        Parameters:
            key (str): Translation key to look up.
        
        Returns:
            str: The original `key`.
        """
        return key


class HighscoreManager:
    """Manage loading, saving and querying highscores."""

    def _generate_default_highscores(self):
        """
        Generate a default highscore list containing C.HIGHSCORE_MAX_ENTRIES entries.
        
        Each entry is a dict with:
        - "name": a randomly generated string of length C.HIGHSCORE_NAME_LENGTH using characters from C.HIGHSCORE_ALLOWED_CHARS.
        - "score": an integer score starting at C.HIGHSCORE_MAX_ENTRIES * 1000 and decreasing by 1000 for each subsequent entry.
        
        Returns:
            list[dict]: The generated list of highscore entries ordered from highest to lowest score.
        """
        return [
            {
                "name": "".join(random.choice(C.HIGHSCORE_ALLOWED_CHARS) for _ in range(C.HIGHSCORE_NAME_LENGTH)),
                "score": (C.HIGHSCORE_MAX_ENTRIES - i) * 1000,
            }
            for i in range(C.HIGHSCORE_MAX_ENTRIES)
        ]

    def __init__(self):
        """Initialize highscore manager and load persisted highscores."""
        self.highscores = []
        self.load_highscores()

    def load_highscores(self):
        """
        Load highscores from disk, or create and persist default entries if no file exists.
        
        If the highscores file is present, replace self.highscores with its parsed JSON content.
        If the file is missing, generate default highscores, assign them to self.highscores, and save them.
        On file I/O or JSON parse errors, print the error and fall back to generated default highscores.
        """
        try:
            if os.path.exists(C.HIGHSCORE_FILE):
                with open(C.HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                    self.highscores = json.load(f)
            else:
                self.highscores = self._generate_default_highscores()
                self.save_highscores()
        except (OSError, json.JSONDecodeError) as e:  # fallback for file/parse errors
            print(f"Error loading highscores: {e}")
            # Fallback: generate entries using the same logic as the default
            # initialization so names and scores are consistent.
            self.highscores = self._generate_default_highscores()

    def save_highscores(self):
        """
        Write the current highscores to the configured highscores file as JSON.
        
        On failure to write the file, prints an error message describing the I/O problem and does not raise.
        """
        try:
            with open(C.HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.highscores, f)
        except OSError as e:  # fallback for file write errors
            print(f"Error saving highscores: {e}")

    def is_highscore(self, score):
        """
        Determine whether a score qualifies for the highscore list.
        
        Returns:
            True if there are fewer than the maximum allowed entries or the score is greater than the lowest recorded highscore, False otherwise.
        """
        if len(self.highscores) < C.HIGHSCORE_MAX_ENTRIES:
            return True
        return score > self.highscores[-1]["score"]

    def add_highscore(self, name, score):
        """
        Add a new highscore and persist the updated list.
        
        The provided name is normalized (uppercased, filtered to allowed characters, truncated to C.HIGHSCORE_NAME_LENGTH, and padded with "A" if shorter). The score is inserted, the list is sorted by score descending, truncated to C.HIGHSCORE_MAX_ENTRIES, and saved.
        
        Parameters:
            name (str): Player name to record; will be normalized as described above.
            score (int): Score value to record.
        
        Returns:
            index (int): Index of the newly added entry in the sorted highscores, or -1 if the entry was not found after insertion.
        """
        name = name.upper()[:C.HIGHSCORE_NAME_LENGTH]
        name = "".join(c for c in name if c in C.HIGHSCORE_ALLOWED_CHARS)
        name = name.ljust(C.HIGHSCORE_NAME_LENGTH, "A")

        self.highscores.append({"name": name, "score": score})
        self.highscores.sort(key=lambda x: x["score"], reverse=True)
        self.highscores = self.highscores[:C.HIGHSCORE_MAX_ENTRIES]
        self.save_highscores()

        for i, entry in enumerate(self.highscores):
            if entry["name"] == name and entry["score"] == score:
                return i
        return -1


class HighscoreInput:
    """Handles input for entering highscore name."""
    def __init__(self, score):
        """
        Create a HighscoreInput for entering a name for the given score.
        
        Initializes the editable name to a list of "A" characters with length C.HIGHSCORE_NAME_LENGTH, sets the current cursor position to 0, and prepares the input font.
        
        Parameters:
            score (int): The score to display and associate with the entered name.
        """
        self.score = score
        # Initialize name with configured length so tests and runtime honour
        # the `HIGHSCORE_NAME_LENGTH` constant.
        self.name = ["A"] * C.HIGHSCORE_NAME_LENGTH
        self.current_pos = 0
        self.done = False
        self.font = pygame.font.Font(None, 64)

    def update(self, events):
        """
        Process pygame key events to update the highscore name entry and cursor.
        
        Updates the current character or the cursor position in response to arrow and backspace keys,
        cycles the character at the cursor with Up/Down, and marks the entry as completed when Return is pressed.
        
        Parameters:
            events (iterable): An iterable of pygame events to handle.
        
        Returns:
            str: The entered name when the user confirms with Return.
            None: If the entry has not been confirmed.
        
        Side effects:
            Sets `self.done` to True when Return is pressed and modifies `self.name` and `self.current_pos`.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.done = True
                    return "".join(self.name)

                if event.key == pygame.K_BACKSPACE:
                    self.current_pos = max(0, self.current_pos - 1)

                if event.key == pygame.K_RIGHT:
                    self.current_pos = min(C.HIGHSCORE_NAME_LENGTH - 1, self.current_pos + 1)

                if event.key == pygame.K_LEFT:
                    self.current_pos = max(0, self.current_pos - 1)

                if event.key == pygame.K_UP:
                    current_char = self.name[self.current_pos]
                    idx = C.HIGHSCORE_ALLOWED_CHARS.find(current_char)
                    idx = (idx + 1) % len(C.HIGHSCORE_ALLOWED_CHARS)
                    self.name[self.current_pos] = C.HIGHSCORE_ALLOWED_CHARS[idx]

                if event.key == pygame.K_DOWN:
                    current_char = self.name[self.current_pos]
                    idx = C.HIGHSCORE_ALLOWED_CHARS.find(current_char)
                    idx = (idx - 1) % len(C.HIGHSCORE_ALLOWED_CHARS)
                    self.name[self.current_pos] = C.HIGHSCORE_ALLOWED_CHARS[idx]

        return None

    def draw(self, screen):
        """
        Render the highscore name-entry UI onto the given surface.
        
        Draws a translucent background overlay, a centered title and formatted score, the editable name characters with the currently selected position highlighted, and two hint lines near the bottom.
        
        Parameters:
            screen (pygame.Surface): Target surface to render the highscore input UI onto.
        """
        overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title_text = self.font.render(gettext("new_highscore"), True, pygame.Color("white"))
        screen.blit(
            title_text,
            (
                C.SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                C.SCREEN_HEIGHT // 3 - title_text.get_height(),
            ),
        )

        score_text = self.font.render(gettext("score_format").format(score=self.score), True, pygame.Color("white"))
        screen.blit(
            score_text,
            (C.SCREEN_WIDTH // 2 - score_text.get_width() // 2, C.SCREEN_HEIGHT // 3),
        )

        for i in range(C.HIGHSCORE_NAME_LENGTH):
            color = pygame.Color("yellow") if i == self.current_pos else pygame.Color("white")
            char_text = self.font.render(self.name[i], True, color)

            x = C.SCREEN_WIDTH // 2 - (C.HIGHSCORE_NAME_LENGTH * 40) // 2 + i * 40
            y = C.SCREEN_HEIGHT // 2

            if i == self.current_pos:
                pygame.draw.rect(
                    screen,
                    pygame.Color("yellow"),
                    (
                        x - 5,
                        y - 5,
                        char_text.get_width() + 10,
                        char_text.get_height() + 10,
                    ),
                    2,
                )

            screen.blit(char_text, (x, y))

        hint_font = pygame.font.Font(None, 30)
        hint1 = hint_font.render(gettext("highscore_hint_updown"), True, pygame.Color("white"))
        hint2 = hint_font.render(gettext("highscore_hint_enter"), True, pygame.Color("white"))

        screen.blit(hint1, (C.SCREEN_WIDTH // 2 - hint1.get_width() // 2, C.SCREEN_HEIGHT * 2 // 3))
        screen.blit(
            hint2,
            (C.SCREEN_WIDTH // 2 - hint2.get_width() // 2, C.SCREEN_HEIGHT * 2 // 3 + 30),
        )


class HighscoreDisplay:
    """Displays the highscore list."""
    def __init__(self, highscore_manager):
        """
        Create a highscore display and initialize its UI state.
        
        Parameters:
            highscore_manager: HighscoreManager providing access to saved highscores and related operations.
        
        Description:
            Stores the provided highscore manager, creates fonts used for title/entries/buttons, and initializes
            visual state for the background fade, back button (text, selection state, hover animation, vertical position),
            and an input cooldown timer.
        """
        self.highscore_manager = highscore_manager
        self.font_title = pygame.font.Font(None, 64)
        self.font_entry = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, C.MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True

        self.back_button = {
            "text": "back",
            "selected": True,
            "hover_animation": 0,
            "y": C.SCREEN_HEIGHT - 60,
        }
        self.input_cooldown = 0

    def update(self, dt, events):
        """
        Update UI animations and handle input that navigates back to the main menu.
        
        Parameters:
            dt (float): Time elapsed since last frame, in seconds.
            events (iterable): Iterable of pygame events to process.
        
        Returns:
            str or None: `"main_menu"` when space, return, or escape is pressed and input cooldown allows it; `None` otherwise.
        """
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / 0.5)
            if self.background_alpha >= 200:
                self.fade_in = False
                self.background_alpha = 200

        target = 1.0 if self.back_button["selected"] else 0.0
        animation_speed = 12.0
        self.back_button["hover_animation"] = (
            self.back_button["hover_animation"] + (target - self.back_button["hover_animation"]) * dt * animation_speed
        )

        if self.input_cooldown > 0:
            self.input_cooldown -= dt

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.input_cooldown <= 0:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                        self.input_cooldown = 0.15
                        return "main_menu"

        return None

    def draw(self, screen):
        """Draw the highscore display screen."""
        overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.background_alpha))
        screen.blit(overlay, (0, 0))

        title_text = self.font_title.render(gettext("highscores"), True, pygame.Color("white"))
        screen.blit(title_text, (C.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, entry in enumerate(self.highscore_manager.highscores):
            if i == 0:
                color = pygame.Color("gold")
            elif i == 1:
                color = pygame.Color(192, 192, 192)
            elif i == 2:
                color = pygame.Color(205, 127, 50)
            else:
                color = pygame.Color("white")
            rank_text = self.font_entry.render(f"{i+1}.", True, color)
            name_text = self.font_entry.render(f"{entry['name']}", True, color)
            score_text = self.font_entry.render(f"{entry['score']}", True, color)

            x_rank = C.SCREEN_WIDTH // 4
            x_name = C.SCREEN_WIDTH // 2 - 50
            x_score = C.SCREEN_WIDTH * 3 // 4
            y = 150 + i * 40

            screen.blit(rank_text, (x_rank, y))
            screen.blit(name_text, (x_name, y))
            screen.blit(score_text, (x_score, y))

        button = self.back_button
        color = pygame.Color(C.MENU_UNSELECTED_COLOR)
        selected_color = pygame.Color(C.MENU_SELECTED_COLOR)
        r = max(
            0,
            min(
                255,
                int(color.r + (selected_color.r - color.r) * button["hover_animation"]),
            ),
        )
        g = max(
            0,
            min(
                255,
                int(color.g + (selected_color.g - color.g) * button["hover_animation"]),
            ),
        )
        b = max(
            0,
            min(
                255,
                int(color.b + (selected_color.b - color.b) * button["hover_animation"]),
            ),
        )
        size_multiplier = 1.0 + 0.2 * button["hover_animation"]
        scaled_font = pygame.font.Font(None, int(C.MENU_ITEM_FONT_SIZE * size_multiplier))

        button_text = scaled_font.render(gettext(button["text"]), True, (r, g, b))
        button_rect = button_text.get_rect(center=(C.SCREEN_WIDTH // 2, button["y"]))
        screen.blit(button_text, button_rect)