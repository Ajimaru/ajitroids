import json
import os
import pygame
import random
from modul.constants import *


class HighscoreManager:
    def __init__(self):
        self.highscores = []
        self.load_highscores()

    def load_highscores(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, "r") as f:
                    self.highscores = json.load(f)
            else:
                self.highscores = [
                    {
                        "name": "".join(random.choice(HIGHSCORE_ALLOWED_CHARS) for _ in range(HIGHSCORE_NAME_LENGTH)),
                        "score": (HIGHSCORE_MAX_ENTRIES - i) * 1000,
                    }
                    for i in range(HIGHSCORE_MAX_ENTRIES)
                ]
                self.save_highscores()
        except Exception as e:
            print(f"Error loading highscores: {e}")
            self.highscores = [{"name": "AAA", "score": 1000 - i * 100} for i in range(HIGHSCORE_MAX_ENTRIES)]

    def save_highscores(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                json.dump(self.highscores, f)
        except Exception as e:
            print(f"Error saving highscores: {e}")

    def is_highscore(self, score):
        if len(self.highscores) < HIGHSCORE_MAX_ENTRIES:
            return True
        return score > self.highscores[-1]["score"]

    def add_highscore(self, name, score):
        name = name.upper()[:HIGHSCORE_NAME_LENGTH]
        name = "".join(c for c in name if c in HIGHSCORE_ALLOWED_CHARS)
        name = name.ljust(HIGHSCORE_NAME_LENGTH, "A")

        self.highscores.append({"name": name, "score": score})
        self.highscores.sort(key=lambda x: x["score"], reverse=True)
        self.highscores = self.highscores[:HIGHSCORE_MAX_ENTRIES]
        self.save_highscores()

        for i, entry in enumerate(self.highscores):
            if entry["name"] == name and entry["score"] == score:
                return i
        return -1


class HighscoreInput:
    def __init__(self, score):
        self.score = score
        self.name = ["A", "A", "A"]
        self.current_pos = 0
        self.done = False
        self.font = pygame.font.Font(None, 64)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.done = True
                    return "".join(self.name)

                elif event.key == pygame.K_BACKSPACE:
                    self.current_pos = max(0, self.current_pos - 1)

                elif event.key == pygame.K_RIGHT:
                    self.current_pos = min(HIGHSCORE_NAME_LENGTH - 1, self.current_pos + 1)

                elif event.key == pygame.K_LEFT:
                    self.current_pos = max(0, self.current_pos - 1)

                elif event.key == pygame.K_UP:
                    current_char = self.name[self.current_pos]
                    idx = HIGHSCORE_ALLOWED_CHARS.find(current_char)
                    idx = (idx + 1) % len(HIGHSCORE_ALLOWED_CHARS)
                    self.name[self.current_pos] = HIGHSCORE_ALLOWED_CHARS[idx]

                elif event.key == pygame.K_DOWN:
                    current_char = self.name[self.current_pos]
                    idx = HIGHSCORE_ALLOWED_CHARS.find(current_char)
                    idx = (idx - 1) % len(HIGHSCORE_ALLOWED_CHARS)
                    self.name[self.current_pos] = HIGHSCORE_ALLOWED_CHARS[idx]

        return None

    def draw(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title_text = self.font.render("NEW HIGHSCORE!", True, pygame.Color("white"))
        screen.blit(
            title_text,
            (
                SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                SCREEN_HEIGHT // 3 - title_text.get_height(),
            ),
        )

        score_text = self.font.render(f"Score: {self.score}", True, pygame.Color("white"))
        screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 3),
        )

        for i in range(HIGHSCORE_NAME_LENGTH):
            color = pygame.Color("yellow") if i == self.current_pos else pygame.Color("white")
            char_text = self.font.render(self.name[i], True, color)

            x = SCREEN_WIDTH // 2 - (HIGHSCORE_NAME_LENGTH * 40) // 2 + i * 40
            y = SCREEN_HEIGHT // 2

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
        hint1 = hint_font.render("UP / DOWN Change letters", True, pygame.Color("white"))
        hint2 = hint_font.render("ENTER Confirm", True, pygame.Color("white"))

        screen.blit(hint1, (SCREEN_WIDTH // 2 - hint1.get_width() // 2, SCREEN_HEIGHT * 2 // 3))
        screen.blit(
            hint2,
            (SCREEN_WIDTH // 2 - hint2.get_width() // 2, SCREEN_HEIGHT * 2 // 3 + 30),
        )


class HighscoreDisplay:
    def __init__(self, highscore_manager):
        self.highscore_manager = highscore_manager
        self.font_title = pygame.font.Font(None, 64)
        self.font_entry = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True

        self.back_button = {
            "text": "Back",
            "selected": True,
            "hover_animation": 0,
            "y": SCREEN_HEIGHT - 60,
        }
        self.input_cooldown = 0

    def update(self, dt, events):
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
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.input_cooldown = 0.15
                        return "main_menu"

        return None

    def draw(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.background_alpha))
        screen.blit(overlay, (0, 0))

        title_text = self.font_title.render("HIGHSCORES", True, pygame.Color("white"))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

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

            x_rank = SCREEN_WIDTH // 4
            x_name = SCREEN_WIDTH // 2 - 50
            x_score = SCREEN_WIDTH * 3 // 4
            y = 150 + i * 40

            screen.blit(rank_text, (x_rank, y))
            screen.blit(name_text, (x_name, y))
            screen.blit(score_text, (x_score, y))

        button = self.back_button
        color = pygame.Color(MENU_UNSELECTED_COLOR)
        selected_color = pygame.Color(MENU_SELECTED_COLOR)
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
        scaled_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * size_multiplier))

        button_text = scaled_font.render(button["text"], True, (r, g, b))
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, button["y"]))
        screen.blit(button_text, button_rect)
