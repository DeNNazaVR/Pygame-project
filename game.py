# -*- coding: utf-8 -*-

# Импорт необходимых библиотек
import pygame
import random
import sys
import sqlite3

# Инициализация Pygame
pygame.init()

# Установка размеров окна и заголовка
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический защитник")

# Определение цветов
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (255, 0, 0)
BLUE = (0, 0, 255)

GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Установка FPS и создание объекта Clock для управления частотой кадров
FPS = 60
clock = pygame.time.Clock()

# Загрузка изображения метеорита и его масштабирование
meteor_image = pygame.image.load("meteor.png")

meteor_image = pygame.transform.scale(meteor_image, (40, 40))

# Инициализация звуков
pygame.mixer.init()
explosion_sound = pygame.mixer.Sound("explosion.wav")

shoot_sound = pygame.mixer.Sound("shoot.wav")


# Класс для управления танком
class Spaceship:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = WIDTH // 2 - self.width // 2

        self.y = HEIGHT - self.height - 10
        self.speed = 5
        self.shield = False

        self.slow_time = False
        self.auto_shoot = False
        self.speed_boost = False
        self.multi_shot = False

        # Загрузка изображения танка и его масштабирование
        self.image = pygame.image.load("tank.png")
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def move(self, keys):
        speed = self.speed * 2 if self.speed_boost else self.speed
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += speed

    def draw(self):
        # Отрисовка изображения танка
        screen.blit(self.image, (self.x, self.y))

        # Отрисовка щита, если он активен
        if self.shield:
            pygame.draw.circle(screen, GREEN, (self.x + self.width // 2, self.y + self.height // 2), 30, 2)


# Класс для управления пулями
class Bullet:
    def __init__(self, x, y, offset=0):
        self.x = x + offset
        self.y = y

        self.speed = 7
        self.width = 5
        self.height = 10

    def move(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))


# Класс для управления метеоритами
class Meteor:
    def __init__(self, speed_multiplier=1):
        self.width = 40
        self.height = 40
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-HEIGHT, -self.height)
        self.speed = 2 * speed_multiplier

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            return True
        return False

    def draw(self):
        screen.blit(meteor_image, (self.x, self.y))  # Отрисовка изображения метеорита


# Класс для управления боссом
class Boss:
    def __init__(self):
        self.width = 150
        self.height = 150
        self.x = WIDTH // 2 - self.width // 2
        self.y = -self.height
        self.speed = 2
        self.health = 100
        self.direction = 1

    def move(self):
        self.y += self.speed
        if self.y >= 50:
            self.y = 50
            self.x += self.speed * self.direction
            if self.x <= 0 or self.x >= WIDTH - self.width:
                self.direction *= -1

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, self.width * (self.health / 100), 5))


# Класс для управления бонусами
class Bonus:
    def __init__(self, bonus_type):
        self.bonus_type = bonus_type
        self.width = 30
        self.height = 30
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-HEIGHT, -self.height)

        self.speed = 3
        self.alpha = 255

        self.blink_speed = 5

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            return True
        return False

    def draw(self):
        self.alpha = (self.alpha + self.blink_speed) % 256
        color = {
            "shield": GREEN,
            "time": YELLOW,
            "speed": BLUE,

            "auto_shoot": WHITE,
            "multi_shot": RED
        }[self.bonus_type]
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        pygame.draw.rect(surface, color + (self.alpha,), (0, 0, self.width, self.height))
        screen.blit(surface, (self.x, self.y))


# Класс для управления взрывами
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.frame = 0
        self.frames = 10

        self.max_radius = 30

    def draw(self):
        radius = int(self.frame * (self.max_radius / self.frames))

        alpha = int(255 * (1 - self.frame / self.frames))
        color = (255, 255, 0, alpha)

        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (radius, radius), radius)

        screen.blit(surface, (self.x - radius, self.y - radius))

        self.frame += 1
        if self.frame >= self.frames:
            return True
        return False


# Функция для отрисовки текста на экране
def draw_text(text, font_size, color, x, y):
    font = pygame.font.Font(None, font_size)

    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


# Функция для отображения меню выбора уровня сложности
def show_menu():
    while True:
        screen.fill(BLACK)
        draw_text("Выберите уровень сложности:", 48, WHITE, WIDTH // 2 - 250, HEIGHT // 2 - 100)
        draw_text("1 - Легкий", 36, GREEN, WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text("2 - Средний", 36, YELLOW, WIDTH // 2 - 100, HEIGHT // 2)
        draw_text("3 - Сложный", 36, RED, WIDTH // 2 - 100, HEIGHT // 2 + 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    return 1
                elif event.key == pygame.K_2:
                    return 2
                elif event.key == pygame.K_3:
                    return 3


# Функция для инициализации базы данных SQLite
def init_db():
    conn = sqlite3.connect(":memory:")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL
        )
    """)
    conn.commit()
    return conn


# Функция для сохранения счета в базу данных
def save_score(conn, score):
    cursor = conn.cursor()

    cursor.execute("INSERT INTO highscores (score) VALUES (?)", (score,))
    conn.commit()


# Функция для загрузки рекордов из базы данных
def load_highscores(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT score FROM highscores ORDER BY score DESC LIMIT 10")

    scores = [row[0] for row in cursor.fetchall()]

    return scores


# Функция для отображения таблицы рекордов
def show_highscores(highscores):
    screen.fill(BLACK)
    draw_text("Таблица рекордов", 48, WHITE, WIDTH // 2 - 150, 50)
    for i, score in enumerate(highscores[:10]):
        draw_text(f"{i + 1}. {score}", 36, WHITE, WIDTH // 2 - 100, 100 + i * 40)

    draw_text("Нажмите ESC для выхода", 36, RED, WIDTH // 2 - 150, HEIGHT - 100)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False


# Функция для отображения экрана паузы
def show_pause_screen():
    screen.fill(BLACK)
    draw_text("Пауза", 72, WHITE, WIDTH // 2 - 100, HEIGHT // 2 - 50)
    draw_text("Нажмите P для продолжения", 36, WHITE, WIDTH // 2 - 200, HEIGHT // 2)

    pygame.display.flip()


# Основная функция игры
def main():
    conn = init_db()

    while True:
        difficulty = show_menu()
        meteor_count = 5 + difficulty * 2

        speed_multiplier = difficulty

        spaceship = Spaceship()
        bullets = []
        meteors = [Meteor(speed_multiplier) for _ in range(meteor_count)]

        bonuses = []
        explosions = []

        score = 0

        boss = None
        boss_active = False

        running = True
        paused = False

        while running:
            if not paused:
                screen.fill(BLACK)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and not spaceship.auto_shoot:
                            if spaceship.multi_shot:
                                bullets.append(Bullet(spaceship.x + spaceship.width // 2 - 10, spaceship.y, -10))

                                bullets.append(Bullet(spaceship.x + spaceship.width // 2 - 2, spaceship.y))

                                bullets.append(Bullet(spaceship.x + spaceship.width // 2 + 6, spaceship.y, 10))

                            else:
                                bullets.append(Bullet(spaceship.x + spaceship.width // 2 - 2, spaceship.y))
                            shoot_sound.play()
                        if event.key == pygame.K_p:
                            paused = True

                if spaceship.auto_shoot:
                    if pygame.time.get_ticks() % 10 == 0:
                        if spaceship.multi_shot:
                            bullets.append(Bullet(spaceship.x + spaceship.width // 2 - 10, spaceship.y, -10))

                            bullets.append(Bullet(spaceship.x + spaceship.width // 2 - 2, spaceship.y))

                            bullets.append(Bullet(spaceship.x + spaceship.width // 2 + 6, spaceship.y, 10))
                        else:
                            bullets.append(Bullet(spaceship.x + spaceship.width // 2 - 2, spaceship.y))
                        shoot_sound.play()

                keys = pygame.key.get_pressed()
                spaceship.move(keys)

                for bullet in bullets[:]:
                    bullet.move()
                    if bullet.y < 0:
                        bullets.remove(bullet)

                for meteor in meteors[:]:
                    if meteor.move():
                        if not spaceship.shield:
                            draw_text("GAME OVER", 72, RED, WIDTH // 2 - 150, HEIGHT // 2 - 36)
                            pygame.display.flip()
                            pygame.time.wait(2000)

                            save_score(conn, score)
                            highscores = load_highscores(conn)

                            show_highscores(highscores)

                            running = False
                        else:
                            meteors.remove(meteor)
                            meteors.append(Meteor(speed_multiplier))

                for meteor in meteors[:]:
                    if (
                            spaceship.x < meteor.x + meteor.width
                            and spaceship.x + spaceship.width > meteor.x
                            and spaceship.y < meteor.y + meteor.height
                            and spaceship.y + spaceship.height > meteor.y
                    ):
                        if spaceship.shield:
                            spaceship.shield = False
                            explosions.append(Explosion(meteor.x, meteor.y))
                            explosion_sound.play()
                            meteors.remove(meteor)
                            meteors.append(Meteor(speed_multiplier))
                        else:
                            explosions.append(Explosion(spaceship.x, spaceship.y))

                            explosion_sound.play()

                            draw_text("GAME OVER", 72, RED, WIDTH // 2 - 150, HEIGHT // 2 - 36)

                            pygame.display.flip()

                            pygame.time.wait(2000)

                            save_score(conn, score)

                            highscores = load_highscores(conn)

                            show_highscores(highscores)

                            running = False

                for bullet in bullets[:]:
                    for meteor in meteors[:]:
                        if (
                                meteor.x < bullet.x < meteor.x + meteor.width
                                and meteor.y < bullet.y < meteor.y + meteor.height
                        ):
                            bullets.remove(bullet)
                            meteors.remove(meteor)
                            explosions.append(Explosion(meteor.x, meteor.y))
                            explosion_sound.play()
                            meteors.append(Meteor(speed_multiplier))
                            score += 10

                if random.randint(1, 500) == 1:
                    bonuses.append(Bonus(random.choice(["shield", "time", "speed", "auto_shoot", "multi_shot"])))

                for bonus in bonuses[:]:
                    if bonus.move():
                        bonuses.remove(bonus)
                    elif (
                            spaceship.x < bonus.x + bonus.width
                            and spaceship.x + spaceship.width > bonus.x
                            and spaceship.y < bonus.y + bonus.height
                            and spaceship.y + spaceship.height > bonus.y
                    ):
                        bonuses.remove(bonus)
                        if bonus.bonus_type == "shield":
                            spaceship.shield = True
                            pygame.time.set_timer(pygame.USEREVENT, 5000)
                        elif bonus.bonus_type == "time":
                            spaceship.slow_time = True
                            pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
                        elif bonus.bonus_type == "speed":
                            spaceship.speed_boost = True
                            pygame.time.set_timer(pygame.USEREVENT + 2, 5000)
                        elif bonus.bonus_type == "auto_shoot":
                            spaceship.auto_shoot = True
                            pygame.time.set_timer(pygame.USEREVENT + 3, 5000)
                        elif bonus.bonus_type == "multi_shot":
                            spaceship.multi_shot = True
                            pygame.time.set_timer(pygame.USEREVENT + 4, 5000)

                for event in pygame.event.get():
                    if event.type == pygame.USEREVENT:
                        spaceship.shield = False
                    if event.type == pygame.USEREVENT + 1:
                        spaceship.slow_time = False
                    if event.type == pygame.USEREVENT + 2:
                        spaceship.speed_boost = False
                    if event.type == pygame.USEREVENT + 3:
                        spaceship.auto_shoot = False
                    if event.type == pygame.USEREVENT + 4:
                        spaceship.multi_shot = False

                if score >= 500 and not boss_active:
                    boss = Boss()
                    boss_active = True

                if boss_active:
                    boss.move()
                    boss.draw()

                    for bullet in bullets[:]:
                        if (
                                boss.x < bullet.x < boss.x + boss.width
                                and boss.y < bullet.y < boss.y + boss.height
                        ):
                            bullets.remove(bullet)
                            boss.health -= 10
                            if boss.health <= 0:
                                explosions.append(Explosion(boss.x, boss.y))
                                explosion_sound.play()
                                boss_active = False
                                score += 100

                spaceship.draw()
                for bullet in bullets:
                    bullet.draw()
                for meteor in meteors:
                    meteor.draw()
                for bonus in bonuses:
                    bonus.draw()

                for explosion in explosions[:]:
                    if explosion.draw():
                        explosions.remove(explosion)

                draw_text(f"Score: {score}", 36, WHITE, 10, 10)

                pygame.display.flip()
                clock.tick(FPS)


# Запуск программы
main()
