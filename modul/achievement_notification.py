"""Achievement notification visuals and manager."""

import time
import pygame
import modul.constants as C
try:
    from modul.i18n import gettext
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback when i18n unavailable
    def gettext(key):
        """Fallback translation returning the passed key when i18n is missing."""
        return key


class AchievementNotification:
    """Visual notification for unlocked achievements, including animation and display logic."""

    def __init__(self, achievement_name, achievement_description):
        """
        Create a visual notification for an unlocked achievement and initialize its timing, animation state, fonts, and on-screen positioning.
        
        Parameters:
            achievement_name (str): The achievement's display name.
            achievement_description (str): A short description of the achievement.
        
        Attributes initialized:
            name, description: Stored values from parameters.
            display_time (float): Total time the notification is shown (4.0 seconds).
            fade_time (float): Duration of fade in/out phases (1.0 second).
            start_time (float): Timestamp when the notification was created.
            animation_progress (float): Current progress of the enter/exit animation (0.0–1.0).
            is_fading_out (bool): Whether the notification is currently fading out.
            target_x, target_y (int): Destination coordinates for the notification on screen.
            current_x, current_y (int): Current coordinates used for animated movement.
            title_font, desc_font: Pygame Font objects used for rendering title and description.
            sound_played (bool): Flag indicating if the achievement sound has been played.
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
        Advance the notification's animation state and position and report whether it remains active.
        
        Updates internal timing to progress through three phases — fade-in, fully visible, and fade-out — moving the notification's horizontal position and adjusting its animation progress accordingly. The `_dt` parameter is accepted for API compatibility but is not used; timing is based on the notification's start time.
        
        Parameters:
            _dt: Ignored. Present for API compatibility with external update loops.
        
        Returns:
            `true` if the notification should continue to be displayed, `false` otherwise.
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
        Compute eased progress using a cubic ease-out curve.
        
        Parameters:
            t (float): Progress value between 0 and 1.
        
        Returns:
            float: Eased progress between 0 and 1 where 0 maps to 0 and 1 maps to 1.
        """
        return 1 - (1 - t) ** 3

    def draw(self, screen):
        """Draw the achievement notification on the screen with fade effects."""
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
        Create a manager for on-screen achievement notifications.
        
        Initializes an empty notification list and the maximum simultaneous notifications (3), and stores an optional sounds provider used to play achievement sounds when notifications are added.
        
        Parameters:
            sounds: Optional object providing a `play_achievement()` method to play a sound when a new notification is added.
        """
        self.notifications = []
        self.max_notifications = 3
        self.sounds = sounds

    def set_sounds(self, sounds):
        """
        Assign the sounds provider used to play achievement sounds.
        
        Parameters:
            sounds (object): Provider object that exposes a `play_achievement` method; if provided, that method is called when a new achievement notification is added.
        """
        self.sounds = sounds

    def add_notification(self, achievement_name, achievement_description):
        """
        Add a new achievement notification and arrange it in the display stack.
        
        If a notification with the same name already exists, this method does nothing.
        The new notification is positioned vertically based on the current stack (80px top margin, 90px spacing),
        appended to the manager, and the configured achievement sound is played if available.
        If adding the notification exceeds the manager's capacity, the oldest notification is removed.
        A debug message is printed when a new notification is added.
        
        Parameters:
            achievement_name (str): The unique name/identifier of the achievement.
            achievement_description (str): A short description to display in the notification.
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
        Advance state for all active achievement notifications and update their vertical layout.
        
        Calls each notification's update(dt) and keeps only those that remain active. Recomputes each notification's target y position (starting at 80px with 90px spacing) and smoothly interpolates the notification's current_y toward its target.
        
        Parameters:
            dt (float): Time elapsed since the last update, in seconds.
        """
        self.notifications = [notification for notification in self.notifications if notification.update(dt)]

        for i, notification in enumerate(self.notifications):
            target_y = 80 + i * 90
            notification.target_y = target_y
            notification.current_y += (target_y - notification.current_y) * dt * 5

    def draw(self, screen):
        """Draw all active notifications on the screen."""
        for notification in self.notifications:
            notification.draw(screen)

    def clear_all(self):
        """
        Remove all active and queued achievement notifications immediately.
        """
        self.notifications.clear()