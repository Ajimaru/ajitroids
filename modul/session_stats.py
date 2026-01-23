"""Game session statistics tracking."""
import time


class SessionStats:
    """Track statistics for the current game session."""

    def __init__(self):
        """Initialize session statistics with default values."""
        # Define all attributes here to satisfy pylint (W0201)
        self.game_start_time = 0
        self.total_score = 0
        self.highest_score = 0
        self.games_played = 0
        self.total_asteroids_destroyed = 0
        self.total_enemies_destroyed = 0
        self.total_bosses_defeated = 0
        self.total_powerups_collected = 0
        self.total_shots_fired = 0
        self.highest_level = 0
        self.total_lives_lost = 0
        self.total_playtime = 0.0
        self.session_start_time = time.time()
        self.reset()

    def reset(self):
        """Reset statistics for a new game."""
        self.game_start_time = time.time()
        self.total_score = 0
        self.highest_score = 0
        self.games_played = 0
        self.total_asteroids_destroyed = 0
        self.total_enemies_destroyed = 0
        self.total_bosses_defeated = 0
        self.total_powerups_collected = 0
        self.total_shots_fired = 0
        self.highest_level = 0
        self.total_lives_lost = 0
        self.total_playtime = 0.0
    
    def start_game(self):
        """Mark the start of a new game."""
        self.game_start_time = time.time()
        self.games_played += 1

    def end_game(self, final_score, final_level):
        """Record stats at game end."""
        self.total_score += final_score
        self.highest_score = max(self.highest_score, final_score)
        self.highest_level = max(self.highest_level, final_level)
        game_duration = time.time() - self.game_start_time
        self.total_playtime += game_duration

    def record_asteroid_destroyed(self):
        """Increment asteroid destruction counter."""
        self.total_asteroids_destroyed += 1

    def record_enemy_destroyed(self):
        """Increment enemy destruction counter."""
        self.total_enemies_destroyed += 1

    def record_boss_defeated(self):
        """Increment boss defeat counter."""
        self.total_bosses_defeated += 1

    def record_powerup_collected(self):
        """Increment powerup collection counter."""
        self.total_powerups_collected += 1

    def record_shot_fired(self):
        """Increment shot fired counter."""
        self.total_shots_fired += 1

    def record_life_lost(self):
        """Increment lives lost counter."""
        self.total_lives_lost += 1

    def get_session_duration(self):
        """Get total session duration in seconds."""
        return time.time() - self.session_start_time

    def get_average_score(self):
        """Calculate average score per game."""
        return self.total_score / max(1, self.games_played)

    def get_accuracy(self):
        """Calculate shot accuracy (targets destroyed / shots fired)."""
        if self.total_shots_fired == 0:
            return 0.0
        total_hits = self.total_asteroids_destroyed + self.total_enemies_destroyed
        return (total_hits / self.total_shots_fired) * 100

    def get_summary(self):
        """Get a dictionary of all statistics."""
        return {
            'games_played': self.games_played,
            'total_score': self.total_score,
            'highest_score': self.highest_score,
            'highest_level': self.highest_level,
            'average_score': self.get_average_score(),
            'total_asteroids_destroyed': self.total_asteroids_destroyed,
            'total_enemies_destroyed': self.total_enemies_destroyed,
            'total_bosses_defeated': self.total_bosses_defeated,
            'total_powerups_collected': self.total_powerups_collected,
            'total_lives_lost': self.total_lives_lost,
            'total_playtime': self.total_playtime,
            'session_duration': self.get_session_duration(),
        }

    def format_time(self, seconds):
        """Format seconds into HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_formatted_summary(self):
        """Get a formatted string representation of stats."""
        stats = self.get_summary()
        return f"""
SESSION STATISTICS
==================
Games Played:         {stats['games_played']}
Highest Score:        {stats['highest_score']:,}
Average Score:        {stats['average_score']:.0f}
Highest Level:        {stats['highest_level']}

COMBAT STATS
============
Asteroids Destroyed:  {stats['total_asteroids_destroyed']:,}
Enemies Destroyed:    {stats['total_enemies_destroyed']:,}
Bosses Defeated:      {stats['total_bosses_defeated']:,}

COLLECTION & SURVIVAL
=====================
Power-ups Collected:  {stats['total_powerups_collected']:,}
Lives Lost:           {stats['total_lives_lost']:,}

TIME
====
Total Playtime:       {self.format_time(stats['total_playtime'])}
Session Duration:     {self.format_time(stats['session_duration'])}
        """.strip()
