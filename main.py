import sys
import pygame
import math
import random
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from particle import Particle
from sounds import Sounds
from starfield import Starfield, MenuStarfield  # MenuStarfield hinzufügen
from powerup import PowerUp  # PowerUp-Klasse importieren
from highscore import HighscoreManager, HighscoreInput, HighscoreDisplay  # Highscore-Klassen importieren
from menu import MainMenu, PauseMenu, TutorialScreen, OptionsMenu, CreditsScreen, GameOverScreen, DifficultyMenu  # Menü-Klassen importieren
from settings import Settings


def main():
    # Existierende Variablen
    pygame.init()
    
    # Mixer explizit initialisieren mit guten Parametern
    try:
        pygame.mixer.init(44100, -16, 2, 2048)
        print("Pygame Mixer erfolgreich initialisiert")
    except Exception as e:
        print(f"Fehler bei der Mixer-Initialisierung: {e}")
    
    pygame.display.set_caption("Ajitroids")
    
    # Clock definieren
    clock = pygame.time.Clock()
    
    # Settings-Objekt initialisieren
    game_settings = Settings()
    
    # Hier fehlt die Definition des Bildschirms (screen)
    # Vollbild-Modus entsprechend der Settings setzen
    if game_settings.fullscreen:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        print("Vollbildmodus aktiviert")
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print("Fenstermodus aktiviert")
    
    # Sound-System initialisieren
    sounds = Sounds()

    # Verzögerung hinzufügen, um sicherzustellen, dass pygame.mixer bereit ist
    pygame.time.delay(200)  # Längere Verzögerung

    # Sound-Einstellungen anwenden
    print(f"Wende Musik-Einstellung an: {game_settings.music_on}")

    # Musik vollständig neu laden und starten
    if game_settings.music_on:
        try:
            # Musik vollständig stoppen falls sie läuft
            pygame.mixer.music.stop()
            # Musik neu laden
            pygame.mixer.music.load("assets/background.mp3")
            pygame.mixer.music.set_volume(0.2)
            # Musik starten
            pygame.mixer.music.play(-1)
            print("Musik beim Start explizit neu geladen und gestartet")
        except Exception as e:
            print(f"Fehler beim Starten der Musik: {e}")
    else:
        pygame.mixer.music.set_volume(0.0)
        pygame.mixer.music.stop()
        print("Musik beim Start deaktiviert")

    # Sound-Effekte-Einstellungen anwenden
    sounds.toggle_sound(game_settings.sound_on)
    
    # Sprite-Gruppen initialisieren
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    # Container für alle Sprite-Typen setzen
    Shot.containers = (shots, updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Player.containers = (updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    Particle.containers = (particles, updatable, drawable)

    # Spielobjekte initialisieren
    asteroid_field = AsteroidField()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    
    # Standard-Starfield für das Spiel
    starfield = Starfield()
    
    # Spezielles Starfield für das Hauptmenü
    menu_starfield = MenuStarfield(200)
    
    font = pygame.font.Font(None, 36)

    # Spielvariablen
    dt = 0
    lives = PLAYER_LIVES
    score = 0
    
    # Level-System-Variablen
    level = 1
    level_up_timer = 0
    level_up_text = ""

    # Highscore-System
    highscore_manager = HighscoreManager()
    highscore_input = None
    highscore_display = HighscoreDisplay(highscore_manager)
    
    # Menüs
    main_menu = MainMenu()
    pause_menu = PauseMenu()
    tutorial_screen = TutorialScreen()
    options_menu = OptionsMenu(game_settings)  # Settings übergeben
    credits_screen = CreditsScreen()
    game_over_screen = GameOverScreen()
    difficulty_menu = DifficultyMenu()  # Neu hinzufügen
    
    # Schwierigkeitsgrad-Variable
    difficulty = "normal"  # Standardwert

    # Anfangszustand ist das Hauptmenü
    game_state = "main_menu"
    main_menu.activate()
    
    # Hauptspielschleife
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
            
            # Pausieren, wenn ESC gedrückt wird und wir im Spiel sind
            if game_state == "playing" and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "pause"
                pause_menu.activate()
        
        # Bildschirm löschen
        screen.fill("black")
        
        # ====== HAUPTMENÜ ======
        if game_state == "main_menu":
            # Animierter Windows 95-artiger Hintergrund
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
            
            action = main_menu.update(dt, events)
            main_menu.draw(screen)
            
            # Version in der unteren rechten Ecke zeichnen
            version_font = pygame.font.Font(None, int(MENU_ITEM_FONT_SIZE / 1.5))
            version_text = version_font.render(GAME_VERSION, True, pygame.Color(MENU_UNSELECTED_COLOR))
            version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            screen.blit(version_text, version_rect)
            
            # Überprüfe Musik-Status im Hauptmenü
            if game_settings.music_on and not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.play(-1)
                    print("Musik im Hauptmenü erneut gestartet")
                except Exception as e:
                    print(f"Fehler beim Starten der Musik im Hauptmenü: {e}")
            
            if action == "start_game":
                game_state = "difficulty_select"  # Statt direkt zum Spiel zur Schwierigkeitsauswahl
                difficulty_menu.activate()
            
            elif action == "tutorial":
                game_state = "tutorial"
                tutorial_screen.fade_in = True
                tutorial_screen.background_alpha = 0
            
            elif action == "highscores":
                game_state = "highscore_display"
            
            elif action == "options":
                game_state = "options"
                options_menu.activate()
                
            elif action == "credits":
                game_state = "credits"
                credits_screen.fade_in = True
                credits_screen.background_alpha = 0
                credits_screen.scroll_position = SCREEN_HEIGHT  # Reset scroll position
    
            elif action == "exit":
                return
            
        # ====== SCHWIERIGKEITSWAHL ======
        elif game_state == "difficulty_select":
            # Menü-Starfield auch hier anzeigen
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
    
            action = difficulty_menu.update(dt, events)
            difficulty_menu.draw(screen)
            
            if action == "difficulty_easy":
                difficulty = "easy"
                game_state = "playing"
                score = 0  # Score zurücksetzen
                lives = PLAYER_LIVES  # Konstante PLAYER_LIVES verwenden oder direkt z.B. 3
                level = 1  # Level zurücksetzen
                
                # Alle vorhandenen Objekte löschen
                for asteroid in list(asteroids):
                    asteroid.kill()
                for powerup in list(powerups):
                    powerup.kill()
                for shot in list(shots):
                    shot.kill()
                for particle in list(particles):
                    particle.kill()
                
                # Spieler neu erstellen und an Startposition setzen
                if player in updatable:
                    player.kill()
                player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.sounds = sounds  # Sounds wieder setzen

                # Spiel starten mit leichter Schwierigkeit
                asteroid_field.asteroid_count = 3  # Weniger Asteroiden
                asteroid_field.spawn_interval = 8.0  # Langsameres Spawnen

            elif action == "difficulty_normal":
                difficulty = "normal"
                game_state = "playing"
                score = 0  # Score zurücksetzen
                lives = PLAYER_LIVES  # Konstante verwenden
                level = 1  # Level zurücksetzen
                
                # Alle vorhandenen Objekte löschen
                for asteroid in list(asteroids):
                    asteroid.kill()
                for powerup in list(powerups):
                    powerup.kill()
                for shot in list(shots):
                    shot.kill()
                for particle in list(particles):
                    particle.kill()
                
                # Spieler neu erstellen
                if player in updatable:
                    player.kill()
                player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.sounds = sounds
                
                # Normaler Schwierigkeitsgrad
                asteroid_field.asteroid_count = 5
                asteroid_field.spawn_interval = 5.0
                
            elif action == "difficulty_hard":
                difficulty = "hard"
                game_state = "playing"
                score = 0
                lives = PLAYER_LIVES
                level = 1
                
                # Alle Objekte löschen
                for asteroid in list(asteroids):
                    asteroid.kill()
                for powerup in list(powerups):
                    powerup.kill()
                for shot in list(shots):
                    shot.kill()
                for particle in list(particles):
                    particle.kill()
                
                # Spieler neu erstellen
                if player in updatable:
                    player.kill()
                player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                player.sounds = sounds
                
                # Schwere Schwierigkeit
                asteroid_field.asteroid_count = 7
                asteroid_field.spawn_interval = 3.0
                
            elif action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()
                
            # Leertaste zum Hauptmenü
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "main_menu"
                    main_menu.activate()
    
        # ====== TUTORIAL ======
        elif game_state == "tutorial":
            # Menü-Starfield auch hier anzeigen
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
    
            action = tutorial_screen.update(dt, events)
            tutorial_screen.draw(screen)
            
            # Leertaste zum Hauptmenü
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "main_menu"
                    main_menu.activate()
    
            if action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()
        
        # ====== PAUSE ======
        elif game_state == "pause":
            # Spiel im Hintergrund anzeigen
            for obj in drawable:
                obj.draw(screen)
                
            # Pause-Menü anzeigen
            action = pause_menu.update(dt, events)
            pause_menu.draw(screen)
            
            # Zur Vereinheitlichung: Leertaste führt immer zum Hauptmenü zurück
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "main_menu"
                    main_menu.activate()
            
            if action == "continue":
                game_state = "playing"
            
            elif action == "restart":
                game_state = "playing"
                # Spiel zurücksetzen
                score = 0
                lives = PLAYER_LIVES
                # Spielobjekte zurücksetzen
                for asteroid in asteroids:
                    asteroid.kill()
                for powerup in powerups:
                    powerup.kill()
                for shot in shots:
                    shot.kill()
                for particle in particles:
                    particle.kill()
                # Spieler zurücksetzen
                player.position.x = RESPAWN_POSITION_X
                player.position.y = RESPAWN_POSITION_Y
                player.velocity = pygame.Vector2(0, 0)
                player.rotation = 0
                player.respawn()
            
            elif action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()
        
        # ====== OPTIONS ======
        elif game_state == "options":
            # Menü-Starfield auch hier anzeigen
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
    
            action = options_menu.handle_action(options_menu.update(dt, events), sounds)
            options_menu.draw(screen)
            
            # Leertaste zum Hauptmenü
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "main_menu"
                    main_menu.activate()
                    
            if action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()
                
        # ====== CREDITS ======
        elif game_state == "credits":
            # Menü-Starfield auch hier anzeigen
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
    
            action = credits_screen.update(dt, events)
            credits_screen.draw(screen)
            
            if action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()
    
        # ====== SPIELEN ======
        elif game_state == "playing":
            # Normales Starfield für das Spielen
            starfield.update(dt)
            starfield.draw(screen)
            
            updatable.update(dt)

            # Im Spielzustand "playing", bei der Asteroidenkollision
            for asteroid in asteroids:
                # Schiffskollision - Schild berücksichtigen 
                if asteroid.collides_with(player) and not player.invincible and not player.shield_active:
                    lives -= 1
                    sounds.play_player_death()  # Spieler-Tod Sound
                    Particle.create_ship_explosion(player.position.x, player.position.y)
                    
                    if lives <= 0:
                        print(f"Game Over! Final Score: {score}")
                        game_over_screen.set_score(score)
                        game_over_screen.fade_in = True
                        game_over_screen.background_alpha = 0
                        game_state = "game_over"
                    else:
                        player.respawn()

                # Asteroidenkollision
                for shot in shots:
                    if asteroid.collides_with(shot):
                        sounds.play_explosion()  # Explosions-Sound
                        # Punktevergabe basierend auf Asteroidengröße
                        if asteroid.radius > ASTEROID_MIN_RADIUS * 2:
                            score += SCORE_LARGE
                        elif asteroid.radius > ASTEROID_MIN_RADIUS:
                            score += SCORE_MEDIUM
                        else:
                            score += SCORE_SMALL
                        
                        # Asteroidenexplosion
                        Particle.create_asteroid_explosion(asteroid.position.x, asteroid.position.y)
                        
                        asteroid.split()
                        shot.kill()
                        break

            # Bildschirm-Wrapping und Bullet-Handling
            for obj in updatable:
                if not hasattr(obj, 'position'):
                    continue
                    
                # Schüsse entfernen, wenn sie den Bildschirm verlassen
                if isinstance(obj, Shot):
                    if (obj.position.x < 0 or obj.position.x > SCREEN_WIDTH or
                        obj.position.y < 0 or obj.position.y > SCREEN_HEIGHT):
                        obj.kill()
                    continue
                
                # Wrapping für alle anderen Objekte
                if obj.position.x < 0:
                    obj.position.x = SCREEN_WIDTH
                elif obj.position.x > SCREEN_WIDTH:
                    obj.position.x = 0
                if obj.position.y < 0:
                    obj.position.y = SCREEN_HEIGHT
                elif obj.position.y > SCREEN_HEIGHT:
                    obj.position.y = 0
            
            # Objekte zeichnen
            for obj in drawable:
                obj.draw(screen)

            # HUD-Elemente mit angepassten Positionen
            
            # Score oben links
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(topleft=(20, 20))
            screen.blit(score_text, score_rect)
            
            # Lives oben links, unter dem Score
            lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
            lives_rect = lives_text.get_rect(topleft=(20, 50))
            screen.blit(lives_text, lives_rect)
            
            # Level oben links, unter den Lives
            level_text = font.render(f"Level: {level}", True, (200, 200, 200))
            level_rect = level_text.get_rect(topleft=(20, 80))
            screen.blit(level_text, level_rect)

            # Level-System aktualisieren
            current_level = min(score // POINTS_PER_LEVEL + 1, MAX_LEVEL)
            
            # Level-Up erkennen
            if current_level > level:
                # Level erhöhen
                level = current_level
                
                # Schwierigkeit anpassen
                asteroid_field.asteroid_count = min(BASE_ASTEROID_COUNT + (level - 1) * ASTEROID_COUNT_PER_LEVEL, 12)
                asteroid_field.spawn_interval = max(BASE_SPAWN_INTERVAL - (level - 1) * SPAWN_INTERVAL_REDUCTION, 0.8)
                
                # Level-Up-Anzeige aktivieren
                level_up_timer = LEVEL_UP_DISPLAY_TIME
                level_up_text = f"LEVEL {level}!"
                
                # Sound für Level-Up
                sounds.play_level_up()
                
                print(f"Level-Up! Jetzt Level {level}, Asteroiden: {asteroid_field.asteroid_count}, Intervall: {asteroid_field.spawn_interval}") 
           
            # Level-Up-Animation anzeigen, wenn aktiv
            if level_up_timer > 0:
                level_up_timer -= dt
                
                # Pulsierender Text
                size = int(72 * (1 + 0.2 * math.sin(level_up_timer * 10)))
                
                level_font = pygame.font.Font(None, size)
                level_surf = level_font.render(level_up_text, True, (255, 215, 0))  # Gold-Farbe
                level_rect = level_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
                
                # Animation mit Transparenz
                alpha = int(255 * min(1, level_up_timer / (LEVEL_UP_DISPLAY_TIME / 2)))
                if level_up_timer < LEVEL_UP_DISPLAY_TIME / 2:
                    level_surf.set_alpha(alpha)
                
                screen.blit(level_surf, level_rect)

            # Power-up Kollisionen
            for powerup in powerups:
                if powerup.collides_with(player):
                    player.activate_powerup(powerup.type)
                    powerup.kill()
        
        # ====== HIGHSCORE EINGABE ======
        elif game_state == "highscore_input":
            # Menü-Starfield auch hier anzeigen
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
    
            name = highscore_input.update(events)
            if name:
                # Highscore speichern und zur Anzeige wechseln
                highscore_manager.add_highscore(name, score)
                game_state = "highscore_display"
                score = 0  # Score zurücksetzen
            
            highscore_input.draw(screen)
        
        # ====== HIGHSCORE ANZEIGE ======
        elif game_state == "highscore_display":
            # Menü-Starfield auch hier anzeigen
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
    
            highscore_display.draw(screen)
            
            # Zurück zum Hauptmenü mit Leertaste oder ESC
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                        game_state = "main_menu"
                        main_menu.activate()
        
        # ====== GAME OVER ======
        elif game_state == "game_over":
            # Menü-Starfield auch hier anzeigen
            menu_starfield.update(dt)
            menu_starfield.draw(screen)
    
            action = game_over_screen.update(dt, events)
            game_over_screen.draw(screen)
            
            if action == "highscore_display":
                if highscore_manager.is_highscore(score):
                    game_state = "highscore_input"
                    highscore_input = HighscoreInput(score)
                else:
                    game_state = "highscore_display"
                    
            elif action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()
        
        # Bildschirm aktualisieren
        pygame.display.flip()
        
        # Delta-Zeit für konstante Geschwindigkeit
        dt = clock.tick(60) / 1000.0


if __name__ == "__main__":
    main()