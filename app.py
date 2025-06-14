import pygame
import random
import math
import time

# Initialize
pygame.init()

start_time = pygame.time.get_ticks()

WIDTH, HEIGHT = 800, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rooftop Runner")

background_img = pygame.image.load("assets/NY.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLUE = (50, 100, 255)

activation_boss = 50      # Score that has to be reached in order for boss to spawn

# Clock
clock = pygame.time.Clock()
FPS = 60

player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (40, 60))

attack_img = pygame.image.load("assets/attack.png").convert_alpha()
attack_img = pygame.transform.scale(attack_img, (20, 20))  # adjust size as needed

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

parachute_img_original = pygame.image.load("assets/parachute.png").convert_alpha()

def scale_button(image_path, target_width):
    img = pygame.image.load(image_path).convert_alpha()
    scale_factor = target_width / img.get_width()
    new_height = int(img.get_height() * scale_factor)
    return pygame.transform.smoothscale(img, (target_width, new_height))

# Resize buttons to be smaller (e.g., 200px wide)
start_btn_img = scale_button("assets/start.png", 200)
gameover_btn_img = scale_button("assets/gameover.png", 400)
youwin_btn_img = scale_button("assets/youwin.png", 200)

# Keep height same as player height (60)
target_height = 75

# Calculate proportional width to keep aspect ratio
scale_factor = target_height / parachute_img_original.get_height()
new_width = int(parachute_img_original.get_width() * scale_factor)

parachute_img = pygame.transform.scale(parachute_img_original, (new_width, target_height))

energy_img = pygame.image.load("assets/energy.png").convert_alpha()
energy_img = pygame.transform.scale(energy_img, (30, 30))  # Resize if needed

boss_img = pygame.image.load("assets/boss.png").convert_alpha()
boss_img = pygame.transform.scale(boss_img, (100, 100))
boss_rect = pygame.Rect(WIDTH - 120, HEIGHT // 2 - 50, 100, 100)

boss_active = False
boss_health = 5
boss_attacks = []
powerups = []
 
parachute_active = False

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
gravity = 0.4
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

class BossBullet:
    def __init__(self, x, y, target_x, target_y):
        self.image = attack_img
        self.rect = self.image.get_rect(center=(x, y))
        dx, dy = target_x - x, target_y - y
        dist = math.hypot(dx, dy)
        speed = 5
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class PowerUp:
    def __init__(self, x, y):
        self.image = energy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vx = -3  # Drift speed toward player

    def update(self):
        self.rect.x += self.vx  # Slowly drift left

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def collides_with(self, player):
        return self.rect.colliderect(player)

def wait_for_button_click(background_img, button_img):
    button_rect = button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    while True:
        win.blit(background_img, (0, 0))
        win.blit(button_img, button_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return

wait_for_button_click(background_img, start_btn_img)

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

    if keys[pygame.K_SPACE]:
        if not is_jumping:
            vel_y = jump_strength
            is_jumping = True
        if vel_y > 0:
            parachute_active = True
    else:
        parachute_active = False


    # Apply gravity or parachute effect
    if parachute_active:
        gravity_effect = 0.01  # Slower descent with parachute
        current_player_img = parachute_img
    else:
        gravity_effect = gravity
        current_player_img = player_img

    # GRAVITY
# GRAVITY & POSITION UPDATE
    vel_y += gravity_effect
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
            game_result = "lose"
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
    win.blit(current_player_img, (player.x, player.y))

    # DRAW OBSTACLES
    for rect, img in obstacles:
        win.blit(img, (rect.x, rect.y))
        # pygame.draw.rect(win, (255, 0, 0), rect, 2)  # uncomment for debug hitboxes


    # SCORE
    score += 1
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    win.blit(text, (10, 10))


    # Activate boss when score reaches activation_boss
    if score >= activation_boss and not boss_active:
        boss_active = True
        # Fill the screen with solid platforms
        platforms = []
        x = 0
        while x < WIDTH + 200:
            img = random.choice(building_imgs)
            width, height = img.get_width(), img.get_height()
            y = HEIGHT - height
            rect = pygame.Rect(x, y, width, height)
            platforms.append((rect, img))
            x += width + 10  # small gap to prevent overlap



    # GAME OVER (falls below screen)
    if player.top > HEIGHT:
        game_result = "lose"
        running = False

    
    if boss_active:
        # Floating motion
        boss_rect.y = 40 + int(10 * math.sin(pygame.time.get_ticks() * 0.005))
        win.blit(boss_img, (boss_rect.x, boss_rect.y))

        # Show boss HP
        text = font.render(f"Boss HP: {boss_health}", True, (0, 0, 0))
        win.blit(text, (WIDTH - 200, 10))

        # Spawn boss attack
        if random.randint(0, 100) == 0:
            bullet = BossBullet(boss_rect.centerx, boss_rect.centery, player.centerx, player.centery)
            boss_attacks.append(bullet)


        # Move and draw boss attacks
        for attack in boss_attacks:
            attack.update()
            attack.draw(win)
        boss_attacks = [a for a in boss_attacks if 0 <= a.rect.x <= WIDTH and 0 <= a.rect.y <= HEIGHT]


        # Check player hit by attack
        for attack in boss_attacks:
            if player.colliderect(attack.rect):
                game_result = "lose"
                running = False  # Game over

        if random.randint(0, 180) == 0:
            valid_platforms = [p for p in platforms if p[0].right > WIDTH // 2]
            if valid_platforms:
                platform_rect, _ = random.choice(valid_platforms)
                x = platform_rect.x + random.randint(0, max(0, platform_rect.width - energy_img.get_width()))
                y = platform_rect.top - energy_img.get_height()
                powerups.append(PowerUp(x, y))

        # Move powerups




        # Check powerup pickup
        # Update powerups
        for p in powerups:
            p.update()
            p.draw(win)

        # Check for pickup
        for p in powerups[:]:
            if p.collides_with(player):
                boss_health -= 5
                powerups.remove(p)



        # Boss defeated
        if boss_health <= 0:
            game_result="win"
            running = False
    
    pygame.display.update()

    if 'game_result' in locals():
        if game_result == "win":
            wait_for_button_click(background_img, youwin_btn_img)
        elif game_result == "lose":
            wait_for_button_click(background_img, gameover_btn_img)
