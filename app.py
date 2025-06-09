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

# Load building images
building_imgs = []
for i in range(1, 5):
    raw_img = pygame.image.load(f"assets/building{i}.png").convert_alpha()
    scaled_img = pygame.transform.scale(raw_img, (int(raw_img.get_width() * 0.2), int(raw_img.get_height() * 0.2)))
    building_imgs.append(scaled_img)

# Platforms: each is a (Rect, Image) tuple
platforms = []
platform_speed = 4
x = 0
while x < WIDTH + 200:
    img = random.choice(building_imgs)
    width, height = img.get_width(), img.get_height()
    y = HEIGHT - height
    rect = pygame.Rect(x, y, width, height)
    platforms.append((rect, img))
    x += width + random.randint(40, 80)

# After creating player rect
player = pygame.Rect(100, 0, 40, 60)
first_rect, _ = platforms[0]
player.bottom = first_rect.top

player_y = float(player.y)  # <-- add this

vel_y = 0
gravity = 0.6
jump_strength = -18
is_jumping = False



def get_difficulty(score):
    difficulty = min(score // 500, 10)
    min_gap = 80 + difficulty * 5       
    max_gap = 100 + difficulty * 8      
    min_width = 120 - difficulty * 5
    max_width = 200 - difficulty * 8
    return max(min_gap, 60), max_gap, max(min_width, 60), max(max_width, 100)


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
# GRAVITY & POSITION UPDATE
    vel_y += gravity
    player_y += vel_y  # update float position
    player.y = int(player_y)  # sync rect position to float

    # FLOOR COLLISION
    for rect, _ in platforms:
        if player.colliderect(rect) and vel_y > 0:
            if player.bottom - vel_y <= rect.top:  # player was above last frame
                player.bottom = rect.top
                vel_y = 0
                is_jumping = False
                player_y = player.y  # sync float position after collision fix

    # SCROLLING PLATFORMS
    for i in range(len(platforms)):
        rect, img = platforms[i]
        rect.x -= platform_speed
        platforms[i] = (rect, img)


    if platforms[-1][0].right < WIDTH:
        min_gap, max_gap, *_ = get_difficulty(score)
        img = random.choice(building_imgs)
        width, height = img.get_width(), img.get_height()
        gap = random.randint(min_gap, max_gap)
        x = WIDTH + gap
        y = HEIGHT - height
        rect = pygame.Rect(x, y, width, height)
        platforms.append((rect, img))

    # REMOVE OFF-SCREEN PLATFORMS
    platforms = [(rect, img) for rect, img in platforms if rect.right > 0]


    # DRAW PLATFORMS
    for rect, img in platforms:
        win.blit(img, (rect.x, rect.y))
        pygame.draw.rect(win, (255, 0, 0), rect, 2)  # red collision box



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

for i, img in enumerate(building_imgs, 1):
    print(f"Building{i} size: {img.get_size()}")

