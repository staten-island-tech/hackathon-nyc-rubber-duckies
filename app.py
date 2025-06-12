import pygame
import random
import math

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

activation_boss = 2000      # Score that has to be reached in order for boss to spawn

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

obstacle_imgs = []
for name in ["cone", "banana"]:
    img = pygame.image.load(f"assets/{name}.png").convert_alpha()
    scaled_img = pygame.transform.scale(img, (30, 30))  # adjust size as needed
    obstacle_imgs.append(scaled_img)

""" 
boss_img = pygame.image.load("assets/boss.png").convert_alpha()
boss_img = pygame.transform.scale(boss_img, (100, 100))
boss_rect = pygame.Rect(WIDTH - 120, 40, 100, 100)

boss_active = False
boss_health = 5
boss_attacks = []
powerups = []

 
 
 
 
 
 """



# Platforms: each is a (Rect, Image) tuple
platforms = []
platform_speed = 4
# Force a known safe starting platform
safe_img = random.choice([img for img in building_imgs if img.get_height() > 50])
safe_width, safe_height = safe_img.get_width(), safe_img.get_height()
safe_rect = pygame.Rect(0, HEIGHT - safe_height, safe_width, safe_height)
platforms.append((safe_rect, safe_img))
x = safe_rect.right + random.randint(40, 80)

# Generate more platforms
while x < WIDTH + 200:
    img = random.choice(building_imgs)
    width, height = img.get_width(), img.get_height()
    y = HEIGHT - height
    rect = pygame.Rect(x, y, width, height)
    platforms.append((rect, img))
    x += width + random.randint(40, 80)


obstacles = []  # list of (rect, img)
obstacle_spawn_timer = 0

# After creating player rect
player = pygame.Rect(100, 0, 40, 60)
first_rect, _ = platforms[0]
player.bottom = first_rect.top

player_y = float(player.y)  # <-- add this

vel_y = 0
gravity = 0.3
jump_strength = -13
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



    # GRAVITY & POSITION UPDATE
    vel_y += gravity
    player_y += vel_y
    player.y = int(player_y)

    # FLOOR COLLISION
    for rect, _ in platforms:
        if player.colliderect(rect) and vel_y > 0:
            overlap = player.bottom - rect.top
            if 0 < overlap < 20:
                player.bottom = rect.top
                vel_y = 0
                is_jumping = False
                player_y = player.y


    # GRAVITY
# GRAVITY & POSITION UPDATE
    vel_y += gravity
    player_y += vel_y  # update float position
    player.y = int(player_y)  # sync rect position to float

    # FLOOR COLLISION
    for rect, _ in platforms:
        if player.colliderect(rect) and vel_y > 0:
            overlap = player.bottom - rect.top
            if 0 < overlap < 20:  # allow some buffer
                player.bottom = rect.top
                vel_y = 0
                is_jumping = False
                player_y = player.y
    # OBSTACLE COLLISION
    for rect, _ in obstacles:
        if player.colliderect(rect):
            print("Hit obstacle!")  # replace with game over or penalty logic
            running = False

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
    # SCROLL OBSTACLES
    for i in range(len(obstacles)):
        rect, img = obstacles[i]
        rect.x -= platform_speed
        obstacles[i] = (rect, img)

    # REMOVE OFF-SCREEN OBSTACLES
    obstacles = [(rect, img) for rect, img in obstacles if rect.right > 0]
    
    # SPAWN OBSTACLES ON PLATFORMS
    obstacle_spawn_timer += 1
    if obstacle_spawn_timer > 90:
        obstacle_spawn_timer = 0
        img = random.choice(obstacle_imgs)

        # Pick a random platform to place the obstacle on
        valid_platforms = [p for p in platforms if p[0].right > WIDTH // 2]
        if valid_platforms:
            platform_rect, _ = random.choice(valid_platforms)
            rect = img.get_rect()
            rect.x = platform_rect.x + random.randint(0, max(0, platform_rect.width - rect.width))
            rect.bottom = platform_rect.top  # sit on top of the platform
            obstacles.append((rect, img))

    # DRAW PLAYER
    win.blit(player_img, (player.x, player.y))

    # DRAW OBSTACLES
    for rect, img in obstacles:
        win.blit(img, (rect.x, rect.y))
        # pygame.draw.rect(win, (255, 0, 0), rect, 2)  # uncomment for debug hitboxes


    # SCORE
    score += 1
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    win.blit(text, (10, 10))

    """""
    # Activate boss when score reaches activation_boss
    if score >= activation_boss and not boss_active:
        boss_active = True
        # Fill the screen with solid platforms
        platforms = []
        for x in range(0, WIDTH + 200, 80):
            height = random.choice([100, 120, 140])
            y = HEIGHT - height
            rect = pygame.Rect(x, y, 80, height)
            img = random.choice(building_imgs)
            platforms.append((rect, img))
"""

    # GAME OVER (falls below screen)
    if player.top > HEIGHT:
        running = False

    """
    if boss_active:
        # Floating motion
        boss_rect.y = 40 + int(10 * math.sin(pygame.time.get_ticks() * 0.005))
        win.blit(boss_img, (boss_rect.x, boss_rect.y))

        # Show boss HP
        text = font.render(f"Boss HP: {boss_health}", True, (0, 0, 0))
        win.blit(text, (WIDTH - 200, 10))

        # Spawn boss attack
        if random.randint(0, 60) == 0:
            attack = pygame.Rect(boss_rect.centerx, boss_rect.bottom, 10, 20)
            boss_attacks.append(attack)

        # Move and draw boss attacks
        for attack in boss_attacks:
            attack.y += 5
            pygame.draw.rect(win, (255, 0, 0), attack)
        boss_attacks = [a for a in boss_attacks if a.y < HEIGHT]

        # Check player hit by attack
        for a in boss_attacks:
            if player.colliderect(a):
                running = False  # Game over

        # Spawn powerups
        if random.randint(0, 180) == 0:
            powerup = pygame.Rect(random.randint(100, WIDTH - 100), 0, 20, 20)
            powerups.append(powerup)

        # Move powerups
        for p in powerups:
            p.y += 2
            pygame.draw.rect(win, (0, 255, 0), p)

        # Check powerup pickup
        for p in powerups[:]:
            if player.colliderect(p):
                boss_health -= 1
                powerups.remove(p)

        # Boss defeated
        if boss_health <= 0:
            print("Boss defeated!")
            running = False

        
    """
    
    pygame.display.update()






