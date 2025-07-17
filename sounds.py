import pygame
import os

class Sounds:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 2048)
        
        self.shoot = pygame.mixer.Sound("assets/shoot.wav")
        self.shoot.set_volume(0.3)
        
        self.explosion = pygame.mixer.Sound("assets/explosion.wav")
        self.explosion.set_volume(0.4)  # Reduzierte Lautstärke
        
        self.player_death = pygame.mixer.Sound("assets/player_death.wav")
        self.player_death.set_volume(0.5)
        
        try:
            pygame.mixer.music.load("assets/background.mp3")
            pygame.mixer.music.set_volume(0.2)           # ...existing code...
            PLAYER_ACCELERATION = 300  # Beschleunigung pro Sekunde
            PLAYER_MAX_SPEED = 400    # Maximale Geschwindigkeit
            PLAYER_FRICTION = 0.02    # Reibung im Weltraum (sehr gering)
            PLAYER_ROTATION_SPEED = 180  # Grad pro Sekunde)  # Noch etwas leiser
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Fehler beim Laden der Hintergrundmusik: {e}")
            print(f"Aktuelles Verzeichnis: {os.getcwd()}")
            print(f"Datei existiert: {os.path.exists('assets/background.mp3')}")

    def play_shoot(self):
        self.shoot.play()

    def play_explosion(self):
        self.explosion.play()

    def play_player_death(self):
        self.player_death.play()