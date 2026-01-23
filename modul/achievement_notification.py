"""Achievement notification visuals and manager."""

import time
import pygame
import modul.constants as C
try:
    from modul.i18n import gettext
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback when i18n unavailable
    def gettext(key):
        """
        Provide a fallback translation that returns the input key when internationalization is unavailable.
        
        Parameters:
            key (str): The translation key or message identifier.
        
        Returns:
            str: The original `key` unchanged.
        """
        return key


class AchievementNotification:
    """Visual notification for unlocked achievements, including animation and display logic."""

    def __init__(self, achievement_name, achievement_description):
        """
        Create an AchievementNotification and initialize its display state, timing, target position, and fonts.
        
        Args:
            achievement_name (str): The achievement title to show.
            achievement_description (str): Short description of the achievement.
        
        Notes:
            - display_time is set to 4.0 seconds and fade_time to 1.0 second.
            - The notification is positioned near the top-right of the screen; target_x is derived from C.SCREEN_WIDTH.
            - Fonts for title and description are created with sizes 32 and 20 respectively.
        """
        self.name = achievement_name
        self.description = achievement_description
        self.display_time = 4.0
        self.fade_time = 1.0
        self.start_time = time.time()
        self.animation_progress = 0.0
        self.is_fading_out = False
        self.target_x = C.SCREEN_WIDTH - 350
        self.target_y = 80
        self.current_x = C.SCREEN_WIDTH
        self.current_y = self.target_y
        self.title_font = pygame.font.Font(None, 32)
        self.desc_font = pygame.font.Font(None, 20)
        self.sound_played = False

    def update(self, _dt):
        """
        Advance the notification's animation and screen position based on the real clock.
        
        Updates internal animation_progress and current_x for fade-in, steady display, and fade-out phases using the notification's start time, fade_time, and display_time.
        
        Parameters:
            _dt (float): Ignored; present for API compatibility. Real elapsed time is measured via the system clock.
        
        Returns:
            bool: `True` while the notification is still active, `False` after its display time has completed.
        """
        current_time = time.time()
        elapsed = current_time - self.start_time


        if elapsed < self.fade_time:
            self.animation_progress = elapsed / self.fade_time
            self.current_x = C.SCREEN_WIDTH - (C.SCREEN_WIDTH - self.target_x) * self._ease_out(self.animation_progress)

        elif elapsed < self.display_time - self.fade_time:
            self.animation_progress = 1.0
            self.current_x = self.target_x


        elif elapsed < self.display_time:
            if not self.is_fading_out:
                self.is_fading_out = True
            fade_progress = (elapsed - (self.display_time - self.fade_time)) / self.fade_time
            self.animation_progress = 1.0 - fade_progress
            self.current_x = self.target_x + (C.SCREEN_WIDTH - self.target_x) * fade_progress

        else:
            return False
        return True

    def _ease_out(self, t):
        """
        Compute a cubic ease-out interpolation for a progress value.
        
        Parameters:
            t (float): Progress in the range [0, 1].
        
        Returns:
            float: Interpolated progress in the range [0, 1], using a cubic ease-out curve.
        """
        return 1 - (1 - t) ** 3

    def draw(self, screen):
        """
        Render the notification at its current animated position using a vertical gradient background, gold border, and text with alpha-based fade.
        
        Parameters:
            screen (pygame.Surface): Surface to draw the notification onto.
        """
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
    """Manages achievement notifications display and animation."""
    def __init__(self, sounds=None):
        """
        Manage active achievement notifications and optional sound playback.
        
        Parameters:
            sounds (optional): An object providing a `play_achievement(name: str)` method; if supplied, the manager calls this when a new achievement notification is added.
        
        Notes:
            - Initializes an empty notification list and sets the maximum concurrent notifications to 3.
        """
        self.notifications = []
        self.max_notifications = 3
        self.sounds = sounds

    def set_sounds(self, sounds):
        """
        Set the sounds provider used to play achievement audio.
        
        Parameters:
            sounds: An object that provides achievement sound playback (expected to expose a `play_achievement` method).
        """
        self.sounds = sounds

    def add_notification(self, achievement_name, achievement_description):
        """
        Create and enqueue an achievement notification unless a notification with the same name already exists.
        
        Creates an AchievementNotification with the given name and description, sets its vertical target position based on current notifications, appends it to the manager, plays the configured achievement sound if available, and removes the oldest notification when the maximum count is exceeded. Prints a debug message when added.
        
        Parameters:
            achievement_name (str): Display name of the achievement.
            achievement_description (str): Short description of the achievement.
        """
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
        """
        Advance and manage active notifications: update each, drop finished ones, and adjust vertical targets with eased positioning.
        
        For each remaining notification this sets its target y position based on its index and moves current_y toward that target using a simple easing factor.
        
        Parameters:
            dt (float): Elapsed time in seconds since the last update; used to scale the easing interpolation.
        """
        self.notifications = [notification for notification in self.notifications if notification.update(dt)]

        for i, notification in enumerate(self.notifications):
            target_y = 80 + i * 90
            notification.target_y = target_y
            notification.current_y += (target_y - notification.current_y) * dt * 5

    def draw(self, screen):
        """
        Draw all managed achievement notifications onto the given screen surface.
        
        Parameters:
            screen (pygame.Surface): Destination surface to render notifications onto.
        """
        for notification in self.notifications:
            notification.draw(screen)

    def clear_all(self):
        """Clear all active notifications."""
        self.notifications.clear()