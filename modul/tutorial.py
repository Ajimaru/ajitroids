import pygame
import math
from modul.constants import *
from modul.starfield import MenuStarfield

class Tutorial:
    def __init__(self):
        self.pages = [
            {
                "title": "Basics",
                "content": [
                    "Move your spaceship with the arrow keys",
                    "Shoot with the spacebar",
                    "Rotate with left/right arrow keys", 
                    "Move forward/backward with up/down arrow keys",
                    "Destroy asteroids for points!",
                    "",
                    "Large asteroids break into smaller pieces",
                    "Collect power-ups for special abilities"
                ]
            },
            {
                "title": "Power-Ups",
                "content": [
                    "[SHIELD] - Immune for 3 sec.",
                    "[3-SHOT] - Three shots simultaneously",
                    "[SPEED] - Increased fire rate",
                    "[LASER] - Increased damage",
                    "[ROCKET] - Tracks nearby asteroids",
                    "[SHOTGUN] - Multiple shots in a spread",
                    "",
                    "Power-ups only appear from large asteroids!",
                    "They disappear after 10 seconds"
                ]
            },
            {
                "title": "Level System",
                "content": [
                    "Collect 2500 points for a level-up",
                    "Higher levels = more and faster asteroids",
                    "Maximum level: 999",
                    "",
                    "*** Boss Fights ***",
                    "A boss appears every 10 levels!",
                    "Bosses have high health and attack patterns",
                    "Reward: +1 life and 500 points",
                    "",
                    "Bosses get stronger with each level!"
                ]
            },
            {
                "title": "Weapon System",
                "content": [
                    "STANDARD: Unlimited ammo",
                    "LASER: 15 shots, penetrates asteroids",
                    "ROCKETS: 8 shots, automatically track targets",
                    "SHOTGUN: 12 shots, spread fire",
                    "",
                    "Collect the same weapon for more ammo",
                    "Weapons automatically switch back to the standard weapon"
                ]
            },
            {
                "title": "Boss Fight Strategies",
                "content": [
                    "*** Boss Behavior ***",
                    "• Moves in different phases",
                    "• Switches between attack patterns",
                    "• Becomes more dangerous at higher levels",
                    "",
                    "*** Tips ***",
                    "• Use movement to dodge projectiles",
                    "• Collect power-ups before the boss fight",
                    "• Focus on the boss core",
                    "• The health bar shows progress"
                ]
            },
            {
                "title": "Advanced Tips",
                "content": [
                    "*** Controls ***",
                    "• ESC for pause",
                    "• F11 for fullscreen",
                    "• Arrow keys for movement",
                    "• Spacebar to shoot",
                    "",
                    "*** Strategy ***",
                    "• Large asteroids give more points",
                    "• Power-ups pulse in the last 3 seconds",
                    "• Use invulnerability after respawn",
                    "• Boss fights are optional - but rewarding!"
                ]
            },
            {
                "title": "Difficulty Levels",
                "content": [
                    "[EASY]:",
                    "• Slower asteroids",
                    "• Fewer asteroids per level",
                    "• More power-up chances",
                    "",
                    "[NORMAL]:",
                    "• Balanced gameplay",
                    "• Standard settings",
                    "",
                    "[HARD]:",
                    "• Faster asteroids",
                    "• More asteroids per level",
                    "• Fewer power-up chances",
                    "• Tougher boss fights"
                ]
            }
        ]
        
        self.current_page = 0
        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 0.3
        
        self.font_title = pygame.font.Font(None, 48)
        self.font_content = pygame.font.Font(None, 28)
        self.font_navigation = pygame.font.Font(None, 24)
        
        try:
            from starfield import MenuStarfield
            self.starfield = MenuStarfield(num_stars=80)
        except ImportError:
            self.starfield = None
            print("Could not import starfield")

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.start_transition(self.current_page + 1)
    
    def previous_page(self):
        if self.current_page > 0:
            self.start_transition(self.current_page - 1)
    
    def start_transition(self, target_page):
        self.transitioning = True
        self.target_page = target_page
        self.transition_timer = 0
    
    def update(self, dt, events):
        if hasattr(self, 'starfield') and self.starfield:
            self.starfield.update(dt)
        
        if self.transitioning:
            self.transition_timer += dt
            if self.transition_timer >= self.transition_duration:
                self.transitioning = False
                self.current_page = self.target_page
                self.transition_timer = 0
                return None
    
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    return "back"
                
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if not self.transitioning:
                        self.previous_page()
                
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if not self.transitioning:
                        self.next_page()
        
        return None
    
    def draw(self, screen):
        screen.fill((0, 0, 0))
        
        if hasattr(self, 'starfield') and self.starfield:
            self.starfield.draw(screen)
        
        alpha = 255
        if self.transitioning:
            progress = self.transition_timer / self.transition_duration
            alpha = int(255 * (1 - abs(progress - 0.5) * 2))
        
        page = self.pages[self.current_page]
        y_offset = 80
        
        title_color = (100, 200, 255) if alpha == 255 else (100, 200, 255, alpha)
        title_surface = self.font_title.render(page["title"], True, title_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH/2, y_offset))
        
        if alpha < 255:
            title_surface.set_alpha(alpha)
        screen.blit(title_surface, title_rect)
        
        y_offset += 80
        
        for line in page["content"]:
            if line == "":
                y_offset += 15
                continue
            
            if ((line.startswith("[") and "]" in line) or 
                (":" in line and any(weapon in line for weapon in ["STANDARD", "LASER", "ROCKET", "SHOTGUN"]))):
                self.draw_colored_line(screen, line, SCREEN_WIDTH//2, y_offset)
            else:
                color = (255, 255, 255)
                
                if line.startswith("*** Boss Fights ***") or line.startswith("*** Boss Behavior ***"):
                    color = (128, 0, 128)
                elif line.startswith("*** Tips ***"):
                    color = (255, 215, 0)
                elif line.startswith("*** Controls ***") or line.startswith("*** Strategy ***"):
                    color = (100, 200, 255)
                
                elif line.startswith("•"):
                    color = (200, 200, 200)
                
                content_surface = self.font_content.render(line, True, color)
                if alpha < 255:
                    content_surface.set_alpha(alpha)
                    
                content_rect = content_surface.get_rect(center=(SCREEN_WIDTH/2, y_offset))
                screen.blit(content_surface, content_rect)
            
            y_offset += 35
        
        nav_y = SCREEN_HEIGHT - 80
        
        page_info = f"Page {self.current_page + 1} of {len(self.pages)}"
        page_surface = self.font_navigation.render(page_info, True, (150, 150, 150))
        page_rect = page_surface.get_rect(center=(SCREEN_WIDTH/2, nav_y))
        screen.blit(page_surface, page_rect)

        nav_text = "LEFT / RIGHT to navigate or SPACE to go Back"
        nav_surface = self.font_navigation.render(nav_text, True, (100, 100, 100))
        nav_rect = nav_surface.get_rect(center=(SCREEN_WIDTH/2, nav_y + 30))
        screen.blit(nav_surface, nav_rect)
        
        progress_width = 300
        progress_height = 4
        progress_x = (SCREEN_WIDTH - progress_width) // 2
        progress_y = nav_y - 30
        
        pygame.draw.rect(screen, (50, 50, 50), 
                        (progress_x, progress_y, progress_width, progress_height))
        
        current_progress = (self.current_page + 1) / len(self.pages)
        progress_fill_width = int(progress_width * current_progress)
        pygame.draw.rect(screen, (100, 200, 255), 
                        (progress_x, progress_y, progress_fill_width, progress_height))
    
    def draw_colored_line(self, screen, line, x, y):
        
        if line.startswith("[") and "]" in line:
            bracket_end = line.find("]") + 1
            name_part = line[:bracket_end]
            desc_part = line[bracket_end:]
            
            name_color = (255, 255, 255)
            if "[SHIELD]" in name_part:
                name_color = (0, 255, 255)
            elif "[LASER]" in name_part:
                name_color = (0, 255, 0)
            elif "[ROCKET]" in name_part:
                name_color = (255, 0, 0)
            elif "[SHOTGUN]" in name_part:
                name_color = (255, 170, 0)
            elif "[3-SHOT]" in name_part:
                name_color = (255, 0, 255)
            elif "[SPEED]" in name_part:
                name_color = (255, 255, 0)
            elif "[LEASY]" in name_part:
                name_color = (0, 255, 0)
            elif "[NORMAL]" in name_part:
                name_color = (255, 255, 0)
            elif "[HARD]" in name_part:
                name_color = (255, 0, 0)

            name_surface = self.font_content.render(name_part, True, name_color)
            name_width = name_surface.get_width()
 
            desc_surface = self.font_content.render(desc_part, True, (255, 255, 255))

            total_width = name_width + desc_surface.get_width()
            start_x = x - total_width // 2
            
            screen.blit(name_surface, (start_x, y))
            screen.blit(desc_surface, (start_x + name_width, y))

        elif ":" in line:
            colon_pos = line.find(":") + 1
            name_part = line[:colon_pos]
            desc_part = line[colon_pos:]

            name_color = (255, 255, 255)
            if "STANDARD:" in name_part:
                name_color = (255, 255, 255)
            elif "LASER:" in name_part:
                name_color = (0, 255, 0)
            elif "ROCKETS:" in name_part:
                name_color = (255, 0, 0)
            elif "SHOTGUN:" in name_part:
                name_color = (255, 165, 0)

            name_surface = self.font_content.render(name_part, True, name_color)
            name_width = name_surface.get_width()

            desc_surface = self.font_content.render(desc_part, True, (255, 255, 255))

            total_width = name_width + desc_surface.get_width()
            start_x = x - total_width // 2
            
            screen.blit(name_surface, (start_x, y))
            screen.blit(desc_surface, (start_x + name_width, y))
            
        else:

            content_surface = self.font_content.render(line, True, (255, 255, 255))
            content_rect = content_surface.get_rect(center=(x, y))
            screen.blit(content_surface, content_rect)