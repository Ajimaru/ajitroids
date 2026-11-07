"""Tests for the survival and time attack progression rules."""

import pygame
import pytest

from modul.constants import (SURVIVAL_WAVE_BASE_COUNT,
                             SURVIVAL_WAVE_BASE_INTERVAL,
                             SURVIVAL_WAVE_BASE_TARGET,
                             SURVIVAL_WAVE_MAX_COUNT, SURVIVAL_WAVE_MAX_TARGET,
                             SURVIVAL_WAVE_MIN_INTERVAL,
                             SURVIVAL_WAVE_SCORE_BONUS,
                             TIME_ATTACK_BASE_TARGET, TIME_ATTACK_BONUS_TIME,
                             TIME_ATTACK_MAX_TARGET, TIME_ATTACK_ROUND_TIME,
                             TIME_ATTACK_SCORE_BONUS, TIME_ATTACK_TARGET_STEP)
from modul.game_modes import SurvivalProgression, TimeAttackProgression
from modul.menu import GameModeMenu


class TestSurvivalProgression:
    """Wave pacing for survival mode."""

    def test_starts_at_first_wave(self):
        """A new run begins at wave 1 with no kills."""
        survival = SurvivalProgression()
        assert survival.wave == 1  # nosec B101
        assert survival.kills == 0  # nosec B101
        assert survival.target == SURVIVAL_WAVE_BASE_TARGET  # nosec B101
        assert survival.remaining == SURVIVAL_WAVE_BASE_TARGET  # nosec B101

    def test_waves_grow_and_speed_up(self):
        """Later waves demand more kills, allow more asteroids and spawn faster."""
        survival = SurvivalProgression()
        first = (survival.target, survival.asteroid_count, survival.spawn_interval)

        survival.next_wave()
        survival.next_wave()

        assert survival.target > first[0]  # nosec B101
        assert survival.asteroid_count > first[1]  # nosec B101
        assert survival.spawn_interval < first[2]  # nosec B101

    def test_values_are_capped(self):
        """Wave scaling stops at the configured limits."""
        survival = SurvivalProgression()
        survival.wave = 500

        assert survival.target == SURVIVAL_WAVE_MAX_TARGET  # nosec B101
        assert survival.asteroid_count == SURVIVAL_WAVE_MAX_COUNT  # nosec B101
        assert survival.spawn_interval == SURVIVAL_WAVE_MIN_INTERVAL  # nosec B101
        assert SURVIVAL_WAVE_BASE_COUNT < SURVIVAL_WAVE_MAX_COUNT  # nosec B101
        assert SURVIVAL_WAVE_BASE_INTERVAL > SURVIVAL_WAVE_MIN_INTERVAL  # nosec B101

    def test_register_kill_only_clears_at_target(self):
        """The wave is reported cleared exactly when the quota is reached."""
        survival = SurvivalProgression()

        for _ in range(survival.target - 1):
            assert survival.register_kill() is False  # nosec B101

        assert survival.remaining == 1  # nosec B101
        assert survival.register_kill() is True  # nosec B101

    def test_next_wave_resets_kills(self):
        """Advancing keeps the wave counter and clears the kill count."""
        survival = SurvivalProgression()
        survival.register_kill()
        survival.register_kill()

        survival.next_wave()

        assert survival.wave == 2  # nosec B101
        assert survival.kills == 0  # nosec B101

    def test_bonus_scales_with_wave(self):
        """Clearing deeper waves pays more."""
        survival = SurvivalProgression()
        assert survival.bonus == SURVIVAL_WAVE_SCORE_BONUS  # nosec B101

        survival.next_wave()
        assert survival.bonus == 2 * SURVIVAL_WAVE_SCORE_BONUS  # nosec B101

    def test_reset_returns_to_first_wave(self):
        """A restart wipes wave progress."""
        survival = SurvivalProgression()
        survival.next_wave()
        survival.register_kill()

        survival.reset()

        assert survival.wave == 1  # nosec B101
        assert survival.kills == 0  # nosec B101

    def test_difficulty_scales_quota_and_pacing(self):
        """Hard raises the kill quota and shortens the spawn interval."""
        easy = SurvivalProgression("easy")
        hard = SurvivalProgression("hard")

        assert easy.target < hard.target  # nosec B101
        assert easy.spawn_interval > hard.spawn_interval  # nosec B101

    def test_unknown_difficulty_falls_back_to_normal(self):
        """An unknown difficulty must not raise or divide by zero."""
        survival = SurvivalProgression("nightmare")

        assert survival.difficulty == "normal"  # nosec B101
        assert survival.target == SURVIVAL_WAVE_BASE_TARGET  # nosec B101

    def test_set_difficulty_applies_to_following_waves(self):
        """The menu can switch difficulty before a run starts."""
        survival = SurvivalProgression()
        normal_interval = survival.spawn_interval
        normal_target = survival.target

        survival.set_difficulty("hard")

        assert survival.spawn_interval < normal_interval  # nosec B101
        assert survival.target > normal_target  # nosec B101


class TestTimeAttackProgression:
    """Round quota and countdown for time attack."""

    def test_starts_with_full_clock(self):
        """A new run begins at round 1 with the full round time."""
        attack = TimeAttackProgression()
        assert attack.round == 1  # nosec B101
        assert attack.kills == 0  # nosec B101
        assert attack.remaining == TIME_ATTACK_ROUND_TIME  # nosec B101
        assert attack.target == TIME_ATTACK_BASE_TARGET  # nosec B101

    def test_clock_runs_out_once(self):
        """update() reports the expiry and keeps the clock at zero."""
        attack = TimeAttackProgression()

        assert attack.update(TIME_ATTACK_ROUND_TIME - 0.1) is False  # nosec B101
        assert attack.update(0.2) is True  # nosec B101
        assert attack.remaining == 0.0  # nosec B101
        assert attack.update(1.0) is True  # nosec B101

    def test_target_grows_and_caps(self):
        """Each round raises the quota up to the configured maximum."""
        attack = TimeAttackProgression()
        first = attack.target

        attack.next_round()
        assert attack.target == first + TIME_ATTACK_TARGET_STEP  # nosec B101

        attack.round = 999
        assert attack.target == TIME_ATTACK_MAX_TARGET  # nosec B101

    def test_next_round_adds_bonus_time(self):
        """Cleared rounds keep the leftover time and add the bonus."""
        attack = TimeAttackProgression()
        attack.remaining = 20.0

        attack.next_round()

        assert attack.remaining == pytest.approx(20.0 + TIME_ATTACK_BONUS_TIME)  # nosec B101
        assert attack.round == 2  # nosec B101
        assert attack.kills == 0  # nosec B101

    def test_bonus_time_is_capped(self):
        """A round can never start with more than one full clock plus bonus."""
        attack = TimeAttackProgression()
        attack.remaining = TIME_ATTACK_ROUND_TIME

        attack.next_round()

        assert attack.remaining == pytest.approx(TIME_ATTACK_ROUND_TIME + TIME_ATTACK_BONUS_TIME)  # nosec B101

    def test_register_kill_only_clears_at_target(self):
        """The round is reported cleared exactly when the quota is reached."""
        attack = TimeAttackProgression()

        for _ in range(attack.target - 1):
            assert attack.register_kill() is False  # nosec B101

        assert attack.register_kill() is True  # nosec B101

    def test_bonus_scales_with_round(self):
        """Later rounds pay more score."""
        attack = TimeAttackProgression()
        assert attack.bonus == TIME_ATTACK_SCORE_BONUS  # nosec B101

        attack.next_round()
        assert attack.bonus == 2 * TIME_ATTACK_SCORE_BONUS  # nosec B101

    def test_ratio_is_clamped(self):
        """The HUD ratio stays between 0 and 1."""
        attack = TimeAttackProgression()
        full = TIME_ATTACK_ROUND_TIME + TIME_ATTACK_BONUS_TIME
        assert attack.ratio == pytest.approx(TIME_ATTACK_ROUND_TIME / full)  # nosec B101

        attack.remaining = 0.0
        assert attack.ratio == 0.0  # nosec B101

        attack.remaining = 999.0
        assert attack.ratio == 1.0  # nosec B101

    def test_reset_clears_progress(self):
        """A restart wipes rounds, kills and the clock."""
        attack = TimeAttackProgression()
        attack.next_round()
        attack.register_kill()
        attack.remaining = 3.0

        attack.reset()

        assert attack.round == 1  # nosec B101
        assert attack.kills == 0  # nosec B101
        assert attack.remaining == TIME_ATTACK_ROUND_TIME  # nosec B101

    def test_difficulty_scales_the_quota(self):
        """Hard raises the quota so the denser field does not make it easier."""
        easy = TimeAttackProgression("easy")
        hard = TimeAttackProgression("hard")

        assert easy.target < hard.target  # nosec B101
        assert easy.target < TIME_ATTACK_BASE_TARGET  # nosec B101
        assert hard.target > TIME_ATTACK_BASE_TARGET  # nosec B101

    def test_unknown_difficulty_falls_back_to_normal(self):
        """An unknown difficulty falls back without touching the quota."""
        attack = TimeAttackProgression("nightmare")

        assert attack.difficulty == "normal"  # nosec B101
        assert attack.target == TIME_ATTACK_BASE_TARGET  # nosec B101

    def test_set_difficulty_applies_to_following_rounds(self):
        """The menu can switch difficulty before a run starts."""
        attack = TimeAttackProgression()
        normal_target = attack.target

        attack.set_difficulty("hard")

        assert attack.target > normal_target  # nosec B101


class TestGameModeMenu:  # pylint: disable=too-few-public-methods
    """The mode menu offers exactly the three shipped modes."""

    def test_menu_items(self):
        """Menu entries map to the mode actions consumed by main()."""
        pygame.init()
        try:
            menu = GameModeMenu()
            assert [item.action for item in menu.items] == [  # nosec B101
                "mode_classic",
                "mode_survival",
                "mode_time_attack",
                "main_menu",
            ]
        finally:
            pygame.quit()


@pytest.mark.parametrize("mode", ["classic", "survival", "time_attack"])
def test_mode_menu_confirms_initial_mode(mode):
    """Each mode action is reachable through the menu."""
    pygame.font.init()
    menu = GameModeMenu(mode)
    menu.activate()
    menu.input_cooldown = 0
    action = menu.update(1, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
    assert action == "mode_" + mode  # nosec B101
