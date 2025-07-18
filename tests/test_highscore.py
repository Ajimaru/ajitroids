from modul.highscore import HighscoreManager

def test_highscore_add():
    hs = HighscoreManager()
    hs.add_highscore('Player1', 99999)
    assert any(entry['score'] == 99999 for entry in hs.highscores)

def test_highscore_order():
    hs = HighscoreManager()
    hs.add_highscore('A', 10000)
    hs.add_highscore('B', 20000)
    scores = hs.highscores
    assert scores[0]['score'] >= scores[1]['score']
