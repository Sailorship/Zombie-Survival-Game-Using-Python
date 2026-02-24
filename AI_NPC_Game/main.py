import pygame
import sys
import random
from player import Player
from npc import NPC, NPC2
from camera import Camera

# Initialize all pygame modules
pygame.init()

# Screen size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A_ Game")

# World size (double the screen)
WORLD_WIDTH = WIDTH * 2
WORLD_HEIGHT = HEIGHT * 2

# Clock to control FPS
clock = pygame.time.Clock()

# Colors
White = (255, 255, 255)
Red = (255, 0, 0)

# Font
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)

# Safe spawn margin (keep NPCs away from edges)
MARGIN = 150


def create_npcs():
    """Spawn 4 NPCs at random positions, avoiding the player start area"""
    npcs = []
    player_center = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
    min_dist_from_player = 270

    while len(npcs) < 4:
        x = random.randint(MARGIN, WORLD_WIDTH - MARGIN)
        y = random.randint(MARGIN, WORLD_HEIGHT - MARGIN)

        # Don't spawn too close to player
        dist = ((x - player_center[0]) ** 2 + (y - player_center[1]) ** 2) ** 0.5
        if dist < min_dist_from_player:
            continue

        npc_class = random.choice([NPC, NPC2])
        npcs.append(npc_class(x, y, WORLD_WIDTH, WORLD_HEIGHT))

    return npcs


# Create player and NPCs
player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
npcs = create_npcs()

# Camera
camera = Camera(WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
camera.load_tile("Sprites/ground.png")

# Game state
game_over = False


def draw_ui():
    """Draw game UI - always in screen space"""
    player_text = small_font.render(f"Player HP: {player.current_health}/100", True, White)
    screen.blit(player_text, (20, 20))

    alive_count = sum(1 for npc in npcs if npc.alive)
    npc_text = small_font.render(f"Enemies: {alive_count}/{len(npcs)}", True, White)
    screen.blit(npc_text, (20, 40))

    controls = small_font.render("WASD: Move | SPACE: Attack", True, White)
    screen.blit(controls, (WIDTH // 2 - 130, HEIGHT - 30))


def draw_game_over():
    """Draw game over screen"""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    game_over_text = font.render("GAME OVER", True, Red)
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    screen.blit(game_over_text, text_rect)

    restart_text = small_font.render("ESC to quit OR R to restart", True, White)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(restart_text, restart_rect)


def reset_game():
    """Reset game to initial state"""
    global player, npcs, game_over
    player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
    npcs = create_npcs()
    game_over = False
    print("Game reset!")


# Main game loop
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game_over:
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:
        player.move(keys, WORLD_WIDTH, WORLD_HEIGHT)

        # Update and attack each NPC
        for npc in npcs:
            player.attack(keys, npc)
            npc.update(player)

        camera.update(player.rect)

        if not player.alive:
            game_over = True
            print("Game Over!")

    # Draw
    camera.draw_background(screen)

    player.draw(screen, camera)
    for npc in npcs:
        npc.draw(screen, camera)

    draw_ui()

    if game_over:
        draw_game_over()

    pygame.display.update()

pygame.quit()
sys.exit()