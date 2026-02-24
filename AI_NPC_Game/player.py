import pygame


class Player:
    def __init__(self, x, y):
        # Player Properties
        self.color = (123, 171, 128)
        self.speed = 3

        # Player image
        self.l_image = pygame.image.load("Sprites/player_left.png").convert_alpha()
        self.r_image = pygame.image.load("Sprites/player_right.png").convert_alpha()

        self.l_image = pygame.transform.scale(self.l_image, (90, 90))
        self.r_image = pygame.transform.scale(self.r_image, (90, 90))

        self.rect = self.r_image.get_rect(topleft=(x, y))
        self.width = self.rect.width
        self.height = self.rect.height

        # Weapon properties
        self.weapon_width = 60
        self.weapon_height = 15
        self.weapon_color = (200, 200, 200)
        self.weapon_rect = None
        self.facing_right = True

        # Attack properties
        self.attack_damage = 10
        self.attack_cooldown = 0
        self.attack_cooldown_time = 25
        self.attacking = False
        self.attack_duration = 10
        self.attack_timer = 0

        self.space_was_pressed = False

        # Health system
        self.max_health = 100
        self.current_health = self.max_health
        self.alive = True

        self.last_dx = 1

    def move(self, keys, world_width=800, world_height=600):
        """Top-down WASD movement clamped to world bounds"""
        if self.alive:
            dx = 0
            dy = 0

            if keys[pygame.K_w] and self.rect.top > 0:
                dy = -self.speed
            if keys[pygame.K_s] and self.rect.bottom < world_height:
                dy = self.speed
            if keys[pygame.K_a] and self.rect.left > 0:
                dx = -self.speed
            if keys[pygame.K_d] and self.rect.right < world_width:
                dx = self.speed

            self.rect.x += dx
            self.rect.y += dy

            if dx > 0:
                self.facing_right = True
                self.last_dx = 1
            elif dx < 0:
                self.facing_right = False
                self.last_dx = -1

        # Decrease attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Decrease attack timer
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.attacking = False
                self.weapon_rect = None

    def attack(self, keys, npc):
        """Attack with SPACE key - creates weapon hitbox"""
        if keys[pygame.K_SPACE] and not self.space_was_pressed:
            if self.attack_cooldown == 0 and self.alive and not self.attacking:
                print("Player attacks!")
                self.attacking = True
                self.attack_cooldown = self.attack_cooldown_time
                self.attack_timer = self.attack_duration
                self.create_weapon_hitbox()

        # Check if weapon hits NPC
        if self.attacking and self.weapon_rect:
            if self.weapon_rect.colliderect(npc.rect):
                npc.take_damage(self.attack_damage)
                self.attacking = False
                self.attack_timer = 0
                self.weapon_rect = None

        self.space_was_pressed = keys[pygame.K_SPACE]

    def create_weapon_hitbox(self):
        """Create weapon rectangle in front of player (world space)"""
        if self.facing_right:
            weapon_x = self.rect.right
        else:
            weapon_x = self.rect.left - self.weapon_width
        weapon_y = self.rect.centery - self.weapon_height // 2
        self.weapon_rect = pygame.Rect(weapon_x, weapon_y,
                                       self.weapon_width, self.weapon_height)

    def take_damage(self, damage):
        """Reduce health when hit"""
        if self.alive:
            self.current_health -= damage
            print(f"Player hit! Health: {self.current_health}/{self.max_health}")
            if self.current_health <= 0:
                self.current_health = 0
                self.alive = False
                print("Player defeated!")

    def draw(self, screen, camera):
        """Draw player and weapon using camera offset"""
        draw_rect = camera.apply(self.rect)

        if self.alive:
            if self.facing_right:
                screen.blit(self.r_image, draw_rect)
            else:
                screen.blit(self.l_image, draw_rect)

        # Draw weapon in screen space
        if self.attacking and self.weapon_rect:
            weapon_draw = camera.apply(self.weapon_rect)
            pygame.draw.rect(screen, self.weapon_color, weapon_draw)
            pygame.draw.rect(screen, (255, 255, 255), weapon_draw, 2)