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

# Spieler-Konstanten
PLAYER_LIVES = 3  # Anzahl der Leben zu Spielbeginn
INVINCIBILITY_TIME = 3.0  # Sekunden Unverwundbarkeit nach Respawn
RESPAWN_POSITION_X = SCREEN_WIDTH / 2
RESPAWN_POSITION_Y = SCREEN_HEIGHT / 2

EXPLOSION_PARTICLES = 15  # Anzahl der Partikel pro Explosion
PARTICLE_COLORS = ["white", "yellow", "red"]  # Verschiedene Farben für Partikel

STAR_COUNT = 100
STAR_SIZES = [1, 2, 3]  # Verschiedene Sterngrößen
STAR_COLORS = ["white", "#ADD8E6", "#FFD700"]  # Weiß, Hellblau, Gold

COLLISION_DEBUG = False  # Zum Debuggen der Hitboxen

# Power-up Konstanten
POWERUP_RADIUS = 15
POWERUP_SPAWN_CHANCE = 0.3  # Erhöht von 0.1 auf 0.3 für häufigere Spawns
POWERUP_MAX_COUNT = 3  # Maximal 3 Power-ups gleichzeitig
POWERUP_LIFETIME = 15.0  # Sekunden bis ein Power-up verschwindet
SHIELD_DURATION = 10.0  # Sekunden
POWERUP_TYPES = ["shield", "triple_shot", "rapid_fire", "laser_weapon", "missile_weapon", "shotgun_weapon"]
POWERUP_COLORS = {
    "shield": "#00FFFF",           # Cyan
    "triple_shot": "#FF00FF",      # Magenta
    "rapid_fire": "#FFFF00",       # Gelb
    "laser_weapon": "#00FF00",     # Grün
    "missile_weapon": "#FF0000",   # Rot
    "shotgun_weapon": "#FFAA00"    # Orange
}
RAPID_FIRE_COOLDOWN = 0.1    # Cooldown während Rapid-Fire
RAPID_FIRE_DURATION = 5.0    # Sekunden
TRIPLE_SHOT_DURATION = 8.0   # Sekunden

# Highscore-Konstanten
HIGHSCORE_FILE = "highscores.json"  # Datei zum Speichern
HIGHSCORE_MAX_ENTRIES = 10          # 10 Einträge
HIGHSCORE_NAME_LENGTH = 3           # 3 Buchstaben
HIGHSCORE_DEFAULT_NAME = "AAA"      # Standardname
HIGHSCORE_ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Erlaubte Zeichen

# Menü-Konstanten
MENU_TITLE_FONT_SIZE = 72
MENU_ITEM_FONT_SIZE = 36
MENU_SELECTED_COLOR = "#FFFFFF"  # Weiß
MENU_UNSELECTED_COLOR = "#888888"  # Grau
MENU_TITLE_COLOR = "#FFAA00"  # Orange
MENU_ITEM_SPACING = 50
MENU_TRANSITION_SPEED = 0.5  # Sekunden für Übergangsanimationen
MENU_BACKGROUND_ALPHA = 180  # Hintergrund-Transparenz (0-255)

# Zusätzliche Menü-Konstanten
MENU_BUTTON_WIDTH = 300
MENU_BUTTON_HEIGHT = 50
MENU_BUTTON_PADDING = 10
MENU_BUTTON_RADIUS = 5
MENU_FADE_SPEED = 2.0  # Geschwindigkeit der Überblend-Effekte

# Schwierigkeitsgrad-Konstanten
DIFFICULTY_EASY_ASTEROIDS = 3
DIFFICULTY_NORMAL_ASTEROIDS = 5
DIFFICULTY_HARD_ASTEROIDS = 8

DIFFICULTY_EASY_INTERVAL = 8.0
DIFFICULTY_NORMAL_INTERVAL = 5.0
DIFFICULTY_HARD_INTERVAL = 3.0

# Arcade-Modus-Konstanten
ARCADE_MODE_TIME = 180  # Sekunden für Arcade-Modus
ARCADE_MODE_BONUS_TIME = 5  # Bonus-Sekunden pro zerstörtem Asteroid

# Credits-Konstanten hinzufügen (nach den Arcade-Modus-Konstanten)
CREDITS_TITLE = "CREDITS"
CREDITS_GAME_NAME = "AJITROIDS"
CREDITS_DEVELOPER = "Ajimaru"
CREDITS_GRAPHICS = "GitHub Copilot"
CREDITS_SOUND = "Freie Soundeffekte von OpenGameArt.org"
CREDITS_SPECIAL_THANKS = [
    "Boot.dev für die Python-Tutorials",
    "Pygame Community",

]
CREDITS_SCROLL_SPEED = 50  # Pixel pro Sekunde
CREDITS_LINE_SPACING = 40  # Pixel zwischen Zeilen
# Nach den Credits-Konstanten hinzufügen
CREDITS_WEBSITE = "https://ajimaru.github.io"
GAME_VERSION = "v0.7.0"  # Aktuelle Spielversion

# Level-Konstanten
POINTS_PER_LEVEL = 1000           # Punkte für Level-Up
MAX_LEVEL = 10                     # Höchstes Level
LEVEL_UP_DISPLAY_TIME = 2.0        # Anzeigezeit in Sekunden
BASE_ASTEROID_COUNT = 3            # Grundwert für Asteroiden-Anzahl
BASE_SPAWN_INTERVAL = 5.0          # Grundwert für Spawn-Interval
ASTEROID_COUNT_PER_LEVEL = 1       # Zusätzliche Asteroiden pro Level
SPAWN_INTERVAL_REDUCTION = 0.4     # Verkürzung des Intervalls pro Level

# Waffen-Konstanten
WEAPON_STANDARD = "standard"
WEAPON_LASER = "laser"       # Durchdringt mehrere Asteroiden
WEAPON_MISSILE = "missile"   # Verfolgt nahe Asteroiden
WEAPON_SHOTGUN = "shotgun"   # Mehrere Schüsse in einem Winkel

WEAPON_COLORS = {
    WEAPON_STANDARD: "#FFFFFF",  # Weiß
    WEAPON_LASER: "#00FF00",     # Grün
    WEAPON_MISSILE: "#FF0000",   # Rot
    WEAPON_SHOTGUN: "#FFAA00"    # Orange
}

# Munition für Spezialwaffen
LASER_AMMO = 15
MISSILE_AMMO = 8
SHOTGUN_AMMO = 12