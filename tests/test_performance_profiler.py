"""Tests for the Performance Profiler module."""

from collections import deque
from unittest.mock import MagicMock, patch

import pytest
import pygame

from modul.performance_profiler import PerformanceProfiler


@pytest.fixture
def mock_pygame():
    """Mock pygame components for testing."""
    with patch('pygame.font.Font'):
        yield


class TestPerformanceProfiler:
    """Test suite for PerformanceProfiler class."""

    def test_profiler_initialization(self):
        """Test profiler initializes with correct default values."""
        profiler = PerformanceProfiler()

        assert profiler.enabled is False
        assert profiler.max_samples == 120
        assert len(profiler.fps_history) == 0
        assert len(profiler.frame_time_history) == 0
        assert profiler.object_counts['asteroids'] == 0
        assert profiler.object_counts['total'] == 0

    def test_profiler_initialization_custom_samples(self):
        """Test profiler initializes with custom max_samples."""
        profiler = PerformanceProfiler(max_samples=60)

        assert profiler.max_samples == 60
        assert profiler.fps_history.maxlen == 60
        assert profiler.frame_time_history.maxlen == 60

    def test_profiler_toggle(self):
        """Test profiler toggle functionality."""
        profiler = PerformanceProfiler()

        assert profiler.enabled is False

        # Toggle on
        result = profiler.toggle()
        assert result is True
        assert profiler.enabled is True

        # Toggle off
        result = profiler.toggle()
        assert result is False
        assert profiler.enabled is False

    def test_profiler_update_disabled(self):
        """Test profiler update does nothing when disabled."""
        profiler = PerformanceProfiler()
        mock_clock = MagicMock()
        mock_clock.get_fps.return_value = 60.0

        profiler.update(0.016, mock_clock, None)

        # Should not update histories when disabled
        assert len(profiler.fps_history) == 0
        assert len(profiler.frame_time_history) == 0

    def test_profiler_update_enabled(self):
        """Test profiler update collects metrics when enabled."""
        profiler = PerformanceProfiler()
        profiler.enabled = True

        mock_clock = MagicMock()
        mock_clock.get_fps.return_value = 60.0

        profiler.update(0.016, mock_clock, None)

        # Should update histories when enabled
        assert len(profiler.fps_history) == 1
        assert profiler.fps_history[0] == 60.0
        assert len(profiler.frame_time_history) == 1
        assert abs(profiler.frame_time_history[0] - 16.0) < 0.1  # ~16ms for 60 FPS

    def test_profiler_update_object_counts(self):
        """Test profiler correctly counts game objects."""
        profiler = PerformanceProfiler()
        profiler.enabled = True

        mock_clock = MagicMock()
        mock_clock.get_fps.return_value = 60.0

        # Mock object groups
        object_groups = {
            'asteroids': [1, 2, 3, 4, 5],  # 5 asteroids
            'shots': [1, 2],  # 2 shots
            'particles': [1, 2, 3],  # 3 particles
            'powerups': [1],  # 1 powerup
            'enemies': []  # 0 enemies
        }

        profiler.update(0.016, mock_clock, object_groups)

        assert profiler.object_counts['asteroids'] == 5
        assert profiler.object_counts['shots'] == 2
        assert profiler.object_counts['particles'] == 3
        assert profiler.object_counts['powerups'] == 1
        assert profiler.object_counts['enemies'] == 0
        assert profiler.object_counts['total'] == 11

    def test_profiler_history_maxlen(self):
        """Test profiler history respects max_samples limit."""
        profiler = PerformanceProfiler(max_samples=5)
        profiler.enabled = True

        mock_clock = MagicMock()
        mock_clock.get_fps.return_value = 60.0

        # Add more samples than max_samples
        for i in range(10):
            profiler.update(0.016, mock_clock, None)

        # Should only keep the last 5 samples
        assert len(profiler.fps_history) == 5
        assert len(profiler.frame_time_history) == 5

    def test_profiler_get_summary(self):
        """Test profiler summary calculation."""
        profiler = PerformanceProfiler()
        profiler.enabled = True

        mock_clock = MagicMock()

        # Add some test data
        fps_values = [60.0, 58.0, 59.0, 57.0, 60.0]
        for fps in fps_values:
            mock_clock.get_fps.return_value = fps
            profiler.update(0.016, mock_clock, None)

        summary = profiler.get_summary()

        assert summary is not None
        assert 'avg_fps' in summary
        assert 'min_fps' in summary
        assert 'max_fps' in summary
        assert 'avg_frame_time_ms' in summary

        # Check calculations
        assert summary['avg_fps'] == sum(fps_values) / len(fps_values)
        assert summary['min_fps'] == min(fps_values)
        assert summary['max_fps'] == max(fps_values)

    def test_profiler_get_summary_empty(self):
        """Test profiler summary returns None when no data."""
        profiler = PerformanceProfiler()

        summary = profiler.get_summary()

        assert summary is None

    def test_profiler_draw_disabled(self, mock_pygame):
        """Test profiler draw does nothing when disabled."""
        profiler = PerformanceProfiler()
        mock_screen = MagicMock()

        # Should not raise any errors or draw anything when disabled
        profiler.draw(mock_screen)

        # Verify no drawing operations were called
        assert mock_screen.blit.call_count == 0

    def test_profiler_draw_enabled(self, mock_pygame):
        """Test profiler draw renders when enabled."""
        profiler = PerformanceProfiler()
        profiler.enabled = True

        # Add some sample data
        mock_clock = MagicMock()
        mock_clock.get_fps.return_value = 60.0
        profiler.update(0.016, mock_clock, None)

        mock_screen = MagicMock()
        mock_screen.get_width.return_value = 1280
        mock_screen.get_height.return_value = 720

        # Should draw without errors
        profiler.draw(mock_screen)

        # Verify some drawing operations were called
        assert mock_screen.blit.call_count > 0
