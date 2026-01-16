"""Performance Profiler Module for in-game performance monitoring.

This module provides real-time performance metrics display including:
- FPS (Frames Per Second)
- Frame time (milliseconds)
- Object counts (asteroids, shots, particles, etc.)
- Performance graph visualization
"""

import pygame
from collections import deque


class PerformanceProfiler:
    """In-game performance monitoring and visualization."""
    
    def __init__(self, max_samples=120):
        """Initialize the performance profiler.
        
        Args:
            max_samples: Number of samples to keep for graphing (default: 120 = 2 seconds at 60 FPS)
        """
        self.enabled = False
        self.max_samples = max_samples
        
        # Performance metrics
        self.fps_history = deque(maxlen=max_samples)
        self.frame_time_history = deque(maxlen=max_samples)
        
        # Object counts
        self.object_counts = {
            'asteroids': 0,
            'shots': 0,
            'particles': 0,
            'powerups': 0,
            'enemies': 0,
            'total': 0
        }
        
        # Graph settings
        self.graph_width = 240
        self.graph_height = 80
        self.graph_padding = 5
        
        # Colors
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (0, 255, 0)    # Green
        self.fps_color = (0, 255, 255)   # Cyan
        self.frame_time_color = (255, 255, 0)  # Yellow
        self.good_color = (0, 255, 0)    # Green (good performance)
        self.warning_color = (255, 255, 0)  # Yellow (moderate)
        self.critical_color = (255, 0, 0)   # Red (poor performance)
        
        # Font
        self.font = None
        self.font_small = None
        
    def toggle(self):
        """Toggle profiler visibility."""
        self.enabled = not self.enabled
        return self.enabled
    
    def update(self, dt, clock, object_groups=None):
        """Update performance metrics.
        
        Args:
            dt: Delta time in seconds
            clock: pygame.time.Clock instance
            object_groups: Dictionary of sprite groups to count objects
        """
        if not self.enabled:
            return
        
        # Update FPS
        current_fps = clock.get_fps()
        self.fps_history.append(current_fps)
        
        # Update frame time (in milliseconds)
        frame_time_ms = dt * 1000.0
        self.frame_time_history.append(frame_time_ms)
        
        # Update object counts
        if object_groups:
            self.object_counts['asteroids'] = len(object_groups.get('asteroids', []))
            self.object_counts['shots'] = len(object_groups.get('shots', []))
            self.object_counts['particles'] = len(object_groups.get('particles', []))
            self.object_counts['powerups'] = len(object_groups.get('powerups', []))
            self.object_counts['enemies'] = len(object_groups.get('enemies', []))
            self.object_counts['total'] = sum([
                self.object_counts['asteroids'],
                self.object_counts['shots'],
                self.object_counts['particles'],
                self.object_counts['powerups'],
                self.object_counts['enemies']
            ])
    
    def draw(self, screen):
        """Draw performance metrics overlay.
        
        Args:
            screen: pygame Surface to draw on
        """
        if not self.enabled:
            return
        
        # Initialize fonts if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        
        # Calculate metrics
        avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
        current_fps = self.fps_history[-1] if self.fps_history else 0
        avg_frame_time = sum(self.frame_time_history) / len(self.frame_time_history) if self.frame_time_history else 0
        current_frame_time = self.frame_time_history[-1] if self.frame_time_history else 0
        
        # Determine performance color based on FPS
        if current_fps >= 55:
            fps_color = self.good_color
        elif current_fps >= 30:
            fps_color = self.warning_color
        else:
            fps_color = self.critical_color
        
        # Draw semi-transparent background
        overlay_width = 260
        overlay_height = 320
        overlay_x = screen.get_width() - overlay_width - 10
        overlay_y = 10
        
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay_surface.fill(self.bg_color)
        screen.blit(overlay_surface, (overlay_x, overlay_y))
        
        # Draw metrics text
        y_offset = overlay_y + 10
        x_offset = overlay_x + 10
        
        # Title
        title = self.font.render("Performance Profiler", True, self.text_color)
        screen.blit(title, (x_offset, y_offset))
        y_offset += 30
        
        # FPS metrics
        fps_text = self.font_small.render(f"FPS: {current_fps:.1f} (avg: {avg_fps:.1f})", True, fps_color)
        screen.blit(fps_text, (x_offset, y_offset))
        y_offset += 20
        
        # Frame time metrics
        frame_time_text = self.font_small.render(f"Frame: {current_frame_time:.2f}ms (avg: {avg_frame_time:.2f}ms)", True, self.frame_time_color)
        screen.blit(frame_time_text, (x_offset, y_offset))
        y_offset += 25
        
        # Draw FPS graph
        self._draw_graph(screen, x_offset, y_offset, self.fps_history, 60, "FPS", self.fps_color)
        y_offset += self.graph_height + 15
        
        # Object counts
        y_offset += 5
        counts_title = self.font_small.render("Object Counts:", True, self.text_color)
        screen.blit(counts_title, (x_offset, y_offset))
        y_offset += 20
        
        for obj_type, count in self.object_counts.items():
            if obj_type != 'total':
                count_text = self.font_small.render(f"  {obj_type.capitalize()}: {count}", True, (200, 200, 200))
                screen.blit(count_text, (x_offset, y_offset))
                y_offset += 18
        
        # Total
        total_text = self.font_small.render(f"Total Objects: {self.object_counts['total']}", True, self.text_color)
        screen.blit(total_text, (x_offset, y_offset))
        
        # Draw hint at bottom
        hint_y = overlay_y + overlay_height - 20
        hint = self.font_small.render("Press F12 to toggle", True, (150, 150, 150))
        screen.blit(hint, (x_offset, hint_y))
    
    def _draw_graph(self, screen, x, y, data, max_value, label, color):
        """Draw a performance graph.
        
        Args:
            screen: pygame Surface to draw on
            x, y: Position to draw the graph
            data: deque of data points
            max_value: Maximum value for scaling
            label: Label for the graph
            color: Color for the graph line
        """
        if not data or len(data) < 2:
            return
        
        # Draw graph background
        graph_rect = pygame.Rect(x, y, self.graph_width, self.graph_height)
        pygame.draw.rect(screen, (20, 20, 20), graph_rect)
        pygame.draw.rect(screen, (50, 50, 50), graph_rect, 1)
        
        # Draw label
        label_surface = self.font_small.render(label, True, color)
        screen.blit(label_surface, (x, y - 18))
        
        # Constants for FPS graph reference lines
        TARGET_FPS = 60
        MIN_ACCEPTABLE_FPS = 30
        
        # Draw reference lines for FPS graphs
        if max_value == TARGET_FPS:
            # Draw 60 FPS line
            reference_y = y + self.graph_height - (TARGET_FPS / max_value * self.graph_height)
            pygame.draw.line(screen, (0, 100, 0), (x, reference_y), (x + self.graph_width, reference_y), 1)
            # Draw 30 FPS line
            reference_y_30 = y + self.graph_height - (MIN_ACCEPTABLE_FPS / max_value * self.graph_height)
            pygame.draw.line(screen, (100, 100, 0), (x, reference_y_30), (x + self.graph_width, reference_y_30), 1)
        
        # Draw data points
        data_list = list(data)
        num_points = len(data_list)
        
        x_step = self.graph_width / (num_points - 1) if num_points > 1 else self.graph_width
        
        points = []
        for i, value in enumerate(data_list):
            # Clamp value to max
            clamped_value = min(value, max_value)
            # Calculate position
            px = x + i * x_step
            py = y + self.graph_height - (clamped_value / max_value * self.graph_height)
            points.append((px, py))
        
        # Draw the graph line
        if len(points) >= 2:
            pygame.draw.lines(screen, color, False, points, 2)
        
        # Draw max/min values
        max_val = max(data_list)
        min_val = min(data_list)
        max_text = self.font_small.render(f"{max_val:.1f}", True, (150, 150, 150))
        min_text = self.font_small.render(f"{min_val:.1f}", True, (150, 150, 150))
        screen.blit(max_text, (x + self.graph_width + 5, y))
        screen.blit(min_text, (x + self.graph_width + 5, y + self.graph_height - 15))
    
    def get_summary(self):
        """Get a summary of performance metrics.
        
        Returns:
            Dictionary with performance summary
        """
        if not self.fps_history or not self.frame_time_history:
            return None
        
        return {
            'avg_fps': sum(self.fps_history) / len(self.fps_history),
            'min_fps': min(self.fps_history),
            'max_fps': max(self.fps_history),
            'avg_frame_time_ms': sum(self.frame_time_history) / len(self.frame_time_history),
            'max_frame_time_ms': max(self.frame_time_history),
            'total_objects': self.object_counts['total']
        }
