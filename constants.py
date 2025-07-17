SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE = 0.8  # seconds
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS

ASTEROID_VERTICES = 12  # Anzahl der Eckpunkte
ASTEROID_IRREGULARITY = 0.4  # Maximale Abweichung vom perfekten Kreis (0-1)

PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
PLAYER_ACCELERATION = 300  # Beschleunigung pro Sekunde
PLAYER_MAX_SPEED = 400    # Maximale Geschwindigkeit
PLAYER_FRICTION = 0.02    # Reibung im Weltraum (sehr gering)
PLAYER_ROTATION_SPEED = 180  # Grad pro Sekunde

PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN = 0.3

SHOT_RADIUS = 5

SCORE_LARGE = 20    # Punkte für große Asteroiden
SCORE_MEDIUM = 50   # Punkte für mittlere Asteroiden
SCORE_SMALL = 100   # Punkte für kleine Asteroiden

PLAYER_LIVES = 3
INVINCIBILITY_TIME = 3.0  # Sekunden Unverwundbarkeit nach Respawn
RESPAWN_POSITION_X = SCREEN_WIDTH / 2
RESPAWN_POSITION_Y = SCREEN_HEIGHT / 2

EXPLOSION_PARTICLES = 15  # Anzahl der Partikel pro Explosion
PARTICLE_COLORS = ["white", "yellow", "red"]  # Verschiedene Farben für Partikel

STAR_COUNT = 100
STAR_SIZES = [1, 2, 3]  # Verschiedene Sterngrößen
STAR_COLORS = ["white", "#ADD8E6", "#FFD700"]  # Weiß, Hellblau, Gold

COLLISION_DEBUG = False  # Zum Debuggen der Hitboxen