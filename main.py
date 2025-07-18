import sys
import pygame
import math
import random
import time
from modul.constants import *
from modul._version import __version__
from modul.player import Player
from modul.asteroid import Asteroid, EnemyShip
from modul.asteroidfield import AsteroidField
from modul.shot import Shot
from modul.particle import Particle
from modul.sounds import Sounds
from modul.starfield import Starfield, MenuStarfield
from modul.powerup import PowerUp
from modul.highscore import HighscoreManager, HighscoreInput, HighscoreDisplay
from modul.menu import (
    MainMenu,
    PauseMenu,
    OptionsMenu,
    CreditsScreen,
    GameOverScreen,
    DifficultyMenu,
    SoundTestMenu,
    AchievementsMenu,
    ShipSelectionMenu,
)
from modul.ships import ship_manager
from modul.tutorial import Tutorial
from modul.settings import Settings
from modul.boss import Boss
from modul.bossprojectile import BossProjectile
from modul.achievements import AchievementSystem
from modul.achievement_notification import AchievementNotificationManager
from modul.groups import collidable, drawable, updatable


class GameSettings:
    def __init__(self):
        self.fullscreen = False


game_settings = GameSettings()


def main():

    global sounds, player, PLAYER_INVINCIBLE_TIME, game_settings

    global game_state, score, lives, level

    global achievement_system, achievement_notifications
    achievement_system = AchievementSystem()
    achievement_notifications = AchievementNotificationManager()

    global powerups_collected, asteroids_destroyed, shields_used, triple_shots_used, speed_boosts_used
    powerups_collected = 0
    asteroids_destroyed = 0
    shields_used = 0
    triple_shots_used = 0
    speed_boosts_used = 0
    achievement_system.set_notification_callback(
        achievement_notifications.add_notification)
    global boss_active, boss_defeated_timer, boss_defeated_message

    pygame.init()

    try:
        pygame.mixer.init(44100, -16, 2, 2048)
        print("Pygame Mixer initialized successfully")
    except Exception as e:
        print(f"Error during mixer initialization: {e}")

    pygame.display.set_caption(f"Ajitroids v{__version__}")

    clock = pygame.time.Clock()

    game_settings = Settings()

    if game_settings.fullscreen:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        print("Fullscreen mode activated")
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print("Windowed mode activated")

    sounds = Sounds()

    achievement_notifications.set_sounds(sounds)

    pygame.time.delay(200)

    if game_settings.music_on:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/background.mp3")
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)
            pygame.time.delay(100)
        except Exception as e:
            print(f"❌ Error starting music: {e}")
            import os

            print(f"Background.mp3 exists: {
                  os.path.exists('assets/background.mp3')}")
            if os.path.exists("assets/background.mp3"):
                print(f"Background.mp3 size: {
                      os.path.getsize('assets/background.mp3')} bytes")
    else:
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.stop()
        print("Music disabled at startup")

    sounds.toggle_sound(game_settings.sound_on)

    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    Asteroid.containers = asteroids, updatable, drawable
    Shot.containers = shots, updatable, drawable
    Particle.containers = particles, updatable, drawable
    PowerUp.containers = powerups, updatable, drawable
    Player.containers = updatable, drawable
    AsteroidField.containers = updatable
    Boss.containers = updatable, drawable
    BossProjectile.containers = updatable, drawable

    Shot.set_asteroids(asteroids)

    asteroid_field = AsteroidField()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    starfield = Starfield()
    menu_starfield = MenuStarfield(200)
    font = pygame.font.Font(None, 36)
    dt = 0
    lives = PLAYER_LIVES
    score = 0
    level = 1
    level_up_timer = 0
    level_up_text = ""

    highscore_manager = HighscoreManager()
    highscore_input = None
    highscore_display = HighscoreDisplay(highscore_manager)

    main_menu = MainMenu()
    pause_menu = PauseMenu()
    options_menu = OptionsMenu(game_settings, sounds)
    sound_test_menu = SoundTestMenu()
    sound_test_menu.set_sounds(sounds)
    credits_screen = CreditsScreen()
    game_over_screen = GameOverScreen()
    difficulty_menu = DifficultyMenu()
    ship_selection_menu = ShipSelectionMenu()
    tutorial = Tutorial()

    difficulty = "normal"

    game_state = "main_menu"
    main_menu.activate()

    boss_active = False
    boss_defeated_timer = 0
    boss_defeated_message = ""

    if "player" not in globals() or not player:
        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    if "PLAYER_INVINCIBLE_TIME" not in globals() or not PLAYER_INVINCIBLE_TIME:
        PLAYER_INVINCIBLE_TIME = 3

    if "game_settings" not in globals() or not game_settings:
        game_settings = Settings()

    print(
        f"Initialized variables: player={player}, sounds={sounds}, PLAYER_INVINCIBLE_TIME={
            PLAYER_INVINCIBLE_TIME}, game_settings={game_settings}"
    )

    toggle_message = None
    toggle_message_timer = 0

    last_spawn_time = time.time()
    spawn_interval = random.uniform(10, 30)
    max_enemy_ships = {"easy": 1, "normal": 2, "hard": 3}
    current_enemy_ships = []

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                if event.key == pygame.K_F10:
                    game_settings.music_on = not game_settings.music_on
                    game_settings.save()
                    if game_settings.music_on:
                        pygame.mixer.music.set_volume(
                            game_settings.music_volume)
                        pygame.mixer.music.play(-1)
                        toggle_message = "Music Enabled"
                    else:
                        pygame.mixer.music.stop()
                        toggle_message = "Music Disabled"
                    toggle_message_timer = 2
                elif event.key == pygame.K_F9:
                    game_settings.sound_on = not game_settings.sound_on
                    game_settings.save()
                    sounds.toggle_sound(game_settings.sound_on)
                    toggle_message = "Sound Effects Enabled" if game_settings.sound_on else "Sound Effects Disabled"
                    toggle_message_timer = 2
                elif event.key == pygame.K_b and player:
                    player.cycle_weapon()

        if toggle_message and toggle_message_timer > 0:
            font = pygame.font.Font(None, 36)
            message_surface = font.render(
                toggle_message, True, (255, 255, 255))
            message_rect = message_surface.get_rect(
                center=(SCREEN_WIDTH / 2, 50))
            screen.blit(message_surface, message_rect)
            toggle_message_timer -= dt
            if toggle_message_timer <= 0:
                toggle_message = None

        if toggle_message and toggle_message_timer > 0:
            font = pygame.font.Font(None, 36)
            message_surface = font.render(
                toggle_message, True, (255, 255, 255))
            message_rect = message_surface.get_rect(
                center=(SCREEN_WIDTH / 2, 50))
            screen.blit(message_surface, message_rect)
            toggle_message_timer -= dt
            if toggle_message_timer <= 0:
                toggle_message = None

        if game_state == "playing" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "pause"
                pause_menu.activate()

        screen.fill("black")

        if game_state == "main_menu":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = main_menu.update(dt, events)
            main_menu.draw(screen)

            version_font = pygame.font.Font(
                None, int(MENU_ITEM_FONT_SIZE / 1.5))
            version_text = version_font.render(
                __version__, True, pygame.Color(MENU_UNSELECTED_COLOR))
            version_rect = version_text.get_rect(
                bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            screen.blit(version_text, version_rect)

            if game_settings.music_on and not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.load("assets/background.mp3")
                    pygame.mixer.music.set_volume(0.8)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"❌ Music error in main menu: {e}")

            if action == "start_game":
                game_state = "difficulty_select"
                difficulty_menu.activate()

            elif action == "tutorial":
                game_state = "tutorial"

            elif action == "highscores":
                game_state = "highscore_display"

            elif action == "options":
                game_state = "options"
                options_menu.activate()

            elif action == "credits":
                game_state = "credits"
                credits_screen.fade_in = True
                credits_screen.background_alpha = 0
                credits_screen.scroll_position = SCREEN_HEIGHT

            elif action == "exit":
                return

            elif action == "achievements":
                game_state = "achievements"
                achievements_menu = AchievementsMenu(achievement_system)
                achievements_menu.activate()

        elif game_state == "difficulty_select":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = difficulty_menu.update(dt, events)
            difficulty_menu.draw(screen)

            if action == "difficulty_easy":
                difficulty = "easy"
                game_state = "ship_selection"
                ship_selection_menu.activate()

            elif action == "difficulty_normal":
                difficulty = "normal"
                game_state = "ship_selection"
                ship_selection_menu.activate()

            elif action == "difficulty_hard":
                difficulty = "hard"
                game_state = "ship_selection"
                ship_selection_menu.activate()

            elif action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()

            for event in events:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE):
                    game_state = "main_menu"
                    main_menu.activate()

        elif game_state == "ship_selection":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = ship_selection_menu.update(dt, events)
            ship_selection_menu.draw(screen)

            if action == "start_game":
                selected_ship = ship_manager.current_ship

                game_state = "playing"
                score = 0
                lives = PLAYER_LIVES
                level = 1

                last_spawn_time = time.time()
                spawn_interval = random.uniform(10, 30)
                current_enemy_ships = []

                for asteroid in list(asteroids):
                    asteroid.kill()
                for powerup in list(powerups):
                    powerup.kill()
                for shot in list(shots):
                    shot.kill()
                for particle in list(particles):
                    particle.kill()

                for obj in list(collidable):
                    if isinstance(obj, EnemyShip):
                        obj.kill()

                if player in updatable:
                    player.kill()
                player = Player(SCREEN_WIDTH / 2,
                                SCREEN_HEIGHT / 2, selected_ship)
                player.sounds = sounds

                if difficulty == "easy":
                    asteroid_field.asteroid_count = 3
                    asteroid_field.spawn_interval = 8.0
                elif difficulty == "normal":
                    asteroid_field.asteroid_count = 5
                    asteroid_field.spawn_interval = 5.0
                elif difficulty == "hard":
                    asteroid_field.asteroid_count = 7
                    asteroid_field.spawn_interval = 3.0

                for _ in range(3):
                    asteroid_field.spawn_random()

            elif action == "difficulty_select":
                game_state = "difficulty_select"
                difficulty_menu.activate()

        elif game_state == "tutorial":
            action = tutorial.update(dt, events)
            tutorial.draw(screen)

            if action == "back":
                game_state = "main_menu"
                main_menu.activate()

        elif game_state == "pause":
            for obj in drawable:
                obj.draw(screen)

            action = pause_menu.update(dt, events)
            pause_menu.draw(screen)

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "main_menu"
                    main_menu.activate()

            if action == "continue":
                game_state = "playing"

            elif action == "restart":
                game_state = "playing"
                score = 0
                lives = PLAYER_LIVES

                last_spawn_time = time.time()
                spawn_interval = random.uniform(10, 30)
                current_enemy_ships = []

                for asteroid in asteroids:
                    asteroid.kill()
                for powerup in powerups:
                    powerup.kill()
                for shot in shots:
                    shot.kill()
                for particle in particles:
                    particle.kill()

                for obj in list(collidable):
                    if isinstance(obj, EnemyShip):
                        obj.kill()

                player.position.x = RESPAWN_POSITION_X
                player.position.y = RESPAWN_POSITION_Y
                player.velocity = pygame.Vector2(0, 0)
                player.rotation = 0
                player.respawn()

            elif action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()

        elif game_state == "options":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = options_menu.handle_action(
                options_menu.update(dt, events), sounds)
            options_menu.draw(screen)

            for event in events:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE):
                    game_state = "main_menu"
                    main_menu.activate()

            if action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()
            elif action == "sound_test":
                game_state = "sound_test"
                sound_test_menu.activate()

        elif game_state == "sound_test":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = sound_test_menu.update(dt, events)
            if action:
                result = sound_test_menu.handle_action(action)
                if result == "options":
                    game_state = "options"
                    options_menu.activate()

            sound_test_menu.draw(screen)

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "options"
                    options_menu.activate()

        elif game_state == "credits":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = credits_screen.update(dt, events)
            credits_screen.draw(screen)

            if action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()

        elif game_state == "playing":
            starfield.update(dt)
            starfield.draw(screen)

            asteroid_field.update(dt)

            if time.time() - last_spawn_time > spawn_interval:
                if len(current_enemy_ships) < max_enemy_ships[difficulty]:
                    enemy_ship = EnemyShip(random.randint(
                        0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 30)
                    updatable.add(enemy_ship)
                    drawable.add(enemy_ship)
                    collidable.add(enemy_ship)
                    current_enemy_ships.append(enemy_ship)
                    last_spawn_time = time.time()
                    spawn_interval = random.uniform(10, 30)
                    print(f"EnemyShip spawned! Current count: {
                          len(current_enemy_ships)}, Max: {max_enemy_ships[difficulty]}")

            current_enemy_ships = [
                ship for ship in current_enemy_ships if ship in updatable]

            for obj in updatable:
                if isinstance(obj, EnemyShip):
                    obj.update(dt, player.position)
                else:
                    obj.update(dt)

            asteroid_list = list(asteroids)
            for i in range(len(asteroid_list)):
                a1 = asteroid_list[i]
                for j in range(i + 1, len(asteroid_list)):
                    a2 = asteroid_list[j]
                    dx = a2.position.x - a1.position.x
                    dy = a2.position.y - a1.position.y
                    dist = math.hypot(dx, dy)
                    min_dist = a1.radius + a2.radius
                    if dist < min_dist and dist > 0:

                        overlap = min_dist - dist
                        nx = dx / dist
                        ny = dy / dist
                        a1.position.x -= nx * overlap / 2
                        a1.position.y -= ny * overlap / 2
                        a2.position.x += nx * overlap / 2
                        a2.position.y += ny * overlap / 2

                        v1 = a1.velocity
                        v2 = a2.velocity
                        a1.velocity, a2.velocity = v2, v1

            for asteroid in asteroids:
                if asteroid.collides_with(player) and not player.invincible and not player.shield_active:
                    lives -= 1
                    sounds.play_player_hit()
                    Particle.create_ship_explosion(
                        player.position.x, player.position.y)

                    if lives <= 0:
                        print(f"Game Over! Final Score: {score}")
                        sounds.play_game_over()
                        game_over_screen.set_score(score)
                        game_over_screen.fade_in = True
                        game_over_screen.background_alpha = 0
                        game_state = "game_over"
                    else:
                        player.respawn()

                for shot in shots:
                    if asteroid.collides_with(shot):
                        sounds.play_explosion()

                        original_size = asteroid.radius
                        is_large_asteroid = original_size >= ASTEROID_MIN_RADIUS * 2
                        is_medium_asteroid = ASTEROID_MIN_RADIUS < original_size < ASTEROID_MIN_RADIUS * 2

                        if is_large_asteroid:
                            score += SCORE_LARGE
                        elif is_medium_asteroid:
                            score += SCORE_MEDIUM
                        else:
                            score += SCORE_SMALL

                        Particle.create_asteroid_explosion(
                            asteroid.position.x, asteroid.position.y)

                        if not achievement_system.is_unlocked("First Blood"):
                            achievement_system.unlock("First Blood")

                        asteroids_destroyed += 1

                        if asteroids_destroyed >= 1000 and not achievement_system.is_unlocked("Asteroid Hunter"):
                            achievement_system.unlock("Asteroid Hunter")

                        if score >= 250000 and not achievement_system.is_unlocked("High Scorer"):
                            achievement_system.unlock("High Scorer")

                        if is_large_asteroid and random.random() < POWERUP_SPAWN_CHANCE:
                            if len(powerups) < POWERUP_MAX_COUNT:
                                powerup_type = random.choice(POWERUP_TYPES)
                                PowerUp(asteroid.position.x,
                                        asteroid.position.y, powerup_type)
                                print(
                                    f"Power-Up {powerup_type} appears from large asteroid!")

                        asteroid.split()
                        shot.kill()
                        break

            for obj in list(collidable):
                if isinstance(obj, EnemyShip):

                    if obj.collides_with(player) and not player.invincible and not player.shield_active:
                        lives -= 1
                        sounds.play_player_hit()
                        Particle.create_ship_explosion(
                            player.position.x, player.position.y)
                        obj.split()

                        if obj in current_enemy_ships:
                            current_enemy_ships.remove(obj)

                        if lives <= 0:
                            print(f"Game Over! Final Score: {score}")
                            sounds.play_game_over()
                            game_over_screen.set_score(score)
                            game_over_screen.fade_in = True
                            game_over_screen.background_alpha = 0
                            game_state = "game_over"
                        else:
                            player.respawn()

                    for shot in shots:
                        if obj.collides_with(shot):
                            sounds.play_explosion()
                            score += SCORE_MEDIUM
                            obj.split()
                            shot.kill()

                            if obj in current_enemy_ships:
                                current_enemy_ships.remove(obj)
                            print(f"EnemyShip destroyed! Remaining count: {
                                  len(current_enemy_ships)}")
                            break

            for enemy_ship in current_enemy_ships:
                for asteroid in asteroids:
                    if enemy_ship.collides_with(asteroid):
                        speed = enemy_ship.velocity.length()
                        enemy_ship.velocity = pygame.Vector2(
                            random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * speed
                        print(
                            f"EnemyShip changed direction due to asteroid collision.")

            for obj in updatable:
                if not hasattr(obj, "position"):
                    continue

                if isinstance(obj, Shot):
                    if (
                        obj.position.x < 0
                        or obj.position.x > SCREEN_WIDTH
                        or obj.position.y < 0
                        or obj.position.y > SCREEN_HEIGHT
                    ):
                        obj.kill()
                    continue

                if obj.position.x < 0:
                    obj.position.x = SCREEN_WIDTH
                elif obj.position.x > SCREEN_WIDTH:
                    obj.position.x = 0
                if obj.position.y < 0:
                    obj.position.y = SCREEN_HEIGHT
                elif obj.position.y > SCREEN_HEIGHT:
                    obj.position.y = 0

            for obj in drawable:
                obj.draw(screen)

            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(topleft=(20, 20))
            screen.blit(score_text, score_rect)

            lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
            lives_rect = lives_text.get_rect(topleft=(20, 50))
            screen.blit(lives_text, lives_rect)

            level_text = font.render(f"Level: {level}", True, (200, 200, 200))
            level_rect = level_text.get_rect(topleft=(20, 80))
            screen.blit(level_text, level_rect)

            difficulty_color = {"easy": (0, 255, 0), "normal": (255, 255, 0), "hard": (255, 0, 0)}.get(
                difficulty, (200, 200, 200)
            )

            difficulty_text = font.render(
                f"Difficulty: {difficulty.capitalize()}", True, difficulty_color)
            difficulty_rect = difficulty_text.get_rect(topleft=(20, 110))
            screen.blit(difficulty_text, difficulty_rect)

            if player:
                player.draw_weapon_hud(screen)

            current_level = min(score // POINTS_PER_LEVEL + 1, MAX_LEVEL)

            if current_level > level:
                if current_level % BOSS_LEVEL_INTERVAL == 0:
                    boss = Boss(current_level)
                    boss_active = True
                    boss_projectiles = pygame.sprite.Group()
                    level_up_text = "BOSS FIGHT!"
                    level_up_timer = LEVEL_UP_DISPLAY_TIME * 2
                    for asteroid in list(asteroids):
                        asteroid.kill()
                    print(f"Boss fight started at level {current_level}!")
                    sounds.play_boss_music()

                level = current_level

                if level == 50:
                    if difficulty == "easy" and not ship_manager.is_ship_unlocked("speedster"):
                        ship_manager.unlock_ship_with_notification(
                            "speedster", achievement_notifications.add_notification)
                    elif difficulty == "normal" and not ship_manager.is_ship_unlocked("tank"):
                        ship_manager.unlock_ship_with_notification(
                            "tank", achievement_notifications.add_notification)
                    elif difficulty == "hard" and not ship_manager.is_ship_unlocked("destroyer"):
                        ship_manager.unlock_ship_with_notification(
                            "destroyer", achievement_notifications.add_notification)

                if level >= 666 and not achievement_system.is_unlocked("Level Master"):
                    achievement_system.unlock("Level Master")

                if level <= 10:
                    asteroid_field.asteroid_count = min(
                        BASE_ASTEROID_COUNT + (level - 1) * ASTEROID_COUNT_PER_LEVEL, 12)
                    asteroid_field.spawn_interval = max(
                        BASE_SPAWN_INTERVAL - (level - 1) * SPAWN_INTERVAL_REDUCTION, 1.0)

                if level_up_timer <= 0:
                    level_up_timer = LEVEL_UP_DISPLAY_TIME
                    level_up_text = f"LEVEL {level}!"

                sounds.play_level_up()

                print(
                    f"Level up! Now level {level}, asteroids: {
                        asteroid_field.asteroid_count}, interval: {asteroid_field.spawn_interval}"
                )

            if level_up_timer > 0:
                level_up_timer -= dt

                size = int(72 * (1 + 0.2 * math.sin(level_up_timer * 10)))

                level_font = pygame.font.Font(None, size)
                level_surf = level_font.render(
                    level_up_text, True, (255, 215, 0))
                level_rect = level_surf.get_rect(
                    center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))

                alpha = int(255 * min(1, level_up_timer /
                            (LEVEL_UP_DISPLAY_TIME / 2)))
                if level_up_timer < LEVEL_UP_DISPLAY_TIME / 2:
                    level_surf.set_alpha(alpha)

                screen.blit(level_surf, level_rect)

            for powerup in powerups:
                if powerup.collides_with(player):
                    player.activate_powerup(powerup.type)
                    powerup.kill()

                    powerups_collected += 1

                    if powerup.type == "shield":
                        shields_used += 1
                    elif powerup.type == "triple_shot":
                        triple_shots_used += 1
                    elif powerup.type == "speed_boost":
                        speed_boosts_used += 1

                    if powerups_collected >= 250 and not achievement_system.is_unlocked("Power User"):
                        achievement_system.unlock("Power User")

                    if shields_used >= 50 and not achievement_system.is_unlocked("Shield Expert"):
                        achievement_system.unlock("Shield Expert")

                    if speed_boosts_used >= 25 and not achievement_system.is_unlocked("Speed Demon"):
                        achievement_system.unlock("Speed Demon")

                    if triple_shots_used >= 20 and not achievement_system.is_unlocked("Triple Threat"):
                        achievement_system.unlock("Triple Threat")

            if current_level > level and current_level % BOSS_LEVEL_INTERVAL == 0:
                boss = Boss(current_level)
                boss_active = True
                boss_projectiles = pygame.sprite.Group()
                level_message = "BOSS FIGHT!"
                level_message_timer = LEVEL_UP_DISPLAY_TIME
                for asteroid in list(asteroids):
                    asteroid.kill()

            if boss_active and boss in updatable:
                boss_attack = boss.update(dt, player.position)

                if boss_attack:
                    if boss_attack["type"] == "circle":
                        for i in range(boss_attack["count"]):
                            angle = math.radians(
                                i * (360 / boss_attack["count"]))
                            velocity = pygame.Vector2(
                                math.cos(angle), math.sin(angle)) * BOSS_PROJECTILE_SPEED
                            BossProjectile(boss.position.x,
                                           boss.position.y, velocity, "normal")
                            sounds.play_enemy_shoot()

                    elif boss_attack["type"] == "spiral":
                        base_angle = pygame.time.get_ticks() % 360
                        for i in range(boss_attack["count"]):
                            angle = math.radians(
                                base_angle + i * (360 / boss_attack["count"]))
                            velocity = pygame.Vector2(
                                math.cos(angle), math.sin(angle)) * BOSS_PROJECTILE_SPEED
                            BossProjectile(boss.position.x,
                                           boss.position.y, velocity, "normal")
                            sounds.play_enemy_shoot()

                    elif boss_attack["type"] == "targeted":
                        if player in updatable:
                            direction = (player.position -
                                         boss.position).normalize()

                            velocity = direction * BOSS_PROJECTILE_SPEED
                            BossProjectile(boss.position.x,
                                           boss.position.y, velocity, "homing")

                            for i in range(1, boss_attack["count"]):
                                offset = 10 * i if i % 2 == 0 else -10 * i
                                offset_dir = direction.rotate(offset)
                                BossProjectile(
                                    boss.position.x, boss.position.y, offset_dir * BOSS_PROJECTILE_SPEED, "normal")
                        sounds.play_enemy_shoot()

                for shot in shots:
                    if boss.collides_with(shot):
                        boss_defeated = boss.take_damage(shot.damage)
                        shot.kill()
                        sounds.play_hit()

                        if boss_defeated:
                            score += BOSS_SCORE
                            boss_active = False

                            if not achievement_system.is_unlocked("Boss Slayer"):
                                achievement_system.unlock("Boss Slayer")

                            lives += 1
                            sounds.play_extra_life()

                            boss_defeated_timer = 3.0
                            boss_defeated_message = "BOSS DEFEATED! +1 LIFE!"

            achievement_notifications.update(dt)
            achievement_notifications.draw(screen)

        elif game_state == "highscore_input":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            name = highscore_input.update(events)
            if name:
                highscore_manager.add_highscore(name, score)
                game_state = "highscore_display"
                score = 0

            highscore_input.draw(screen)

        elif game_state == "highscore_display":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = highscore_display.update(dt, events)
            highscore_display.draw(screen)

            if action == "main_menu":
                game_state = "main_menu"
                main_menu.activate()

        elif game_state == "game_over":
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

        elif game_state == "achievements":
            menu_starfield.update(dt)
            menu_starfield.draw(screen)

            action = achievements_menu.update(dt, events)
            achievements_menu.draw(screen)

            if action == "back":
                game_state = "main_menu"

        pygame.display.flip()

        dt = clock.tick(60) / 1000.0


def player_hit():
    global lives

    lives -= 1
    sounds.play_explosion()

    Particle.create_player_explosion(player.position.x, player.position.y)

    if lives > 0:
        player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        player.velocity = pygame.Vector2(0, 0)
        player.invincible = True
        player.invincible_timer = PLAYER_INVINCIBLE_TIME
        print(f"Player respawned with {
              PLAYER_INVINCIBLE_TIME} seconds of invincibility")
    else:
        player.kill()
        game_state = "game_over"
        sounds.play_game_over()


def debug_music_status():
    print(f"🎵 Music status:")
    print(f"   - Busy: {pygame.mixer.music.get_busy()}")
    print(f"   - Volume: {pygame.mixer.music.get_volume()}")
    print(f"   - Mixer Init: {pygame.mixer.get_init()}")
    print(f"   - Settings Music: {game_settings.music_on}")


def toggle_fullscreen():
    global screen
    game_settings.fullscreen = not game_settings.fullscreen
    if game_settings.fullscreen:
        screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        print("Switched to fullscreen mode")
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print("Switched to windowed mode")


if __name__ == "__main__":
    main()
    print("Game over.")
