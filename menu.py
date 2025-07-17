import pygame
from constants import *
import math

class MenuItem:
    def __init__(self, text, action):
        self.text = text
        self.action = action
        self.selected = False
        self.hover_animation = 0
        self.opacity = 255  # Vollständig sichtbar standardmäßig
        self.delay = 0  # Verzögerung für das Einblenden
    
    def update(self, dt):
        # Schnellere Animation für die Auswahl
        target = 1.0 if self.selected else 0.0
        animation_speed = 12.0  # Erhöht von 5 auf 12 für schnellere Reaktion
        self.hover_animation = self.hover_animation + (target - self.hover_animation) * dt * animation_speed
        
        # Verzögerung berücksichtigen
        if self.delay > 0:
            self.delay -= dt
            if self.delay <= 0:
                self.delay = 0
                self.opacity = 255  # Vollständig sichtbar, wenn die Verzögerung vorbei ist
        
    def draw(self, screen, position, font):
        # Farbe basierend auf Auswahl und Animation
        color = pygame.Color(MENU_UNSELECTED_COLOR)
        selected_color = pygame.Color(MENU_SELECTED_COLOR)
        
        # Sicherstellen, dass die RGB-Werte im gültigen Bereich (0-255) liegen
        r = max(0, min(255, int(color.r + (selected_color.r - color.r) * self.hover_animation)))
        g = max(0, min(255, int(color.g + (selected_color.g - color.g) * self.hover_animation)))
        b = max(0, min(255, int(color.b + (selected_color.b - color.b) * self.hover_animation)))
        
        # Größe basierend auf Auswahl
        size_multiplier = 1.0 + 0.2 * self.hover_animation
        scaled_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * size_multiplier))
        
        # Text rendern - auch unausgewählte Menüpunkte sind sichtbar
        text_surface = scaled_font.render(self.text, True, (r, g, b))
        text_rect = text_surface.get_rect(center=(position[0], position[1]))
        screen.blit(text_surface, text_rect)
        
        return text_rect


class Menu:
    def __init__(self, title):
        self.title = title
        self.items = []
        self.selected_index = 0
        self.background_alpha = 0
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.item_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.active = False
        self.fade_in = False
        self.input_cooldown = 0  # Cooldown für Tasteneingaben
        
    def add_item(self, text, action, shortcut=None):
        item = MenuItem(text, action)
        item.shortcut = shortcut  # z.B. "S" für Start
        self.items.append(item)
        if len(self.items) == 1:
            self.items[0].selected = True
            
    def activate(self):
        self.active = True
        self.fade_in = True
        self.background_alpha = 0
        # Items mit Verzögerung einblenden
        for i, item in enumerate(self.items):
            item.opacity = 0
            item.delay = i * 0.1  # Jedes Item erscheint 100ms nach dem vorherigen
            
    def update(self, dt, events):
        # Hintergrund-Fade-Animation
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA
        
        # Menüpunkt-Animation
        for item in self.items:
            item.update(dt)
        
        # Input-Cooldown reduzieren
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
        
        # Tastatureingaben verarbeiten
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Sofortige Eingabe bei Tastendruck
                if self.input_cooldown <= 0:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self._select_previous()
                        self.input_cooldown = 0.15  # Kurzer Cooldown (150 ms)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self._select_next()
                        self.input_cooldown = 0.15
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.items[self.selected_index].action
        
        # Tastenkürzel prüfen
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Vorhandener Code...
                
                # Tastenkürzel prüfen
                for i, item in enumerate(self.items):
                    if hasattr(item, 'shortcut') and item.shortcut and event.unicode.lower() == item.shortcut.lower():
                        self.selected_index = i
                        self.items[self.selected_index].selected = True
                        return item.action
        
        # Kontinuierliche Eingabe bei gehaltener Taste
        keys = pygame.key.get_pressed()
        if self.input_cooldown <= 0:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self._select_previous()
                self.input_cooldown = 0.15
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self._select_next()
                self.input_cooldown = 0.15
        
        # Controller-Eingabe prüfen
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            
            # D-Pad oder Analog-Stick für Navigation
            axis_y = joystick.get_axis(1)  # Vertikale Achse
            if axis_y < -0.5 and self.input_cooldown <= 0:  # Nach oben
                self._select_previous()
                self.input_cooldown = 0.15
            elif axis_y > 0.5 and self.input_cooldown <= 0:  # Nach unten
                self._select_next()
                self.input_cooldown = 0.15
                
            # A-Taste für Auswahl
            if joystick.get_button(0) and self.input_cooldown <= 0:
                self.input_cooldown = 0.15
                return self.items[self.selected_index].action
                
        return None
        
    def _select_next(self):
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self.items[self.selected_index].selected = True
        # Sound abspielen, wenn verfügbar
        if 'sounds' in globals() or hasattr(self, 'sounds'):
            try:
                sounds.play_menu_move()
            except:
                pass

    def _select_previous(self):
        self.items[self.selected_index].selected = False
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self.items[self.selected_index].selected = True
        # Sound abspielen, wenn verfügbar
        if 'sounds' in globals() or hasattr(self, 'sounds'):
            try:
                sounds.play_menu_move()
            except:
                pass

    def draw(self, screen):
        # Halbtransparenten Hintergrund zeichnen
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))
        
        # Titel zeichnen
        title_surf = self.title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        screen.blit(title_surf, title_rect)
        
        # Menüpunkte zeichnen
        start_y = SCREEN_HEIGHT / 2
        for i, item in enumerate(self.items):
            position = (SCREEN_WIDTH / 2, start_y + i * MENU_ITEM_SPACING)
            item.draw(screen, position, self.item_font)


class MainMenu(Menu):
    def __init__(self):
        super().__init__("AJITROIDS")
        self.add_item("Start Game", "start_game")
        self.add_item("Tutorial", "tutorial")
        self.add_item("Highscores", "highscores")
        self.add_item("Optionen", "options")  # Neue Option
        self.add_item("Credits", "credits")   # Neue Option
        self.add_item("Exit", "exit")
    
    # In der MainMenu.draw() Methode hinzufügen
    def draw(self, screen):
        # Vorhandener Code zum Zeichnen des Menüs
        super().draw(screen)
        
        # Version in der unteren rechten Ecke zeichnen
        version_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE / 1.5))
        version_text = version_font.render(GAME_VERSION, True, pygame.Color(MENU_UNSELECTED_COLOR))
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        screen.blit(version_text, version_rect)


class PauseMenu(Menu):
    def __init__(self):
        super().__init__("PAUSE")
        self.add_item("Continue", "continue")
        self.add_item("Restart", "restart")
        self.add_item("Main Menu", "main_menu")


class TutorialScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True
        
    def update(self, dt, events):
        # Hintergrund-Fade-Animation
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA
        
        # Tastatureingaben - jetzt nur ESC für zurück, damit Leertaste global ist
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main_menu"
        
        return None
    
    def draw(self, screen):
        # Halbtransparenten Hintergrund zeichnen
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))
        
        # Titel
        title_surf = self.title_font.render("How to Play", True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, 100))
        screen.blit(title_surf, title_rect)
        
        # Anleitung
        instructions = [
            "W / Pfeil hoch: Beschleunigen",
            "A / Pfeil links: Nach links drehen",
            "D / Pfeil rechts: Nach rechts drehen",
            "S / Pfeil runter: Rückwärts",
            "Leertaste: Schießen / Im Menü: Zurück zum Hauptmenü",
            "ESC: Pause",
            "",
            "Zerstöre alle Asteroiden und sammle Power-ups:",
            "Schild (Blau): Vorübergehende Unverwundbarkeit",
            "Dreifachschuss (Magenta): Drei Schüsse auf einmal",
            "Schnellfeuer (Gelb): Erhöhte Feuerrate",
            "",
            "Drücke LEERTASTE, um zum Hauptmenü zurückzukehren"
        ]
        
        y = 180
        for line in instructions:
            text_surf = self.text_font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH/2, y))
            screen.blit(text_surf, text_rect)
            y += 40


class OptionsMenu(Menu):
    def __init__(self, settings):
        super().__init__("OPTIONEN")
        self.settings = settings  # Einstellungen speichern
        
        # Menüpunkte basierend auf aktuellen Einstellungen
        self.add_item(f"Musik: {'An' if settings.music_on else 'Aus'}", "toggle_music")
        self.add_item(f"Soundeffekte: {'An' if settings.sound_on else 'Aus'}", "toggle_sound")
        self.add_item(f"Vollbild: {'An' if settings.fullscreen else 'Aus'}", "toggle_fullscreen")
        self.add_item("Zurück", "main_menu")
    
    def handle_action(self, action, sounds=None):
        if action == "toggle_music":
            self.settings.music_on = not self.settings.music_on
            self.items[0].text = f"Musik: {'An' if self.settings.music_on else 'Aus'}"
            
            # Musik ein-/ausschalten
            if sounds:
                sounds.toggle_music(self.settings.music_on)
                
            # Einstellungen sofort speichern
            self.settings.save()
            return None
            
        elif action == "toggle_sound":
            self.settings.sound_on = not self.settings.sound_on
            self.items[1].text = f"Soundeffekte: {'An' if self.settings.sound_on else 'Aus'}"
            # Soundeffekte ein-/ausschalten
            if sounds:
                sounds.toggle_sound(self.settings.sound_on)
            # Einstellungen speichern
            self.settings.save()
            return None
            
        elif action == "toggle_fullscreen":
            self.settings.fullscreen = not self.settings.fullscreen
            self.items[2].text = f"Vollbild: {'An' if self.settings.fullscreen else 'Aus'}"
            
            # Vollbildmodus umschalten
            try:
                if self.settings.fullscreen:
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                # Einstellungen speichern
                self.settings.save()
            except Exception as e:
                print(f"Fehler beim Umschalten des Vollbildmodus: {e}")
                # Zurücksetzen bei Fehler
                self.settings.fullscreen = not self.settings.fullscreen
                self.items[2].text = f"Vollbild: {'An' if self.settings.fullscreen else 'Aus'}"
                
            return None
        else:
            return action


class CreditsScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE - 8)  # Etwas kleinere Schrift
        self.background_alpha = 0
        self.fade_in = True
        self.scroll_position = SCREEN_HEIGHT  # Start unterhalb des Bildschirms
    
    def update(self, dt, events):
        # Hintergrund-Fade-Animation
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA
        
        # Scrolling-Animation mit Konstante
        self.scroll_position -= CREDITS_SCROLL_SPEED * dt
    
        # Tastatureingaben
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    return "main_menu"
        
        return None
    
    def draw(self, screen):
        # Halbtransparenten Hintergrund zeichnen
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))
        
        # Titel
        title_surf = self.title_font.render(CREDITS_TITLE, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, 100))
        screen.blit(title_surf, title_rect)
        
        # Credits-Text aus Konstanten zusammenbauen
        credits = [
            CREDITS_GAME_NAME,
            "",
            f"Ein Spiel von {CREDITS_DEVELOPER}",
            "",
            "Programmierung",
            CREDITS_DEVELOPER,
            "",
            "Grafik & Design",
            CREDITS_GRAPHICS,
            "",
            "Sound & Musik",
            CREDITS_SOUND,
            "",
            "Besonderer Dank an"
        ]
        
        # Special Thanks hinzufügen
        credits.extend(CREDITS_SPECIAL_THANKS)
        
        # Website und Abschlusstext hinzufügen
        credits.extend([
            "",
            f"Download & Updates: {CREDITS_WEBSITE}",
            "",
            "Vielen Dank fürs Spielen!",
            "",
            "Drücke LEERTASTE, um zurückzukehren"
        ])
        
        y = self.scroll_position
        for line in credits:
            text_surf = self.text_font.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH/2, y))
            screen.blit(text_surf, text_rect)
            y += CREDITS_LINE_SPACING
            
        # Wenn Credits komplett durchgescrollt sind, von vorne beginnen
        if y < 0:
            self.scroll_position = SCREEN_HEIGHT


class GameOverScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        self.text_font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        self.background_alpha = 0
        self.fade_in = True
        self.final_score = 0
        
    def set_score(self, score):
        self.final_score = score
        
    def update(self, dt, events):
        # Hintergrund-Fade-Animation
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA
        
        # Tastatureingaben
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return "highscore_display"
                elif event.key == pygame.K_ESCAPE:
                    return "main_menu"
        
        return None
    
    def draw(self, screen):
        # Halbtransparenten Hintergrund zeichnen
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))
        
        # Game Over Titel
        title_surf = self.title_font.render("GAME OVER", True, pygame.Color("red"))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
        screen.blit(title_surf, title_rect)
        
        # Score anzeigen
        score_surf = self.text_font.render(f"Dein Score: {self.final_score}", True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(score_surf, score_rect)
        
        # Anweisungen
        instruction1 = self.text_font.render("Drücke LEERTASTE um die Highscores zu sehen", True, (200, 200, 200))
        instruction1_rect = instruction1.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80))
        screen.blit(instruction1, instruction1_rect)
        
        instruction2 = self.text_font.render("Drücke ESC um zum Hauptmenü zurückzukehren", True, (200, 200, 200))
        instruction2_rect = instruction2.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 120))
        screen.blit(instruction2, instruction2_rect)


# Neue Klasse am Ende der Datei ergänzen
class DifficultyMenu(Menu):
    def __init__(self):
        super().__init__("SCHWIERIGKEIT")
        self.add_item("Leicht", "difficulty_easy", "L")
        self.add_item("Normal", "difficulty_normal", "N")
        self.add_item("Schwer", "difficulty_hard", "S")
        self.add_item("Zurück", "main_menu", "Z")