from modul.achievements import AchievementSystem


def test_achievement_unlock():
    system = AchievementSystem()
    system.unlock("First Blood")
    assert system.is_unlocked("First Blood")


def test_achievement_not_unlocked():
    system = AchievementSystem()
    assert not system.is_unlocked("Survivor")
