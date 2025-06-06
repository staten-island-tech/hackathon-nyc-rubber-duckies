import pygame
import random

# Initialize
pygame.init()


WIDTH, HEIGHT = 800, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rooftop Runner")

background_img = pygame.image.load("assets/NY.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLUE = (50, 100, 255)

# Clock
clock = pygame.time.Clock()
FPS = 60

player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (40, 60))

# Player
player = pygame.Rect(100, 300, 40, 60)
vel_y = 0
gravity = 0.8
jump_strength = -15
is_jumping = False

# Platforms (Rooftops)
platforms = []
x = 0
while x < WIDTH + 200:  # Fill enough for initial screen
    width = random.randint(100, 200)
    y = random.randint(300, 360)
    platforms.append(pygame.Rect(x, y, width, 50))
    x += width + random.randint(20, 60)  # smaller gap
platform_speed = 4

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Game loop
running = True
while running:
    clock.tick(FPS)
    win.blit(background_img, (0, 0))


    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # INPUT
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not is_jumping:
        vel_y = jump_strength
        is_jumping = True

    # GRAVITY
    vel_y += gravity
    player.y += vel_y

    # FLOOR COLLISION
    for plat in platforms:
        if player.colliderect(plat) and vel_y > 0:
            player.bottom = plat.top
            vel_y = 0
            is_jumping = False

    # SCROLLING PLATFORMS
    for plat in platforms:
        plat.x -= platform_speed

    # SPAWN NEW PLATFORM
    if platforms[-1].x + platforms[-1].width < WIDTH:
        new_width = random.randint(100, 200)
        new_gap = random.randint(20, 80)  # smaller gap
        new_height = platforms[-1].y + random.randint(-10, 10)  # similar height
        new_height = max(200, min(new_height, 360))  # clamp height
        new_plat = pygame.Rect(WIDTH + new_gap, new_height, new_width, 50)
        platforms.append(new_plat)

    # REMOVE OFF-SCREEN PLATFORMS
    platforms = [plat for plat in platforms if plat.right > 0]

    # DRAW PLATFORMS
    for plat in platforms:
        pygame.draw.rect(win, GRAY, plat)

    # DRAW PLAYER
    win.blit(player_img, (player.x, player.y))


    # SCORE
    score += 1
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    win.blit(text, (10, 10))

    # GAME OVER (falls below screen)
    if player.top > HEIGHT:
        running = False

    pygame.display.update()

pygame.quit()
