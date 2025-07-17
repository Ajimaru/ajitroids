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
        
        # Menüsounds
        try:
            self.menu_move = pygame.mixer.Sound("assets/menu_move.wav")  # Menübewegungssound
            self.menu_select = pygame.mixer.Sound("assets/menu_select.wav")  # Menüauswahlsound
            self.menu_move.set_volume(0.3)
            self.menu_select.set_volume(0.4)
        except:
            print("Menüsounds konnten nicht geladen werden")
        
        # Musik laden, aber noch nicht abspielen
        try:
            pygame.mixer.music.load("assets/background.mp3")
            pygame.mixer.music.set_volume(0.2)  # Standardlautstärke setzen
            # Wichtig: Nicht hier pygame.mixer.music.play() aufrufen!
            print("Hintergrundmusik geladen (aber noch nicht gestartet)")
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

    def play_menu_move(self):
        try:
            self.menu_move.play()
        except:
            pass

    def play_menu_select(self):
        try:
            self.menu_select.play()
        except:
            pass

    def toggle_music(self, enabled):
        try:
            if enabled:
                pygame.mixer.music.set_volume(0.2)  # Musik mit ursprünglicher Lautstärke
                # Wenn die Musik nicht bereits läuft, laden und starten
                if not pygame.mixer.music.get_busy():
                    # Musik vollständig neu laden
                    pygame.mixer.music.load("assets/background.mp3")
                    pygame.mixer.music.play(-1)  # Musik starten (endlos)
                    print("toggle_music: Musik neu geladen und gestartet")
                else:
                    print("toggle_music: Musik läuft bereits")
            else:
                pygame.mixer.music.stop()
                pygame.mixer.music.set_volume(0.0)
                print("toggle_music: Musik gestoppt und Lautstärke auf 0")
        except Exception as e:
            print(f"Fehler beim Umschalten der Musik: {e}")

    def toggle_sound(self, enabled):
        volume = 0.5 if enabled else 0.0
        try:
            # Liste der Soundobjekte anpassen - 'powerup_pickup' in 'powerup' ändern
            sound_list = []
            
            # Jeden Sound einzeln prüfen und hinzufügen, falls er existiert
            if hasattr(self, 'shoot'):
                sound_list.append(self.shoot)
            if hasattr(self, 'explosion'):
                sound_list.append(self.explosion)
            if hasattr(self, 'player_death'):
                sound_list.append(self.player_death)
            if hasattr(self, 'powerup'): # Der korrekte Attributname ist wahrscheinlich 'powerup'
                sound_list.append(self.powerup)
            
            # Lautstärke für alle Sounds setzen
            for sound in sound_list:
                if sound is not None:
                    sound.set_volume(volume)
            
            # Menüsounds auch anpassen
            if hasattr(self, 'menu_move'):
                self.menu_move.set_volume(0.3 if enabled else 0.0)
            if hasattr(self, 'menu_select'):
                self.menu_select.set_volume(0.4 if enabled else 0.0)
        except Exception as e:
            print(f"Fehler beim Ändern der Sound-Lautstärke: {e}")

    # Neue Methode zur Sounds-Klasse hinzufügen
    def change_background_music(self, track_name):
        pygame.mixer.music.fadeout(1000)  # Fade-out über 1 Sekunde
        pygame.time.delay(1000)
        pygame.mixer.music.load(f"assets/{track_name}")
        pygame.mixer.music.play(-1)