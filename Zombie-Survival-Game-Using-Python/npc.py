import pygame
import math


class NPC:
    def __init__(self, x, y, world_width=1600, world_height=1200):
        # NPC Properties
        self.color = (133, 29, 40)
        self.speed = 1
        self.world_width = world_width
        self.world_height = world_height

        # Store original patrol position
        self.ori_posx = x
        self.ori_posy = y

        # NPC image - LOAD FIRST
        self.l_image = pygame.image.load("Sprites/npc1_left.png").convert_alpha()
        self.r_image = pygame.image.load("Sprites/npc1_right.png").convert_alpha()

        # Scale DOWN to game size
        self.l_image = pygame.transform.scale(self.l_image, (90, 90))
        self.r_image = pygame.transform.scale(self.r_image, (90, 90))

        # Rectangle matches the image size (70x80)
        self.rect = self.r_image.get_rect(topleft=(x, y))

        # Extract actual width/height from rect
        self.width = self.rect.width
        self.height = self.rect.height

        self.facing_right = True

        # Patrol boundaries (horizontal patrol)
        self.direction = 1
        self.left_limit = x - 100
        self.right_limit = x + 100

        # FSM state tracking
        self.state = "PATROL"
        self.prev_state = None

        # Detection and combat
        self.detection_radius = 120
        self.attack_range = 80
        self.melee_range = 70

        # Attack properties
        self.attack_damage = 5
        self.attack_cooldown = 0
        self.attack_cooldown_time = 60
        self.attacking = False
        self.attack_duration = 15  # How long attack animation lasts
        self.attack_timer = 0

        # Return threshold
        self.return_threshold = 5

        # Health system
        self.max_health = 100
        self.current_health = self.max_health
        self.alive = True

    def update(self, player):
        """Main update loop"""
        # Decrease cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.attacking = False

        # Only update AI if alive
        if self.alive:
            self.decide_state(player)

            # Only face the player during CHASE or ATTACK; patrol handles its own facing
            if self.state in ("CHASE", "ATTACK"):
                self.facing_right = player.rect.centerx > self.rect.centerx

            # Log state changes
            if self.state != self.prev_state:
                print(f"NPC State: {self.state}")
                self.prev_state = self.state

            # Execute behavior
            if self.state == "PATROL":
                self.patrol()
            elif self.state == "CHASE":
                self.chase(player)
            elif self.state == "RETURN":
                self.return_to_patrol()
            elif self.state == "ATTACK":
                self.attack(player)

            # Clamp NPC to world bounds
            self.rect.clamp_ip(pygame.Rect(0, 0, self.world_width, self.world_height))

    def decide_state(self, player):
        """Determine state based on distance"""
        distance = math.dist(self.rect.center, player.rect.center)

        # Lock in ATTACK during cooldown
        if self.state == "ATTACK" and self.attack_cooldown > 0:
            return

        # State transitions
        if distance <= self.attack_range:
            self.state = "ATTACK"
        elif distance <= self.detection_radius:
            self.state = "CHASE"
        else:
            if self.state in ["CHASE", "ATTACK"]:
                self.state = "RETURN"
            elif self.state == "RETURN":
                if self.is_at_original_position():
                    self.state = "PATROL"

    def patrol(self):
        """Move back and forth horizontally"""
        self.rect.x += self.speed * self.direction

        # Reverse at limits
        if self.rect.x >= self.right_limit:
            self.direction = -1
            self.facing_right = False
        elif self.rect.x <= self.left_limit:
            self.direction = 1
            self.facing_right = True

    def chase(self, player):
        """Chase player in both directions"""
        distance = math.dist(self.rect.center, player.rect.center)

        # Only move if not in attack range AND not too close
        if distance > self.attack_range:
            # Move horizontally
            if player.rect.centerx > self.rect.centerx:
                self.rect.x += self.speed
            elif player.rect.centerx < self.rect.centerx:
                self.rect.x -= self.speed

            # Move vertically
            if player.rect.centery > self.rect.centery:
                self.rect.y += self.speed
            elif player.rect.centery < self.rect.centery:
                self.rect.y -= self.speed

    def attack(self, player):
        """Bare-handed melee attack - no weapon visual"""
        distance = math.dist(self.rect.center, player.rect.center)

        if self.attack_cooldown == 0 and not self.attacking:
            # Only attack if within melee range
            if distance <= self.melee_range:
                print("NPC attacks!")
                self.attacking = True
                self.attack_cooldown = self.attack_cooldown_time
                self.attack_timer = self.attack_duration

                player.take_damage(self.attack_damage)

    def return_to_patrol(self):
        """Return to original position"""
        # Move horizontally
        if self.rect.x < self.ori_posx - self.return_threshold:
            self.rect.x += self.speed
        elif self.rect.x > self.ori_posx + self.return_threshold:
            self.rect.x -= self.speed

        # Move vertically
        if self.rect.y < self.ori_posy - self.return_threshold:
            self.rect.y += self.speed
        elif self.rect.y > self.ori_posy + self.return_threshold:
            self.rect.y -= self.speed

    def is_at_original_position(self):
        """Check if at original position"""
        return (abs(self.rect.x - self.ori_posx) <= self.return_threshold and
                abs(self.rect.y - self.ori_posy) <= self.return_threshold)

    def take_damage(self, damage):
        """Reduce health when hit"""
        if self.alive:
            self.current_health -= damage
            print(f"NPC hit! Health: {self.current_health}/{self.max_health}")

            if self.current_health <= 0:
                self.current_health = 0
                self.alive = False
                print("NPC defeated!")

    def draw(self, screen, camera):
        """Draw NPC using camera offset"""
        draw_rect = camera.apply(self.rect)

        if self.alive:
            if self.facing_right:
                screen.blit(self.r_image, draw_rect)
            else:
                screen.blit(self.l_image, draw_rect)
        else:
            image = self.r_image.copy()
            image.fill((120, 120, 120), special_flags=pygame.BLEND_RGB_MULT)
            screen.blit(image, draw_rect)

        if self.alive:
            self.draw_healthbar(screen, camera)

    def draw_healthbar(self, screen, camera):
        """Draw health bar above NPC in screen space"""
        bar_width = 70
        bar_height = 6
        draw_rect = camera.apply(self.rect)
        bar_x = draw_rect.x
        bar_y = draw_rect.y - 12

        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

# Second NPC
class NPC2(NPC):
    def __init__(self, x, y, world_width=1600, world_height=1200):
        # Call parent init (inherits all stats and behaviour)
        super().__init__(x, y, world_width, world_height)

        # Override sprites with NPC2 images
        self.l_image = pygame.image.load("Sprites/npc2_left.png").convert_alpha()
        self.r_image = pygame.image.load("Sprites/npc2_right.png").convert_alpha()

        self.l_image = pygame.transform.scale(self.l_image, (90, 90))
        self.r_image = pygame.transform.scale(self.r_image, (90, 90))

        self.rect = self.r_image.get_rect(topleft=(x, y))
        self.width = self.rect.width
        self.height = self.rect.height