import pygame
from constants import *
import math

# Globale Variable für Sounds
sounds = None

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
        self.add_item("Achievements", "achievements")  # Neue Option
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
        super().__init__("OPTIONS")
        self.settings = settings
        self.add_item("Music: ON" if settings.music_on else "Music: OFF", "toggle_music")
        self.add_item("Sound: ON" if settings.sound_on else "Sound: OFF", "toggle_sound") 
        self.add_item("Fullscreen: ON" if settings.fullscreen else "Fullscreen: OFF", "toggle_fullscreen")
        self.add_item("Sound Test", "sound_test")  # NEU: Sound Test hinzufügen
        self.add_item("Back", "back")
        
    def handle_action(self, action, sounds):
        if action == "toggle_music":
            self.settings.music_on = not self.settings.music_on
            self.settings.save()
            sounds.toggle_music(self.settings.music_on)
            # Menütext korrekt aktualisieren (MenuItem-Objekt, nicht Tuple!)
            self.items[0].text = "Music: ON" if self.settings.music_on else "Music: OFF"
            return None
            
        elif action == "toggle_sound":
            self.settings.sound_on = not self.settings.sound_on
            self.settings.save()
            sounds.toggle_sound(self.settings.sound_on)
            # Menütext korrekt aktualisieren (MenuItem-Objekt, nicht Tuple!)
            self.items[1].text = "Sound: ON" if self.settings.sound_on else "Sound: OFF"
            return None
            
        elif action == "toggle_fullscreen":
            self.settings.fullscreen = not self.settings.fullscreen
            self.settings.save()
            
            # WICHTIG: Fullscreen sofort anwenden!
            try:
                if self.settings.fullscreen:
                    # Zu Fullscreen wechseln
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    print("Fullscreen aktiviert")
                else:
                    # Zu Fenstermodus wechseln
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    print("Fenstermodus aktiviert")
            except Exception as e:
                print(f"Fehler beim Umschalten des Bildschirmmodus: {e}")
                # Einstellung rückgängig machen bei Fehler
                self.settings.fullscreen = not self.settings.fullscreen
                self.settings.save()
            
            # Menütext korrekt aktualisieren (MenuItem-Objekt, nicht Tuple!)
            self.items[2].text = "Fullscreen: ON" if self.settings.fullscreen else "Fullscreen: OFF"
            return None
            
        elif action == "sound_test":
            return "sound_test"
            
        elif action == "back":
            return "main_menu"
            
        return None


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


# Neue Klasse am Ende der Datei ergännen
class DifficultyMenu(Menu):
    def __init__(self):
        super().__init__("SCHWIERIGKEIT")
        self.add_item("Leicht", "difficulty_easy", "L")
        self.add_item("Normal", "difficulty_normal", "N")
        self.add_item("Schwer", "difficulty_hard", "S")
        self.add_item("Zurück", "main_menu", "Z")

# Neue Klasse am Ende der Datei hinzufügen:

class SoundTestMenu(Menu):
    def __init__(self):
        super().__init__("SOUND TEST")
        self.sounds = None  # Wird später gesetzt
        self.last_played = ""
        self.last_played_timer = 0
        
        # Scroll-Variablen
        self.scroll_offset = 0
        self.max_visible_items = 12  # Anzahl der sichtbaren Items
        self.current_selection = 0   # WICHTIG: Hier initialisieren!
        
        # Sound-Test-Items (vollständige Liste)
        self.sound_items = [
            ("Standard Shoot", "test_shoot"),
            ("Laser Shoot", "test_laser_shoot"),
            ("Rocket Shoot", "test_rocket_shoot"),
            ("Shotgun Shoot", "test_shotgun_shoot"),
            ("Triple Shoot", "test_triple_shoot"),
            ("", ""),  # Leerzeile
            ("Explosion", "test_explosion"),
            ("Player Hit", "test_player_hit"),
            ("PowerUp", "test_powerup"),
            ("Shield Activate", "test_shield_activate"),
            ("Weapon Pickup", "test_weapon_pickup"),
            ("", ""),  # Leerzeile
            ("Boss Spawn", "test_boss_spawn"),
            ("Boss Death", "test_boss_death"),
            ("Boss Attack", "test_boss_attack"),
            ("", ""),  # Leerzeile
            ("Level Up", "test_level_up"),
            ("Game Over", "test_game_over"),
            ("Menu Select", "test_menu_select"),
            ("Menu Confirm", "test_menu_confirm"),
            ("", ""),  # Leerzeile
            ("Test All Sounds", "test_all"),
            ("", ""),  # Leerzeile
            ("Back", "back")
        ]
        
        # Basis-Menu mit den sichtbaren Items initialisieren
        self.update_visible_items()
        
        # Fade-in Animation (wie andere Menüs)
        self.background_alpha = 0
        self.fade_in = False
    
    def activate(self):
        """Aktiviert das Sound Test Menü (überschreibt Menu.activate())"""
        self.fade_in = True
        self.background_alpha = 0
        # Keine Item-Animation da wir Tuples statt MenuItem-Objekte verwenden
        # Scroll-Position zurücksetzen
        self.scroll_offset = 0
        self.current_selection = 0
        self.update_visible_items()
    
    def set_sounds(self, sounds):
        """Sounds-Objekt setzen"""
        self.sounds = sounds
    
    def update_visible_items(self):
        """Aktualisiert die sichtbaren Menu-Items basierend auf scroll_offset"""
        self.items = []
        start_index = self.scroll_offset
        end_index = min(start_index + self.max_visible_items, len(self.sound_items))
        
        for i in range(start_index, end_index):
            self.items.append(self.sound_items[i])
        
        # Current selection innerhalb der sichtbaren Items halten
        if self.current_selection >= len(self.items):
            self.current_selection = max(0, len(self.items) - 1)
        if self.current_selection < 0:
            self.current_selection = 0
    
    def update(self, dt, events):
        """Update-Methode mit Scroll-Funktionalität"""
        # Fade-in Animation (wie Menu-Klasse)
        if self.fade_in:
            self.background_alpha = min(255, self.background_alpha + 255 * dt / MENU_TRANSITION_SPEED)
            if self.background_alpha >= MENU_BACKGROUND_ALPHA:
                self.fade_in = False
                self.background_alpha = MENU_BACKGROUND_ALPHA
        
        # Timer für "zuletzt gespielt" reduzieren
        if self.last_played_timer > 0:
            self.last_played_timer -= dt
            if self.last_played_timer <= 0:
                self.last_played = ""
        
        # Scroll-Eingaben verarbeiten
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.current_selection -= 1
                    
                    # Scrollen nach oben wenn am oberen Rand
                    if self.current_selection < 0:
                        if self.scroll_offset > 0:
                            self.scroll_offset -= 1
                            self.current_selection = 0
                            self.update_visible_items()
                        else:
                            # Am Anfang der Liste - wrap to bottom
                            self.scroll_offset = max(0, len(self.sound_items) - self.max_visible_items)
                            self.current_selection = min(self.max_visible_items - 1, len(self.sound_items) - 1 - self.scroll_offset)
                            self.update_visible_items()
                
                elif event.key == pygame.K_DOWN:
                    self.current_selection += 1
                    
                    # Scrollen nach unten wenn am unteren Rand
                    if self.current_selection >= len(self.items):
                        if self.scroll_offset + self.max_visible_items < len(self.sound_items):
                            self.scroll_offset += 1
                            self.current_selection = len(self.items) - 1
                            self.update_visible_items()
                        else:
                            # Am Ende der Liste - wrap to top
                            self.scroll_offset = 0
                            self.current_selection = 0
                            self.update_visible_items()
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if 0 <= self.current_selection < len(self.items):
                        return self.items[self.current_selection][1]  # Return action
                
                elif event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    return "back"
        
        return None
    
    def handle_action(self, action):
        """Sound-Test-Aktionen verarbeiten"""
        if not self.sounds:
            return None
            
        # Sound-Tests
        if action == "test_shoot":
            self.sounds.play_shoot()
            self.last_played = "Standard Shoot played"
            self.last_played_timer = 2.0
            
        elif action == "test_laser_shoot":
            if hasattr(self.sounds, 'play_laser_shoot'):
                self.sounds.play_laser_shoot()
            else:
                self.sounds.play_shoot()  # Fallback
            self.last_played = "Laser Shoot played"
            self.last_played_timer = 2.0
            
        elif action == "test_rocket_shoot":
            if hasattr(self.sounds, 'play_rocket_shoot'):
                self.sounds.play_rocket_shoot()
            else:
                self.sounds.play_shoot()  # Fallback
            self.last_played = "Rocket Shoot played"
            self.last_played_timer = 2.0
            
        elif action == "test_shotgun_shoot":
            if hasattr(self.sounds, 'play_shotgun_shoot'):
                self.sounds.play_shotgun_shoot()
            else:
                self.sounds.play_shoot()  # Fallback
            self.last_played = "Shotgun Shoot played"
            self.last_played_timer = 2.0
            
        elif action == "test_triple_shoot":
            if hasattr(self.sounds, 'play_triple_shoot'):
                self.sounds.play_triple_shoot()
            else:
                self.sounds.play_shoot()  # Fallback
            self.last_played = "Triple Shoot played"
            self.last_played_timer = 2.0
            
        elif action == "test_explosion":
            self.sounds.play_explosion()
            self.last_played = "Explosion played"
            self.last_played_timer = 2.0
            
        elif action == "test_player_hit":
            self.sounds.play_player_hit()
            self.last_played = "Player Hit played"
            self.last_played_timer = 2.0
            
        elif action == "test_powerup":
            self.sounds.play_powerup()
            self.last_played = "PowerUp played"
            self.last_played_timer = 2.0
            
        elif action == "test_shield_activate":
            self.sounds.play_shield_activate()
            self.last_played = "Shield Activate played"
            self.last_played_timer = 2.0
            
        elif action == "test_weapon_pickup":
            if hasattr(self.sounds, 'play_weapon_pickup'):
                self.sounds.play_weapon_pickup()
            else:
                self.sounds.play_powerup()  # Fallback
            self.last_played = "Weapon Pickup played"
            self.last_played_timer = 2.0
            
        elif action == "test_boss_spawn":
            self.sounds.play_boss_spawn()
            self.last_played = "Boss Spawn played"
            self.last_played_timer = 2.0
            
        elif action == "test_boss_death":
            self.sounds.play_boss_death()
            self.last_played = "Boss Death played"
            self.last_played_timer = 2.0
            
        elif action == "test_boss_attack":
            if hasattr(self.sounds, 'play_boss_attack'):
                self.sounds.play_boss_attack()
            else:
                self.sounds.play_explosion()  # Fallback
            self.last_played = "Boss Attack played"
            self.last_played_timer = 2.0
            
        elif action == "test_level_up":
            self.sounds.play_level_up()
            self.last_played = "Level Up played"
            self.last_played_timer = 2.0
            
        elif action == "test_game_over":
            self.sounds.play_game_over()
            self.last_played = "Game Over played"
            self.last_played_timer = 2.0
            
        elif action == "test_menu_select":
            self.sounds.play_menu_move()
            self.last_played = "Menu Select played"
            self.last_played_timer = 2.0
            
        elif action == "test_menu_confirm":
            self.sounds.play_menu_select()
            self.last_played = "Menu Confirm played"
            self.last_played_timer = 2.0
            
        elif action == "test_all":
            # Alle Sounds nacheinander abspielen
            import threading
            import time
            
            def play_all_sounds():
                sound_list = [
                    ("Standard Shoot", self.sounds.play_shoot),
                    ("Explosion", self.sounds.play_explosion),
                    ("Player Hit", self.sounds.play_player_hit),
                    ("PowerUp", self.sounds.play_powerup),
                    ("Level Up", self.sounds.play_level_up),
                    ("Game Over", self.sounds.play_game_over),
                ]
                
                for name, sound_func in sound_list:
                    try:
                        sound_func()
                        time.sleep(0.8)  # Pause zwischen Sounds
                    except:
                        pass  # Fehler ignorieren
            
            threading.Thread(target=play_all_sounds, daemon=True).start()
            self.last_played = "Playing all sounds..."
            self.last_played_timer = 8.0
            
        elif action == "back":
            return "options"
            
        return None

    def draw(self, screen):
        """Sound-Test-Menü mit verbessertem Layout zeichnen"""
        # Halbtransparenten Hintergrund zeichnen (wie Menu-Klasse)
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))
        
        # Titel zeichnen
        title_font = pygame.font.Font(None, MENU_TITLE_FONT_SIZE)
        title_surface = title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH/2, 60))
        screen.blit(title_surface, title_rect)
        
        # Scroll-Indikatoren
        indicator_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.7))
        
        # Nach oben scrollen möglich?
        if self.scroll_offset > 0:
            up_text = indicator_font.render("▲ Scroll UP", True, pygame.Color("yellow"))
            up_rect = up_text.get_rect(center=(SCREEN_WIDTH/2, 100))
            screen.blit(up_text, up_rect)
    
        # Nach unten scrollen möglich?
        if self.scroll_offset + self.max_visible_items < len(self.sound_items):
            down_text = indicator_font.render("▼ Scroll DOWN", True, pygame.Color("yellow"))
            down_rect = down_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 180))
            screen.blit(down_text, down_rect)
    
        # Menu-Items zeichnen mit verbessertem Layout
        font = pygame.font.Font(None, MENU_ITEM_FONT_SIZE)
        small_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.9))
        start_y = 130
    
        visible_item_count = 0  # Zähler für sichtbare Items (ohne Leerzeilen)
    
        for i, (text, action) in enumerate(self.items):
            current_y = start_y + visible_item_count * 35  # Kleinerer Abstand
    
            if text == "":  # Leerzeile - nur Platz hinzufügen
                visible_item_count += 0.3  # Kleine Lücke für Leerzeilen
                continue
    
            # Farbe und Stil basierend auf Auswahl
            is_selected = (i == self.current_selection)
    
            if is_selected:
                # Ausgewähltes Item - größer und heller
                color = MENU_SELECTED_COLOR
                scaled_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 1.1))
                surface = scaled_font.render(f"► {text}", True, pygame.Color(color))
    
                # Hintergrund für ausgewähltes Item
                bg_rect = pygame.Rect(SCREEN_WIDTH/2 - 200, current_y - 15, 400, 30)
                pygame.draw.rect(screen, (30, 30, 50, 100), bg_rect, border_radius=5)
            else:
                # Normales Item
                color = MENU_UNSELECTED_COLOR
                surface = small_font.render(f"  {text}", True, pygame.Color(color))
    
            # Spezielle Farben für verschiedene Sound-Kategorien
            if "Shoot" in text:
                category_color = (150, 255, 150)  # Grün für Waffen
            elif text in ["Explosion", "Player Hit"]:
                category_color = (255, 150, 150)  # Rot für Kampf
            elif text in ["PowerUp", "Shield Activate", "Weapon Pickup"]:
                category_color = (150, 150, 255)  # Blau für PowerUps
            elif "Boss" in text:
                category_color = (255, 200, 100)  # Orange für Boss
            elif text in ["Level Up", "Game Over"]:
                category_color = (255, 255, 150)  # Gelb für Spiel-Events
            elif "Menu" in text:
                category_color = (200, 200, 200)  # Grau für UI
            elif text in ["Test All Sounds", "Back"]:
                category_color = (255, 150, 255)  # Magenta für Aktionen
            else:
                category_color = (255, 255, 255)  # Weiß als Standard
    
            # Farbe anwenden wenn nicht ausgewählt
            if not is_selected:
                surface = small_font.render(f"  {text}", True, category_color)
    
            rect = surface.get_rect(center=(SCREEN_WIDTH/2, current_y))
            screen.blit(surface, rect)
    
            visible_item_count += 1
    
        # "Zuletzt gespielt" Anzeige mit besserem Styling
        if self.last_played:
            played_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.8))
    
            # Hintergrund für Feedback
            feedback_bg = pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT - 140, 300, 25)
            pygame.draw.rect(screen, (0, 100, 0, 150), feedback_bg, border_radius=10)
    
            played_text = played_font.render(self.last_played, True, pygame.Color("lightgreen"))
            played_rect = played_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 128))
            screen.blit(played_text, played_rect)
    
        # Anweisungen mit besserer Formatierung
        instructions = [
            "Navigation: ↑/↓ | Test: ENTER | Zurück: SPACE"
        ]
    
        instruction_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.65))
        for i, instruction in enumerate(instructions):
            # Hintergrund für Anweisungen
            instr_bg = pygame.Rect(20, SCREEN_HEIGHT - 80 + i * 25, SCREEN_WIDTH - 40, 20)
            pygame.draw.rect(screen, (20, 20, 20, 180), instr_bg, border_radius=5)
    
            text = instruction_font.render(instruction, True, pygame.Color("lightgray"))
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 70 + i * 25))
            screen.blit(text, text_rect)
    
        # Scroll-Info mit verbessertem Design
        scroll_info = f"Seite {(self.scroll_offset // self.max_visible_items) + 1} | Items {self.scroll_offset + 1}-{min(self.scroll_offset + self.max_visible_items, len(self.sound_items))} von {len(self.sound_items)}"
        info_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.6))
        info_text = info_font.render(scroll_info, True, pygame.Color("gray"))
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 25))
        screen.blit(info_text, info_rect)
    
        # Legende für Farbkodierung (optional)
        if self.scroll_offset == 0:  # Nur auf der ersten Seite anzeigen
            legend_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE * 0.5))
            legend_y = SCREEN_HEIGHT - 50
    
            legend_items = [
                ("Waffen", (150, 255, 150)),
                ("Kampf", (255, 150, 150)),
                ("PowerUps", (150, 150, 255)),
                ("Boss", (255, 200, 100))
            ]
    
            legend_x = 50
            for legend_text, legend_color in legend_items:
                legend_surface = legend_font.render(legend_text, True, legend_color)
                screen.blit(legend_surface, (legend_x, legend_y))
                legend_x += 120


class AchievementsMenu(Menu):
    def __init__(self, achievement_system):
        super().__init__("ACHIEVEMENTS")
        self.achievement_system = achievement_system
        self.add_item("Zurück", "back")
        
        # 8-bit ASCII Grafiken für jedes Achievement (kompakter)
        self.achievement_graphics = {
            "First Blood": [
                " ▄▄▄ ",
                "█░█░█",
                "░█▄█░",
                "█░█░█",
                " ▀▀▀ "
            ],
            "Survivor": [
                " ▄▄▄ ",
                "█░░░█",
                "█░█░█",
                "█░░░█",
                " ▀▀▀ "
            ],
            "Asteroid Hunter": [
                " ▄███▄ ",
                "█░▄▄▄░█",
                "█▄█▀█▄█",
                "█░▀▀▀░█",
                " ▀███▀ "
            ],
            "Power User": [
                " ▄█▄ ",
                "█░█░█",
                "█▄█▄█",
                "█░█░█",
                " ▀█▀ "
            ],
            "Boss Slayer": [
                " ▄▄▄▄▄ ",
                "█░███░█",
                "█░▀█▀░█",
                "█░▄█▄░█",
                " ▀▀▀▀▀ "
            ],
            "Level Master": [
                " ▄▄▄ ",
                "█▀▀▀█",
                "█░█░█",
                "█▄▄▄█",
                " ▀▀▀ "
            ],
            "High Scorer": [
                " ▄▄▄ ",
                "█░█░█",
                "█▄█▄█",
                "█░█░█",
                " ▀▀▀ "
            ],
            "Shield Expert": [
                " ▄▄▄ ",
                "█░░░█",
                "█░▄░█",
                "█░▀░█",
                " ▀▀▀ "
            ],
            "Speed Demon": [
                " ▄▄▄ ",
                "█▄▄▄█",
                "█▀▀▀█",
                "█▄▄▄█",
                " ▀▀▀ "
            ],
            "Triple Threat": [
                " ▄ ▄ ▄ ",
                "█ █ █ █",
                "█ █ █ █",
                "█ █ █ █",
                " ▀ ▀ ▀ "
            ]
        }

    def draw(self, screen):
        # Halbtransparenten Hintergrund zeichnen
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.background_alpha))
        screen.blit(background, (0, 0))

        # Titel zeichnen
        title_surf = self.title_font.render(self.title, True, pygame.Color(MENU_TITLE_COLOR))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 12))
        screen.blit(title_surf, title_rect)

        # Achievements mit kompaktem Layout zeichnen
        start_y = SCREEN_HEIGHT / 5
        achievement_spacing = 45  # Kompakter Abstand
        graphics_font = pygame.font.Font(None, 20)  # Schrift für ASCII-Grafiken
        name_font = pygame.font.Font(None, 28)      # Schrift für Achievement-Namen
        
        for i, achievement in enumerate(self.achievement_system.achievements):
            current_y = start_y + i * achievement_spacing
            
            # Prüfen ob Achievement freigeschaltet ist
            is_unlocked = achievement.unlocked
            
            # Farben basierend auf Status
            if is_unlocked:
                name_color = pygame.Color("gold")
                graphic_color = pygame.Color("yellow")
                status_color = pygame.Color("lightgreen")
            else:
                name_color = pygame.Color("darkgray")
                graphic_color = pygame.Color("darkred")
                status_color = pygame.Color("gray")
            
            # 8-bit Grafik zeichnen (nur wenn freigeschaltet)
            if is_unlocked and achievement.name in self.achievement_graphics:
                graphics = self.achievement_graphics[achievement.name]
                graphic_x = 80  # Links positioniert
                
                for line_idx, line in enumerate(graphics):
                    graphic_surf = graphics_font.render(line, True, graphic_color)
                    graphic_rect = graphic_surf.get_rect(topleft=(graphic_x, current_y - 8 + line_idx * 8))
                    screen.blit(graphic_surf, graphic_rect)
            
            # Achievement-Name zeichnen
            name_surf = name_font.render(achievement.name, True, name_color)
            name_rect = name_surf.get_rect(topleft=(200, current_y + 5))
            screen.blit(name_surf, name_rect)
            
            # Status-Indikator (kompakt)
            if is_unlocked:
                status_surf = name_font.render("✓", True, status_color)
            else:
                status_surf = name_font.render("🔒", True, status_color)
            status_rect = status_surf.get_rect(topleft=(520, current_y + 5))
            screen.blit(status_surf, status_rect)

        # Normale Menü-Items zeichnen (für "Zurück"-Button)
        back_button_y = SCREEN_HEIGHT - 100
        for i, item in enumerate(self.items):
            item_rect = item.draw(screen, (SCREEN_WIDTH / 2, back_button_y + i * MENU_ITEM_SPACING), self.item_font)

        # Zusätzliche Anweisung
        instruction_font = pygame.font.Font(None, 24)
        instruction_surf = instruction_font.render("Drücke ESC oder SPACE, um zurückzukehren", True, pygame.Color(MENU_UNSELECTED_COLOR))
        instruction_rect = instruction_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40))
        screen.blit(instruction_surf, instruction_rect)
        
        # Fortschrittsanzeige
        unlocked_count = sum(1 for achievement in self.achievement_system.achievements if achievement.unlocked)
        total_count = len(self.achievement_system.achievements)
        progress_text = f"Fortschritt: {unlocked_count}/{total_count} Achievements freigeschaltet"
        progress_surf = instruction_font.render(progress_text, True, pygame.Color("lightblue"))
        progress_rect = progress_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 12 + 40))
        screen.blit(progress_surf, progress_rect)

    def update(self, dt, events):
        # Erst die normale Menu-Update-Logik aufrufen
        result = super().update(dt, events)
        if result:
            return result

        # Zusätzliche ESC/SPACE-Behandlung für direktes Zurückkehren
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    return "back"

        return None