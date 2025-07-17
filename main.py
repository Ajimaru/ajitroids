import sys
import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    AsteroidField.containers = updatable
    asteroid_field = AsteroidField()

    Player.containers = (updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    dt = 0
    score = 0

    font = pygame.font.Font(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)

        for asteroid in asteroids:
            if asteroid.collides_with(player):
                print(f"Game Over! Final Score: {score}")
                sys.exit()

            for shot in shots:
                if asteroid.collides_with(shot):
                    # Punktevergabe basierend auf Asteroidengröße
                    if asteroid.radius > ASTEROID_MIN_RADIUS * 2:
                        score += SCORE_LARGE
                    elif asteroid.radius > ASTEROID_MIN_RADIUS:
                        score += SCORE_MEDIUM
                    else:
                        score += SCORE_SMALL
                    print(f"Score: {score}")

                    asteroid.split()
                    shot.kill()
                    break

        # Bildschirm-Wrapping nur für Objekte mit position-Attribut
        for obj in updatable:
            if hasattr(obj, 'position'):  # Prüfe ob das Objekt eine Position hat
                if obj.position.x < 0:
                    obj.position.x = SCREEN_WIDTH
                elif obj.position.x > SCREEN_WIDTH:
                    obj.position.x = 0
                if obj.position.y < 0:
                    obj.position.y = SCREEN_HEIGHT
                elif obj.position.y > SCREEN_HEIGHT:
                    obj.position.y = 0

        screen.fill("black")

        for obj in drawable:
            obj.draw(screen)

        # Score anzeigen
        score_text = font.render(f"Score: {score}", True, "white")
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        # limit the framerate to 60 FPS
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()