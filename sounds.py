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

        self.sound_on = True  # Standard-Einstellung

    def load_sounds(self):
        # Bestehende Sound-Lade-Logik...
        
        try:
            self.level_up = pygame.mixer.Sound("sassets/level_up.wav")
        except:
            self.level_up = None
            print("Level-Up-Sound konnte nicht geladen werden")

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

    def play_level_up(self):
        if hasattr(self, 'level_up') and self.level_up and self.sound_on:
            self.level_up.play()

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

    def play_boss_music(self):
        """Spielt die Boss-Kampf-Musik"""
        try:
            # Überprüfe, ob Sound aktiviert ist (ohne auf sound_on zuzugreifen)
            if pygame.mixer.get_init() is not None:
                # Normale Musik pausieren
                pygame.mixer.music.pause()
                
                try:
                    # Alternativ: Direkt zur Boss-Musik wechseln
                    pygame.mixer.music.load("assets/boss_music.mp3")
                    pygame.mixer.music.set_volume(0.3)  # Etwas lauter als normale Hintergrundmusik
                    pygame.mixer.music.play(-1)
                    print("Boss-Musik gestartet")
                except:
                    # Fallback: Nur ein Level-Up-Sound abspielen
                    print("Boss-Musik konnte nicht geladen werden, verwende normalen Sound")
                    self.play_explosion()  # Alternativ einen dramatischeren Sound verwenden
        except Exception as e:
            print(f"Fehler beim Starten der Boss-Musik: {e}")

    def play_hit(self):
        """Spielt den Sound ab, wenn der Boss getroffen wird"""
        try:
            if pygame.mixer.get_init() is not None:
                # Vorhandenen Sound verwenden, oder einen neuen laden
                self.play_explosion()  # Vorhandenen Sound wiederverwenden
        except Exception as e:
            print(f"Fehler beim Abspielen des Hit-Sounds: {e}")

    def play_extra_life(self):
        """Spielt einen Sound ab, wenn der Spieler ein extra Leben bekommt"""
        try:
            if pygame.mixer.get_init() is not None:
                # Da wir keinen eigenen Sound haben, verwenden wir einen vorhandenen Sound
                # Spielen wir den Level-Up-Sound etwas länger oder wiederhole ihn für Effekt
                self.play_player_death()  # Ironischerweise, aber ein markanter Sound
                
                # Optional: Mit kurzer Verzögerung einen weiteren Sound spielen
                # für einen spezielleren Effekt
                pygame.time.delay(200)  # 200ms warten
                self.play_explosion()
                
                print("Extra-Leben-Sound abgespielt")
        except Exception as e:
            print(f"Fehler beim Abspielen des Extra-Leben-Sounds: {e}")