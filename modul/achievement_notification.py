import pygame
import time
from modul.constants import ARCADE_MODE_BONUS_TIME as ARCADE_MODE_BONUS_TIME, ARCADE_MODE_TIME as ARCADE_MODE_TIME, ASTEROID_COUNT_PER_LEVEL as ASTEROID_COUNT_PER_LEVEL, ASTEROID_IRREGULARITY as ASTEROID_IRREGULARITY, ASTEROID_KINDS as ASTEROID_KINDS, ASTEROID_MAX_RADIUS as ASTEROID_MAX_RADIUS, ASTEROID_MIN_RADIUS as ASTEROID_MIN_RADIUS, ASTEROID_SPAWN_RATE as ASTEROID_SPAWN_RATE, ASTEROID_VERTICES as ASTEROID_VERTICES, BASE_ASTEROID_COUNT as BASE_ASTEROID_COUNT, BASE_SPAWN_INTERVAL as BASE_SPAWN_INTERVAL, BOSS_ATTACK_INTERVAL as BOSS_ATTACK_INTERVAL, BOSS_BASE_HEALTH as BOSS_BASE_HEALTH, BOSS_COLOR as BOSS_COLOR, BOSS_DEATH_DURATION as BOSS_DEATH_DURATION, BOSS_HEALTH_PER_LEVEL as BOSS_HEALTH_PER_LEVEL, BOSS_LEVEL_INTERVAL as BOSS_LEVEL_INTERVAL, BOSS_MOVE_SPEED as BOSS_MOVE_SPEED, BOSS_PROJECTILE_COLORS as BOSS_PROJECTILE_COLORS, BOSS_PROJECTILE_RADIUS as BOSS_PROJECTILE_RADIUS, BOSS_PROJECTILE_SPEED as BOSS_PROJECTILE_SPEED, BOSS_RADIUS as BOSS_RADIUS, BOSS_SCORE as BOSS_SCORE, COLLISION_DEBUG as COLLISION_DEBUG, CREDITS_DEVELOPER as CREDITS_DEVELOPER, CREDITS_GAME_NAME as CREDITS_GAME_NAME, CREDITS_GRAPHICS as CREDITS_GRAPHICS, CREDITS_LINE_SPACING as CREDITS_LINE_SPACING, CREDITS_MASTERMIND as CREDITS_MASTERMIND, CREDITS_SCROLL_SPEED as CREDITS_SCROLL_SPEED, CREDITS_SOUND as CREDITS_SOUND, CREDITS_SPECIAL_THANKS as CREDITS_SPECIAL_THANKS, CREDITS_TITLE as CREDITS_TITLE, CREDITS_WEBSITE as CREDITS_WEBSITE, DEFAULT_HIGHSCORES as DEFAULT_HIGHSCORES, DIFFICULTY_EASY_ASTEROIDS as DIFFICULTY_EASY_ASTEROIDS, DIFFICULTY_EASY_INTERVAL as DIFFICULTY_EASY_INTERVAL, DIFFICULTY_HARD_ASTEROIDS as DIFFICULTY_HARD_ASTEROIDS, DIFFICULTY_HARD_INTERVAL as DIFFICULTY_HARD_INTERVAL, DIFFICULTY_NORMAL_ASTEROIDS as DIFFICULTY_NORMAL_ASTEROIDS, DIFFICULTY_NORMAL_INTERVAL as DIFFICULTY_NORMAL_INTERVAL, EXPLOSION_PARTICLES as EXPLOSION_PARTICLES, HIGHSCORE_ALLOWED_CHARS as HIGHSCORE_ALLOWED_CHARS, HIGHSCORE_DEFAULT_NAME as HIGHSCORE_DEFAULT_NAME, HIGHSCORE_FILE as HIGHSCORE_FILE, HIGHSCORE_MAX_ENTRIES as HIGHSCORE_MAX_ENTRIES, HIGHSCORE_NAME_LENGTH as HIGHSCORE_NAME_LENGTH, INVINCIBILITY_TIME as INVINCIBILITY_TIME, LASER_AMMO as LASER_AMMO, LEVEL_UP_DISPLAY_TIME as LEVEL_UP_DISPLAY_TIME, MAX_LEVEL as MAX_LEVEL, MENU_BACKGROUND_ALPHA as MENU_BACKGROUND_ALPHA, MENU_BUTTON_HEIGHT as MENU_BUTTON_HEIGHT, MENU_BUTTON_PADDING as MENU_BUTTON_PADDING, MENU_BUTTON_RADIUS as MENU_BUTTON_RADIUS, MENU_BUTTON_WIDTH as MENU_BUTTON_WIDTH, MENU_FADE_SPEED as MENU_FADE_SPEED, MENU_ITEM_FONT_SIZE as MENU_ITEM_FONT_SIZE, MENU_ITEM_SPACING as MENU_ITEM_SPACING, MENU_SELECTED_COLOR as MENU_SELECTED_COLOR, MENU_TITLE_COLOR as MENU_TITLE_COLOR, MENU_TITLE_FONT_SIZE as MENU_TITLE_FONT_SIZE, MENU_TRANSITION_SPEED as MENU_TRANSITION_SPEED, MENU_UNSELECTED_COLOR as MENU_UNSELECTED_COLOR, MISSILE_AMMO as MISSILE_AMMO, PARTICLE_COLORS as PARTICLE_COLORS, PLAYER_ACCELERATION as PLAYER_ACCELERATION, PLAYER_FRICTION as PLAYER_FRICTION, PLAYER_LIVES as PLAYER_LIVES, PLAYER_MAX_SPEED as PLAYER_MAX_SPEED, PLAYER_RADIUS as PLAYER_RADIUS, PLAYER_ROTATION_SPEED as PLAYER_ROTATION_SPEED, PLAYER_SHOOT_COOLDOWN as PLAYER_SHOOT_COOLDOWN, PLAYER_SHOOT_SPEED as PLAYER_SHOOT_SPEED, PLAYER_SPEED as PLAYER_SPEED, PLAYER_TURN_SPEED as PLAYER_TURN_SPEED, POINTS_PER_LEVEL as POINTS_PER_LEVEL, POWERUP_COLORS as POWERUP_COLORS, POWERUP_LIFETIME as POWERUP_LIFETIME, POWERUP_MAX_COUNT as POWERUP_MAX_COUNT, POWERUP_RADIUS as POWERUP_RADIUS, POWERUP_SPAWN_CHANCE as POWERUP_SPAWN_CHANCE, POWERUP_TYPES as POWERUP_TYPES, RAPID_FIRE_COOLDOWN as RAPID_FIRE_COOLDOWN, RAPID_FIRE_DURATION as RAPID_FIRE_DURATION, RESPAWN_POSITION_X as RESPAWN_POSITION_X, RESPAWN_POSITION_Y as RESPAWN_POSITION_Y, SCORE_LARGE as SCORE_LARGE, SCORE_MEDIUM as SCORE_MEDIUM, SCORE_SMALL as SCORE_SMALL, SCREEN_HEIGHT as SCREEN_HEIGHT, SCREEN_WIDTH as SCREEN_WIDTH, SHIELD_DURATION as SHIELD_DURATION, SHOTGUN_AMMO as SHOTGUN_AMMO, SHOT_RADIUS as SHOT_RADIUS, SPAWN_INTERVAL_REDUCTION as SPAWN_INTERVAL_REDUCTION, STAR_COLORS as STAR_COLORS, STAR_COUNT as STAR_COUNT, STAR_SIZES as STAR_SIZES, TRIPLE_SHOT_DURATION as TRIPLE_SHOT_DURATION, WEAPON_COLORS as WEAPON_COLORS, WEAPON_LASER as WEAPON_LASER, WEAPON_MISSILE as WEAPON_MISSILE, WEAPON_SHOTGUN as WEAPON_SHOTGUN, WEAPON_STANDARD as WEAPON_STANDARD, generate_default_highscores as generate_default_highscores, random as random


class AchievementNotification:
    def __init__(self, achievement_name, achievement_description):
        self.name = achievement_name
        self.description = achievement_description
        self.display_time = 4.0
        self.fade_time = 1.0
        self.start_time = time.time()
        self.animation_progress = 0.0
        self.is_fading_out = False
        self.target_x = SCREEN_WIDTH - 350
        self.target_y = 80
        self.current_x = SCREEN_WIDTH
        self.current_y = self.target_y
        self.title_font = pygame.font.Font(None, 32)
        self.desc_font = pygame.font.Font(None, 20)
        self.sound_played = False

    def update(self, dt):
        current_time = time.time()
        elapsed = current_time - self.start_time

        if elapsed < self.fade_time:
            self.animation_progress = elapsed / self.fade_time
            self.current_x = SCREEN_WIDTH - (SCREEN_WIDTH - self.target_x) * self._ease_out(self.animation_progress)

        elif elapsed < self.display_time - self.fade_time:
            self.animation_progress = 1.0
            self.current_x = self.target_x

        elif elapsed < self.display_time:
            if not self.is_fading_out:
                self.is_fading_out = True
            fade_progress = (elapsed - (self.display_time - self.fade_time)) / self.fade_time
            self.animation_progress = 1.0 - fade_progress
            self.current_x = self.target_x + (SCREEN_WIDTH - self.target_x) * fade_progress

        else:
            return False
        return True

    def _ease_out(self, t):
        return 1 - (1 - t) ** 3

    def draw(self, screen):
        if self.animation_progress <= 0:
            return

        notification_width = 320
        notification_height = 80
        alpha = int(255 * self.animation_progress)
        bg_surface = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)

        for i in range(notification_height):
            gradient_alpha = int(alpha * 0.9 * (1 - i / notification_height * 0.3))
            color = (20, 20, 60, gradient_alpha)
            pygame.draw.rect(bg_surface, color, (0, i, notification_width, 1))

        border_color = (255, 215, 0, alpha)
        pygame.draw.rect(bg_surface, border_color, (0, 0, notification_width, notification_height), 3)

        rect_x = int(self.current_x)
        rect_y = int(self.current_y)
        screen.blit(bg_surface, (rect_x, rect_y))

        header_color = (255, 215, 0, alpha)
        try:
            from modul.i18n import gettext
        except Exception:
            def gettext(k):
                return k

        header_text = gettext("achievement_unlocked")
        header_surf = self.title_font.render(header_text, True, header_color)
        header_rect = header_surf.get_rect(center=(rect_x + notification_width // 2, rect_y + 20))

        if alpha < 255:
            header_surf.set_alpha(alpha)
        screen.blit(header_surf, header_rect)

        name_color = (255, 255, 255, alpha)
        name_surf = self.desc_font.render(self.name, True, name_color)
        name_rect = name_surf.get_rect(center=(rect_x + notification_width // 2, rect_y + 45))

        if alpha < 255:
            name_surf.set_alpha(alpha)
        screen.blit(name_surf, name_rect)

        desc_text = self.description
        if len(desc_text) > 35:
            desc_text = desc_text[:32] + "..."

        desc_color = (200, 200, 200, alpha)
        desc_surf = self.desc_font.render(desc_text, True, desc_color)
        desc_rect = desc_surf.get_rect(center=(rect_x + notification_width // 2, rect_y + 65))

        if alpha < 255:
            desc_surf.set_alpha(alpha)
        screen.blit(desc_surf, desc_rect)


class AchievementNotificationManager:
    def __init__(self, sounds=None):
        self.notifications = []
        self.max_notifications = 3
        self.sounds = sounds

    def set_sounds(self, sounds):
        self.sounds = sounds

    def add_notification(self, achievement_name, achievement_description):
        for notification in self.notifications:
            if notification.name == achievement_name:
                return
        notification = AchievementNotification(achievement_name, achievement_description)
        notification.target_y = 80 + len(self.notifications) * 90
        notification.current_y = notification.target_y
        self.notifications.append(notification)
        if self.sounds and hasattr(self.sounds, "play_achievement"):
            self.sounds.play_achievement()
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
        print(f"Achievement notification added: {achievement_name}")

    def update(self, dt):

        self.notifications = [notification for notification in self.notifications if notification.update(dt)]

        for i, notification in enumerate(self.notifications):
            target_y = 80 + i * 90
            notification.target_y = target_y
            notification.current_y += (target_y - notification.current_y) * dt * 5

    def draw(self, screen):
        for notification in self.notifications:
            notification.draw(screen)

    def clear_all(self):
        self.notifications.clear()
