import pygame
import random
import sys

# --- Khởi tạo ---
pygame.init()
WIDTH, HEIGHT = 490, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rialo Racing Game")

FPS = 60
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
GRAY, YELLOW, GREEN, RED = (120, 120, 120), (255, 255, 0), (0, 200, 0), (200, 30, 30)

FONT = pygame.font.SysFont("comicsansms", 28)
BIG_FONT = pygame.font.SysFont("comicsansms", 48)

# --- Load ảnh ---
def load_img(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except:
        return None

PLAYER_IMG = load_img("player_car.png", (70, 90))
ENEMY_IMGS = [load_img(f"enemy{i}.png", (60, 60)) for i in range(1, 7)]
ENEMY_IMGS = [im for im in ENEMY_IMGS if im]

# Logo
LOGO_IMG = load_img("logo.png", (150, 150))

# Cảnh vật 2 bên đường
SIDE_OBJECTS = [
    load_img("tree.png", (60, 80)),
    load_img("house.png", (80, 100)),
    load_img("bush.png", (70, 90))
]
SIDE_OBJECTS = [im for im in SIDE_OBJECTS if im]

# --- Lớp đối tượng ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG if PLAYER_IMG else pygame.Surface((50, 90))
        if not PLAYER_IMG:
            self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-100))
        self.speed = 6

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if self.rect.left < 50:
            self.rect.left = 50
        if self.rect.right > WIDTH-50:
            self.rect.right = WIDTH-50

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed, score_callback):
        super().__init__()
        size = (60, 60)
        if ENEMY_IMGS:
            self.image = pygame.transform.smoothscale(random.choice(ENEMY_IMGS), size)
        else:
            self.image = pygame.Surface(size)
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(60, WIDTH-110)
        self.rect.y = -100
        self.speed = speed
        self.score_callback = score_callback

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
            self.score_callback()

class SideObject(pygame.sprite.Sprite):
    def __init__(self, x, speed):
        super().__init__()
        if SIDE_OBJECTS:
            self.image = random.choice(SIDE_OBJECTS)
        else:
            self.image = pygame.Surface((40, 60))
            self.image.fill((0, random.randint(150, 255), 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -random.randint(50, 200)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# --- Vẽ đường ---
def draw_road(offset):
    WIN.fill((0, 150, 0))
    road_rect = pygame.Rect(45, 0, WIDTH-90, HEIGHT)
    pygame.draw.rect(WIN, (50, 50, 50), road_rect)
    dash_h, gap = 40, 20
    lane_x = WIDTH//2
    y = - (offset % (dash_h+gap))
    while y < HEIGHT:
        pygame.draw.line(WIN, WHITE, (lane_x, y), (lane_x, y+dash_h), 6)
        y += dash_h+gap

# --- Menu chọn độ khó ---
def menu():
    options = ["Easy", "Medium", "Hard"]
    selected = 0
    while True:
        WIN.fill(GRAY)

        if LOGO_IMG:
            WIN.blit(LOGO_IMG, (WIDTH//2 - LOGO_IMG.get_width()//2, 30))

        title = BIG_FONT.render("Rialo Racing Game", True, YELLOW)
        WIN.blit(title, (WIDTH//2-title.get_width()//2, 170))

        for i, opt in enumerate(options):
            color = WHITE if i != selected else YELLOW
            txt = FONT.render(opt, True, color)
            WIN.blit(txt, (WIDTH//2 - txt.get_width()//2, 280+i*60))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected-1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected+1) % len(options)
                if event.key == pygame.K_RETURN:
                    return options[selected].lower()

# --- Vòng chơi ---
def game_loop(difficulty):
    clock = pygame.time.Clock()
    player = Player()
    enemies = pygame.sprite.Group()
    side_objects = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    if difficulty == "easy":
        enemy_speed, spawn_delay = 4, 1200
    elif difficulty == "medium":
        enemy_speed, spawn_delay = 6, 900
    else:
        enemy_speed, spawn_delay = 9, 600

    score, spawn_timer, side_timer, offset = 0, 0, 0, 0
    running, game_over = True, False

    def add_score():
        nonlocal score, enemy_speed
        score += 1
        enemy_speed += 0.2

    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return True
                if event.key == pygame.K_q: return False

        if not game_over:
            player.update(keys)
            enemies.update()
            side_objects.update()

            spawn_timer += dt
            if spawn_timer >= spawn_delay:
                spawn_timer = 0
                e = Enemy(enemy_speed, add_score)
                enemies.add(e)
                all_sprites.add(e)

            side_timer += dt
            if side_timer >= 800:
                side_timer = 0
                # spawn cảnh vật ngoài mặt đường
                if random.choice([True, False]):
                    x_pos = random.randint(0,10)  # trái ngoài đường
                else:
                    x_pos = random.randint(WIDTH-80, WIDTH-40)  # phải ngoài đường
                s = SideObject(x_pos, enemy_speed-1)
                side_objects.add(s)
                all_sprites.add(s)

            offset += enemy_speed
            for e in enemies:
                if player.rect.inflate(-20, -20).colliderect(e.rect.inflate(-10, -10)):
                    game_over = True
                    break

        draw_road(offset)
        side_objects.draw(WIN)
        all_sprites.draw(WIN)

        score_txt = FONT.render(f"Score: {score}", True, WHITE)
        WIN.blit(score_txt, (10, 10))

        if game_over:
            go_txt = BIG_FONT.render("GAME OVER", True, YELLOW)
            info_txt = FONT.render("R = Restart, Q = Quit", True, WHITE)
            WIN.blit(go_txt, (WIDTH//2-go_txt.get_width()//2, HEIGHT//2-50))
            WIN.blit(info_txt, (WIDTH//2-info_txt.get_width()//2, HEIGHT//2+20))

        pygame.display.flip()

# --- Main ---
if __name__ == "__main__":
    while True:
        diff = menu()
        again = game_loop(diff)
        if not again:
            break
