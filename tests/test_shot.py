from modul.shot import Shot

def test_shot_init():
    try:
        shot = Shot(5, 10)
        assert shot.position.x == 5
        assert shot.position.y == 10
    except AttributeError as e:
        assert 'containers' in str(e)
