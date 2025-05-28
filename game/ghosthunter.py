import random
import math
from pgzero.builtins import Actor
from pygame import Rect
import pgzrun

WIDTH = 800
HEIGHT = 600

menu = True
game_active = False
game_over = False
sound_enabled = True

start_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
sound_button = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)

score = 0
survival_time = 0
max_ghosts = 5

ghosts = []
projectiles = []
frame_count = 0

current_music = None

class Hero:
    def __init__(self):
        self.frames = {
            "up": ["hero_up1", "hero_up2"],
            "down": ["hero_down1", "hero_down2"],
            "left": ["hero_left1", "hero_left2"],
            "right": ["hero_right1", "hero_right2"]
        }
        self.facing = "down"
        self.frame_index = 0
        self.actor = Actor(self.frames[self.facing][self.frame_index])
        self.actor.pos = WIDTH // 2, HEIGHT // 2
        self.actor.scale = 2.5
        self.speed = 4

    def update(self):
        moved = False
        if keyboard.left:
            self.actor.x -= self.speed
            self.facing = "left"
            moved = True
        elif keyboard.right:
            self.actor.x += self.speed
            self.facing = "right"
            moved = True
        elif keyboard.up:
            self.actor.y -= self.speed
            self.facing = "up"
            moved = True
        elif keyboard.down:
            self.actor.y += self.speed
            self.facing = "down"
            moved = True

        self.actor.x = max(20, min(WIDTH - 20, self.actor.x))
        self.actor.y = max(20, min(HEIGHT - 20, self.actor.y))
        return moved

    def animate(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames[self.facing])
        self.actor.image = self.frames[self.facing][self.frame_index]
        self.actor.scale = 1.8

    def draw(self):
        self.actor.draw()

class Ghost:
    def __init__(self):
        ghost_type = random.choice(['ghost1', 'ghost2', 'ghost3'])
        self.frames = [ghost_type] * 2
        self.frame_index = 0
        self.actor = Actor(self.frames[self.frame_index])

        self.actor.x = random.randint(50, WIDTH - 50)
        self.actor.y = random.randint(50, HEIGHT - 50)
        self.vx = random.choice([-1, 1]) * random.randint(2, 3)
        self.vy = random.choice([-1, 1]) * random.randint(2, 3)

        self.actor.scale = 2.0

    def update(self):
        self.actor.x += self.vx
        self.actor.y += self.vy

        if self.actor.left <= 0 or self.actor.right >= WIDTH:
            self.vx *= -1
        if self.actor.top <= 0 or self.actor.bottom >= HEIGHT:
            self.vy *= -1

    def animate(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.actor.image = self.frames[self.frame_index]
        self.actor.scale = 1.5

    def draw(self):
        self.actor.draw()

class Projectile:
    def __init__(self, x, y, direction):
        self.actor = Actor('projectile')
        self.actor.pos = x, y
        self.speed = 6
        if direction == "up":
            self.vx, self.vy = 0, -self.speed
        elif direction == "down":
            self.vx, self.vy = 0, self.speed
        elif direction == "left":
            self.vx, self.vy = -self.speed, 0
        else:
            self.vx, self.vy = self.speed, 0

    def update(self):
        self.actor.x += self.vx
        self.actor.y += self.vy

    def draw(self):
        self.actor.draw()

    def is_outside(self):
        return (
            self.actor.x < 0 or self.actor.x > WIDTH or
            self.actor.y < 0 or self.actor.y > HEIGHT
        )

hero = Hero()

def toggle_sound():
    global sound_enabled, current_music
    sound_enabled = not sound_enabled
    if current_music:
        current_music.stop()
    if sound_enabled:
        if menu:
            play_music('menu_music')
        elif game_active:
            play_music('game_music')
    elif menu:
        play_music('menu_music')
    elif game_active:
        play_music('game_music')

def play_music(name):
    global current_music
    if sound_enabled:
        if current_music:
            current_music.stop()
        current_music = getattr(sounds, name)
        current_music.play(-1)

def start_game():
    global game_active, menu, game_over, score, survival_time, max_ghosts
    menu = False
    game_active = True
    game_over = False
    score = 0
    survival_time = 0
    max_ghosts = 5
    ghosts.clear()
    projectiles.clear()
    hero.actor.pos = WIDTH // 2, HEIGHT // 2
    play_music('game_music')
    for _ in range(max_ghosts):
        ghosts.append(Ghost())

def update():
    global game_over, survival_time, frame_count, score, max_ghosts
    if menu or game_over:
        return

    survival_time += 1 / 60
    frame_count += 1

    # Aumenta dificuldade
    max_ghosts = 5 + (score // 5)
    while len(ghosts) < max_ghosts:
        ghosts.append(Ghost())

    hero.update()
    for ghost in ghosts:
        ghost.update()

    for projectile in projectiles[:]:
        projectile.update()
        if projectile.is_outside():
            projectiles.remove(projectile)
            continue

        for ghost in ghosts[:]:
            if projectile.actor.colliderect(ghost.actor):
                ghosts.remove(ghost)
                score += 1
                if projectile in projectiles:
                    projectiles.remove(projectile)
                break

    for ghost in ghosts:
        if ghost.actor.colliderect(hero.actor):
            game_over = True
            if current_music:
                current_music.stop()

    if frame_count % 20 == 0:
        hero.animate()
        for ghost in ghosts:
            ghost.animate()

def draw():
    screen.clear()
    if menu:
        screen.blit('background_menu', (0, 0))
        screen.draw.filled_rect(start_button, "black")
        screen.draw.text("Iniciar", center=start_button.center, fontsize=32, color="white")
        screen.draw.filled_rect(sound_button, "black")
        screen.draw.text("Som: Ligado" if sound_enabled else "Som: Desligado",
                         center=sound_button.center, fontsize=32, color="white")

    elif game_active:
        screen.blit('background_game', (0, 0))
        hero.draw()
        for ghost in ghosts:
            ghost.draw()
        for p in projectiles:
            p.draw()

        screen.draw.text(f"Pontos: {score}", (10, 10), fontsize=30, color="white")
        screen.draw.text(f"Tempo: {int(survival_time)}s", (10, 50), fontsize=30, color="white")

        if game_over:
            screen.draw.text("Derrota!", center=(WIDTH // 2, HEIGHT // 2 - 40), fontsize=64, color="red")
            screen.draw.text(f"Pontos Finais: {score}", center=(WIDTH // 2, HEIGHT // 2 + 10), fontsize=36, color="yellow")
            screen.draw.text(f"Tempo Final: {int(survival_time)}s", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=36, color="yellow")
            screen.draw.text("Pressione ENTER para voltar ao menu.",
                             center=(WIDTH // 2, HEIGHT // 2 + 100), fontsize=28, color="white")

def on_mouse_down(pos):
    if menu:
        if start_button.collidepoint(pos):
            start_game()
        elif sound_button.collidepoint(pos):
            toggle_sound()

def on_key_down(key):
    global menu, game_active

    if game_active and not game_over:
        if key == keys.SPACE:
            direction = hero.facing
            x, y = hero.actor.pos
            projectiles.append(Projectile(x, y, direction))
            if sound_enabled:
                sounds.shoot.play()

    if game_over and key == keys.RETURN:
        menu = True
        game_active = False
        play_music('menu_music')

if sound_enabled:
    play_music('menu_music')

pgzrun.go()