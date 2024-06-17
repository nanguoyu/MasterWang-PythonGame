import pygame
import sys
import qrcode
from enemy import Enemy
from utils import get_local_ip, GameServer
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.load_sounds()
        self.load_animations()
        self.action = 'idle'
        self.frame_index = 0
        self.facing_right = True
        self.image = self.animations[self.action][self.frame_index]
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))
        self.animation_speed = 0.25
        self.moving_right = False
        self.moving_left = False
        self.jumping = False
        self.attacking = False
        self.on_ground = True
        self.vel_y = 0
        self.gravity = 0.4
        self.health = 100  
        self.attack_damage = 10 
        self.alive = True

    def load_animations(self):
        self.animations = {
            'attack': self.load_animation('assets/images/Character/hero1/Attack-01/Attack-01-Sheet.png', 8),
            'idle': self.load_animation('assets/images/Character/hero1/Idle/Idle-Sheet.png', 4),
            'jump': self.load_animation('assets/images/Character/hero1/Jump-All/Jump-All-Sheet.png', 15),
            'run': self.load_animation('assets/images/Character/hero1/Run/Run-Sheet.png', 8),
        }

    def load_sounds(self):
        self.sounds = {
            'jump': pygame.mixer.Sound('assets/music/movement/Jump.wav'),
            'attack': pygame.mixer.Sound('assets/music/movement/Attack.wav'),
            'run': pygame.mixer.Sound('assets/music/movement/Step_grass.wav')
        }

    def load_animation(self, path, frame_count):
        full_image = pygame.image.load(path).convert_alpha()
        frame_width = full_image.get_width() // frame_count
        frame_height = full_image.get_height()
        return [full_image.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(frame_count)]

    def update(self, screen_width, screen_height, enemies):
        if self.alive:
            self.handle_actions()
            self.move_character(screen_width, screen_height)
            self.apply_gravity(screen_height)
            self.check_attack(enemies)  # 检查攻击行为
            self.image = self.animations[self.action][int(self.frame_index)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)


    def check_attack(self, enemies):
        if self.attacking:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    enemy.health -= self.attack_damage
                    print(f"Enemy health: {enemy.health}")
                    if enemy.health <= 0:
                        enemy.alive = False
                        enemy.kill()

    def handle_actions(self):
        current_action = self.action
        if self.jumping:
            self.action = 'jump'
            if self.action != current_action:
                self.sounds['jump'].play()
        elif self.attacking:
            self.action = 'attack'
            if self.action != current_action:
                self.sounds['attack'].play()
        elif self.moving_left or self.moving_right:
            self.action = 'run'
            if self.action != current_action:
                # print(f"current_action {current_action}, left:{self.moving_left} or right:{ self.moving_right}")
                self.sounds['run'].play()
        else:
            self.action = 'idle'
        
        if self.action != current_action:
            self.frame_index = 0
        
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.action]):
            if self.action == 'jump':
                self.jumping = False
            if self.action == 'attack':
                self.attacking = False
            self.action = "idle"
            self.frame_index = 0

        self.image = self.animations[self.action][int(self.frame_index)]

    def move_character(self, screen_width, screen_height):
        if self.moving_right:
            self.rect.x += 5
            self.facing_right = True
        if self.moving_left:
            self.rect.x -= 5
            self.facing_right = False

        # Boundary check
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def apply_gravity(self, screen_height):
        if not self.on_ground:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y
            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                self.vel_y = 0
                self.on_ground = True
            if self.rect.top < 0:
                self.rect.top = 0
                self.on_ground = False


    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # 在玩家上方显示生命值
        health_text = pygame.font.Font(None, 24).render(f'HP: {self.health}', True, (255, 0, 0))
        screen.blit(health_text, (self.rect.x, self.rect.y - 20))

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False

def handle_event(event, player):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_d:
            player.moving_right = True
        elif event.key == pygame.K_a:
            player.moving_left = True
        if event.key == pygame.K_SPACE and not player.jumping:
            player.jumping = True
            player.on_ground = False
            player.vel_y = -10
        if event.key == pygame.K_q and not player.attacking:
            player.attacking = True
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_d and not pygame.key.get_pressed()[pygame.K_a]:
            player.moving_right = False
        elif event.key == pygame.K_a and not pygame.key.get_pressed()[pygame.K_d]:
            player.moving_left = False

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

def show_menu(screen, ip, port, server):
    menu_running = True
    screen_width, screen_height = 1280, 720

    title_font = pygame.font.Font(None, 74)
    button_font = pygame.font.Font(None, 36)
    pygame.mixer.music.load('assets/music/Battle of Legends 2.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)
    title_text = title_font.render('Master Wang: find your legend', True, (255, 255, 255))
    start_text = button_font.render('Start Game', True, (255, 255, 255))

    title_rect = title_text.get_rect(center=(640, 200))
    start_rect = start_text.get_rect(center=(640, 600))
    bg = pygame.image.load('assets/images/main_menu.png').convert_alpha()
    bg = pygame.transform.scale(bg, (screen_width, screen_height))
    qr_data = f"{ip}:{port}"
    # qr_data = f"masterwang.wangdongdong.wang:80"
    qr_image = generate_qr_code(qr_data)
    qr_image.save("qr.png")
    qr_surface = pygame.image.load("qr.png")
    qr_rect = qr_surface.get_rect(center=(640, 400))

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_rect.collidepoint(mouse_pos):
                    menu_running = False
        
        if server.connected:  
            menu_running = False

        screen.blit(bg, (0, 0))
        screen.blit(title_text, title_rect)
        screen.blit(start_text, start_rect)
        screen.blit(qr_surface, qr_rect)
        pygame.display.flip()

def main():
    pygame.init()
    screen_width, screen_height = 1280, 720
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF | pygame.HWSURFACE)
    pygame.display.set_caption("Master Wang")

    # local_ip = "172.20.10.7"
    local_ip = "192.168.6.218"
    port =  random.randint(10038, 10099)
    server = GameServer(local_ip, port)
    server.start()

    show_menu(screen, local_ip, port, server)

    bg = pygame.image.load('assets/images/background.png').convert_alpha()
    bg = pygame.transform.scale(bg, (screen_width, screen_height))
    pygame.mixer.music.load('assets/music/Battle of Legends 1.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)
    player = Player(450, 600)
    server.player = player  # Set player reference in the server
    enemies = pygame.sprite.Group()
    enemy01 = Enemy(900, 600, 1)  # 难度为1
    enemies.add(enemy01)

    clock = pygame.time.Clock()
    running = True
    game_over = False
    game_over_message = ""
    game_over_sound = None
    game_over_sound_played = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                server.stop()
                pygame.quit()
                sys.exit()
            if not game_over:
                handle_event(event, player)
        
        if not game_over:
            player.update(screen_width, screen_height, enemies)
            enemies.update(screen_width, screen_height, player)
            
            if not player.alive:
                game_over = True
                game_over_message = "Try it Again"
                game_over_sound = 'assets/music/fail.wav'
            elif len(enemies) == 0:
                game_over = True
                game_over_message = "K.O."
                game_over_sound = 'assets/music/ko.wav'

        screen.blit(bg, (0, 0))
        player.draw(screen)
        enemies.draw(screen)

        if game_over:
            font = pygame.font.Font(None, 120)
            text = font.render(game_over_message, True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(text, text_rect)

            if not game_over_sound_played:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(game_over_sound)
                pygame.mixer.music.play()
                game_over_sound_played = True

        pygame.display.flip()
        clock.tick(60)

    server.stop()  # Ensure the server is stopped when the loop exits
    pygame.quit()
    print("Byebye!")

if __name__ == "__main__":
    main()
