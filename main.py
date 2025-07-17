import sys
import pygame
import random
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from particle import Particle
from sounds import Sounds
from starfield import Starfield
from powerup import PowerUp  # PowerUp-Klasse importieren


# Power-up Konstanten
POWERUP_RADIUS = 15
POWERUP_SPAWN_CHANCE = 0.2  # 20% Chance dass ein Asteroid ein Power-up droppt
SHIELD_DURATION = 10.0  # Sekunden
POWERUP_TYPES = ["shield", "triple_shot", "rapid_fire"]
POWERUP_COLORS = {
    "shield": "#00FFFF",      # Cyan
    "triple_shot": "#FF00FF", # Magenta
    "rapid_fire": "#FFFF00"   # Gelb
}
RAPID_FIRE_COOLDOWN = 0.1    # Cooldown während Rapid-Fire
RAPID_FIRE_DURATION = 5.0    # Sekunden
TRIPLE_SHOT_DURATION = 8.0


def main():
    pygame.init()
    # Sound-System initialisieren
    sounds = Sounds()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()  # Gruppe für Power-ups erstellen
    
    # Container für alle Sprite-Typen setzen
    Shot.containers = (shots, updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Player.containers = (updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)  # PowerUp-Container definieren

    asteroid_field = AsteroidField()

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    dt = 0
    lives = PLAYER_LIVES
    score = 0

    font = pygame.font.Font(None, 36)

    starfield = Starfield()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)

        for asteroid in asteroids:
            # Schiffskollision
            if asteroid.collides_with(player) and not player.invincible:
                lives -= 1
                sounds.play_player_death()  # Spieler-Tod Sound
                Particle.create_ship_explosion(player.position.x, player.position.y)
                
                if lives <= 0:
                    print(f"Game Over! Final Score: {score}")
                    sys.exit()
                else:
                    player.respawn()

            # Asteroidenkollision
            for shot in shots:
                if asteroid.collides_with(shot):
                    sounds.play_explosion()  # Explosions-Sound
                    # Punktevergabe basierend auf Asteroidengröße
                    if asteroid.radius > ASTEROID_MIN_RADIUS * 2:
                        score += SCORE_LARGE
                    elif asteroid.radius > ASTEROID_MIN_RADIUS:
                        score += SCORE_MEDIUM
                    else:
                        score += SCORE_SMALL
                    print(f"Score: {score}")

                    # Asteroidenexplosion
                    Particle.create_asteroid_explosion(asteroid.position.x, asteroid.position.y)
                    
                    asteroid.split()
                    shot.kill()
                    break

        # Bildschirm-Wrapping und Bullet-Handling
        for obj in updatable:
            if not hasattr(obj, 'position'):
                continue
                
            # Schüsse entfernen, wenn sie den Bildschirm verlassen
            if isinstance(obj, Shot):
                if (obj.position.x < 0 or obj.position.x > SCREEN_WIDTH or
                    obj.position.y < 0 or obj.position.y > SCREEN_HEIGHT):
                    obj.kill()
                continue
            
            # Wrapping für alle anderen Objekte
            if obj.position.x < 0:
                obj.position.x = SCREEN_WIDTH
            elif obj.position.x > SCREEN_WIDTH:
                obj.position.x = 0
            if obj.position.y < 0:
                obj.position.y = SCREEN_HEIGHT
            elif obj.position.y > SCREEN_HEIGHT:
                obj.position.y = 0

        screen.fill("black")
        starfield.update(dt)
        starfield.draw(screen)  # Zeichne Sterne vor allen anderen Objekten
        
        for obj in drawable:
            obj.draw(screen)

        # Score anzeigen
        score_text = font.render(f"Score: {score}", True, "white")
        screen.blit(score_text, (10, 10))

        # Leben anzeigen
        lives_text = font.render(f"Lives: {lives}", True, "white")
        screen.blit(lives_text, (10, 50))

        # Power-up Kollisionen
        for powerup in powerups:
            if powerup.collides_with(player):
                player.activate_powerup(powerup.type)
                powerup.kill()

        pygame.display.flip()

        # limit the framerate to 60 FPS
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()