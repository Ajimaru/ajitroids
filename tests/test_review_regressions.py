"""Regression coverage for the full review's gameplay and subsystem defects."""

from types import SimpleNamespace
from unittest.mock import Mock

import pygame
import pytest

import main
import modul.audio_enhancements as audio
import modul.constants as C
from modul.replay_system import GameFrame, ReplayPlayer, ReplayRecorder
from modul.session_stats import SessionStats


@pytest.fixture
def run_game(monkeypatch, tmp_path):
    """Drive the real main loop with deterministic input and headless SDL."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    monkeypatch.setattr(audio, "TTS_AVAILABLE", False)
    monkeypatch.setattr(pygame.time, "delay", lambda _ms: None)
    monkeypatch.setattr(pygame.time, "Clock", lambda: SimpleNamespace(tick=lambda _fps: 16, get_fps=lambda: 60))
    monkeypatch.setattr(main.MainMenu, "update", lambda *_args: "start_game")
    monkeypatch.setattr(main.DifficultyMenu, "update", lambda *_args: "difficulty_normal")
    monkeypatch.setattr(main.ShipSelectionMenu, "update", lambda *_args: "start_game")
    monkeypatch.setattr(main, "collidable", pygame.sprite.Group())
    for entity in (main.Asteroid, main.Shot, main.Particle, main.PowerUp, main.Player, main.Boss, main.BossProjectile):
        monkeypatch.setattr(entity, "containers", (), raising=False)
    monkeypatch.setattr(main.Shot, "asteroids_group", None)
    stats, recorder = SessionStats(), ReplayRecorder()
    monkeypatch.setattr(main, "SessionStats", lambda: stats)
    monkeypatch.setattr(main, "ReplayRecorder", lambda: recorder)
    context = SimpleNamespace(stats=stats, recorder=recorder, observations=[])

    def run(callback, stop_at=7):
        def events():
            step = len(context.observations) + 1
            context.observations.append((main.game_state, main.score, main.lives, main.level))
            if step >= stop_at:
                return [pygame.event.Event(pygame.QUIT)]
            return callback(step, context) or []

        monkeypatch.setattr(pygame.event, "get", events)
        args = SimpleNamespace(debug=False, log_file=None, fullscreen=False, windowed=True, skip_intro=False)
        try:
            main.main(args)
        finally:
            pygame.quit()
        return context

    return run


def key(keycode):
    """Build a real Pygame key event with the attributes menus expect."""
    return pygame.event.Event(pygame.KEYDOWN, key=keycode, unicode="")


def clear_asteroids():
    """Remove random spawns so collision fixtures control their own hazards."""
    for asteroid in list(main.Asteroid.containers[0]):
        asteroid.kill()


@pytest.mark.parametrize("restart_from_game_over", [False, True])
def test_quick_restart_uses_live_state(run_game, restart_from_game_over):
    def drive(step, context):
        if step == 4:
            main.score = 1234
            if restart_from_game_over:
                clear_asteroids()
                main.lives = 1
                main.player.invincible = False
                main.Asteroid(main.player.position.x, main.player.position.y, 20, *main.Asteroid.containers)
            else:
                return [key(pygame.K_r)]
        if step == 5 and restart_from_game_over:
            assert main.game_state == "game_over"
            return [key(pygame.K_r)]
        if step == 6:
            assert (main.game_state, main.score, main.level, main.lives) == ("playing", 0, 1, C.PLAYER_LIVES)
            assert context.recorder.recording
            assert context.stats.games_played == 2
            assert context.stats.total_score == 1234
            assert len(main.Asteroid.containers[0]) == 3

    run_game(drive)


@pytest.mark.parametrize("binding", ["K_ESCAPE", "p", "JOY0_BUTTON1", "JOY0_AXIS1_NEG", "JOY0_HAT0_UP"])
def test_pause_consumes_its_event_and_does_not_reuse_it(run_game, monkeypatch, binding):
    pressed = [False]
    original = main.input_utils.is_action_pressed
    monkeypatch.setattr(
        main.input_utils, "is_action_pressed", lambda action: pressed[0] if action == "pause" else original(action)
    )

    def drive(step, _context):
        if step == 4:
            main.game_settings.controls["pause"] = binding
            if binding.startswith("JOY"):
                pressed[0] = True
            else:
                pause_key = main.input_utils.get_action_keycode("pause")
                return [key(pause_key), pygame.event.Event(pygame.MOUSEMOTION)]
        if step == 6:
            assert main.game_state == "pause"

    run_game(drive)


@pytest.mark.parametrize("new_game", [False, True])
def test_reset_clears_bosses_levels_weapons_and_restarts_sessions(run_game, monkeypatch, new_game):
    monkeypatch.setattr(main.PauseMenu, "update", lambda *_args: "main_menu" if new_game else "restart")

    def drive(step, context):
        if step == 4:
            main.score = 9 * C.POINTS_PER_LEVEL
        if step == 5:
            assert main.boss_active
            main.BossProjectile(10, 10, pygame.Vector2())
            main.player.weapons[C.WEAPON_LASER] = 10
            return [key(pygame.K_ESCAPE)]
        if step == 6:
            return [key(pygame.K_RETURN)]
        if step == (11 if new_game else 7):
            assert (main.score, main.level, main.lives) == (0, 1, C.PLAYER_LIVES)
            assert not main.boss_active
            assert not any(isinstance(obj, (main.Boss, main.BossProjectile)) for obj in main.Boss.containers[0])
            assert main.player.weapons[C.WEAPON_LASER] == 0
            assert context.stats.games_played == 2
            assert context.stats.total_score == 9 * C.POINTS_PER_LEVEL

    run_game(drive, stop_at=12 if new_game else 8)


@pytest.mark.parametrize("hazard", ["asteroid", "enemy", "boss", "projectile"])
def test_terminal_collision_saves_replay_and_counts_one_game(run_game, tmp_path, hazard):
    def drive(step, context):
        if step == 4:
            clear_asteroids()
            main.lives, main.score = 1, 1000
            main.player.invincible = False
            x, y = main.player.position
            if hazard == "asteroid":
                for dx in (-20, 20):
                    main.Asteroid(x + dx, y, 60, *main.Asteroid.containers)
            elif hazard == "enemy":
                enemy = main.EnemyShip(x, y, 30)
                enemy.velocity.update(0, 0)
                main.Boss.containers[0].add(enemy)
                main.Boss.containers[1].add(enemy)
                main.collidable.add(enemy)
            elif hazard == "boss":
                main.Boss(10)
            else:
                main.BossProjectile(x, y, pygame.Vector2())
        if step == 5:
            assert main.game_state == "game_over"
            assert main.lives == 0
            assert context.stats.total_score == 1000
            assert context.stats.total_lives_lost == 1
            assert not context.recorder.recording
            assert len(list((tmp_path / "replays").glob("*"))) == 1

    context = run_game(drive)
    assert context.stats.total_score == 1000


@pytest.mark.parametrize("protection", ["invincible", "shield_active"])
def test_boss_hazards_respect_player_protection(run_game, protection):
    def drive(step, _context):
        if step == 4:
            clear_asteroids()
            setattr(main.player, protection, True)
            main.Boss(10)
            main.BossProjectile(*main.player.position, pygame.Vector2())
        if step == 5:
            assert main.lives == C.PLAYER_LIVES

    run_game(drive)


def test_boss_updates_once_and_targeted_overlap_is_safe(run_game, monkeypatch):
    calls = []
    original = main.Boss.update

    def update(boss, dt, player_position=None):
        calls.append((dt, player_position))
        return original(boss, dt, player_position)

    monkeypatch.setattr(main.Boss, "update", update)

    def drive(step, context):
        if step == 4:
            main.score = 9 * C.POINTS_PER_LEVEL
        if step == 5:
            boss = next(obj for obj in main.Boss.containers[0] if isinstance(obj, main.Boss))
            boss.position = main.player.position.copy()
            boss.attack_timer = boss.attack_interval
            boss.attack_pattern = 2
            context.calls_before = len(calls)
        if step == 6:
            assert len(calls) == context.calls_before + 1
            assert all(position is not None for _dt, position in calls)
            assert any(isinstance(obj, main.BossProjectile) for obj in main.BossProjectile.containers[0])

    run_game(drive)


def test_metal_asteroid_rewards_only_the_fatal_hit(run_game):
    def drive(step, context):
        if step == 4:
            clear_asteroids()
            context.asteroid = main.Asteroid(100, 100, 40, *main.Asteroid.containers, asteroid_type="metal")
            main.Shot(100, 100)
        if step == 5:
            assert context.asteroid.health == 1
            assert main.score == 0
            assert context.stats.total_asteroids_destroyed == 0
            assert not main.achievement_system.is_unlocked("First Blood")
            main.Shot(100, 100)
        if step == 6:
            assert main.score == 30
            assert context.stats.total_asteroids_destroyed == 1
            assert main.achievement_system.is_unlocked("First Blood")

    run_game(drive)


def test_quit_from_pause_finalizes_once(run_game, tmp_path):
    def drive(step, _context):
        if step == 4:
            main.score = 4321
            return [key(pygame.K_ESCAPE)]

    context = run_game(drive)
    assert context.stats.total_score == 4321
    assert not context.recorder.recording
    assert len(list((tmp_path / "replays").glob("*"))) == 1


@pytest.mark.parametrize(
    "weapon,base_damage,count",
    [(C.WEAPON_STANDARD, 1, 1), (C.WEAPON_LASER, 2, 1), (C.WEAPON_MISSILE, 3, 1), (C.WEAPON_SHOTGUN, 1, 5), ("triple", 1, 3)],
)
def test_destroyer_damage_applies_to_every_projectile(monkeypatch, weapon, base_damage, count):
    shots = pygame.sprite.Group()
    monkeypatch.setattr(main.Shot, "containers", (shots,), raising=False)
    monkeypatch.setattr(main.Player, "containers", (), raising=False)
    monkeypatch.setattr("modul.player.Sounds", Mock())
    player = main.Player(100, 100, "destroyer")
    if weapon == "triple":
        player.triple_shot_active = True
    else:
        player.current_weapon = weapon
        player.weapons[weapon] = 10
    player.shoot()
    assert len(shots) == count
    boss = main.Boss(10)
    before = boss.health
    monkeypatch.setattr(main.Particle, "containers", (), raising=False)
    for shot in shots:
        assert shot.damage == base_damage * 2
        boss.take_damage(shot.damage)
    assert boss.health == before - count * base_damage * 2


def test_powerup_drop_cap_and_one_roll_per_destruction(monkeypatch):
    pygame.init()
    try:
        powerups, asteroids = pygame.sprite.Group(), pygame.sprite.Group()
        monkeypatch.setattr(main.PowerUp, "containers", (powerups,), raising=False)
        monkeypatch.setattr(main.Asteroid, "containers", (asteroids,), raising=False)
        monkeypatch.setattr(main.Particle, "containers", (), raising=False)
        monkeypatch.setattr("modul.powerup.random.random", lambda: 0)
        for _ in range(C.POWERUP_MAX_COUNT - 1):
            main.PowerUp(0, 0)
        asteroid = main.Asteroid(0, 0, 40, asteroids)
        assert asteroid.split()
        assert len(powerups) == C.POWERUP_MAX_COUNT
        main.Asteroid(0, 0, 20, asteroids).split()
        assert len(powerups) == C.POWERUP_MAX_COUNT
    finally:
        pygame.quit()


def test_dynamic_music_receives_counts_and_respects_mute(monkeypatch):
    monkeypatch.setattr(audio, "TTS_AVAILABLE", False)
    manager = audio.AudioEnhancementManager()
    manager.dynamic_music.update = Mock()
    state = dict(asteroids_count=10, enemies_count=2, boss_active=True, score=25000, level=10)
    asset_path = Mock()
    manager.update(0.016, state, asset_path)
    manager.dynamic_music.update.assert_called_once_with(0.016, 10, 2, True, 25000, 10, asset_path)
    manager.update(0.016, dict(state, music_on=False), asset_path)
    assert manager.dynamic_music.update.call_count == 1


def test_paused_seek_and_playback_completion(monkeypatch):
    clock = [100.0]
    monkeypatch.setattr("modul.replay_system.time.time", lambda: clock[0])
    player = ReplayPlayer()
    player.frames = [GameFrame(float(i), (0, 0), 0, (0, 0), 0, 3, 1) for i in range(11)]
    player.metadata = {"duration": 10}
    player.start_playback()
    clock[0] = 102
    player.get_current_frame()
    player.toggle_pause()
    player.skip_forward(5)
    assert player.get_current_timestamp() == 7
    player.set_speed(2)
    player.toggle_pause()
    assert player.get_current_timestamp() == 7
    clock[0] += 10
    assert player.get_current_frame() == player.frames[-1]
    assert not player.playing
    assert player.get_current_timestamp() == 10
    assert player.get_current_frame() == player.frames[-1]
    player.skip_backward(5)
    assert player.playing
    assert player.get_current_frame().timestamp == 5
    player.stop_playback()
    assert player.get_current_frame() is None
    player.start_playback()
    assert player.get_current_timestamp() == 0


def test_dashboard_rows_use_distinct_columns(monkeypatch):
    pygame.font.init()
    try:
        dashboard = main.StatsDashboard(SessionStats())
        positions = []
        original = dashboard._draw_stat_line

        def draw_line(screen, label, value, y, x):
            positions.append((x, y))
            return original(screen, label, value, y, x)

        monkeypatch.setattr(dashboard, "_draw_stat_line", draw_line)
        dashboard.draw(pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT)))
        assert len(positions) == 10
        assert {x for x, _y in positions[:5]} == {C.SCREEN_WIDTH / 4}
        assert {x for x, _y in positions[5:]} == {C.SCREEN_WIDTH * 3 / 4}
    finally:
        pygame.font.quit()
