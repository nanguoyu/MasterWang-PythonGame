import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, difficulty):
        super().__init__()
        self.load_sounds()
        self.load_animations()
        self.action = 'idle'
        self.frame_index = 0
        self.facing_right = False
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
        self.health = 50 * difficulty 
        self.attack_damage = 5 * difficulty 
        self.attack_frequency = max(60 // difficulty, 15) 
        self.attack_timer = 0
        self.alive = True

    def load_animations(self):
        self.animations = {
            'attack': self.load_animation('assets/images/Character/hero2/itch hurt 2 sheet-Sheet.png', 7),
            'idle': self.load_animation('assets/images/Character/hero2/idle sheet-Sheet.png', 18),
            'run': self.load_animation('assets/images/Character/hero2/itch run-Sheet sheet.png', 24),
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
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        health_text = pygame.font.Font(None, 24).render(f'HP: {self.health}', True, (255, 0, 0))
        screen.blit(health_text, (self.rect.x, self.rect.y - 20))

    def handle_actions(self, player):
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

        # 攻击玩家
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.attack_timer == 0 and self.rect.colliderect(player.rect):
            self.attacking = True
            player.take_damage(self.attack_damage)
            self.attack_timer = self.attack_frequency
            print(f"Player health: {player.health}")

    def update(self, screen_width, screen_height, player):
        if self.alive:
            self.move_towards_player(player, screen_width)
            self.apply_gravity(screen_height)
            self.handle_actions(player)  # 更新动作状态
            self.image = self.animations[self.action][int(self.frame_index)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            # 检查生命值
            if self.health <= 0:
                self.alive = False
                self.kill()

    def move_towards_player(self, player, screen_width):
        if self.rect.x < player.rect.x:
            self.rect.x += 2  # 你可以调整这个值来改变敌人的移动速度
            self.facing_right = True
            self.moving_right = True
            self.moving_left = False
        elif self.rect.x > player.rect.x:
            self.rect.x -= 2
            self.facing_right = False
            self.moving_right = False
            self.moving_left = True
        else:
            self.moving_right = False
            self.moving_left = False

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
