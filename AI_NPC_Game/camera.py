import pygame


class Camera:
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        self.offset_x = 0
        self.offset_y = 0

        self.tile = None
        self.tile_size = 64

    def load_tile(self, path):
        """Load the ground tile image. Call once after pygame.init()"""
        self.tile = pygame.image.load(path).convert()
        self.tile_size = self.tile.get_width()

    def update(self, target_rect):
        """Center camera on target, clamped to world bounds"""
        self.offset_x = target_rect.centerx - self.screen_width // 2
        self.offset_y = target_rect.centery - self.screen_height // 2

        self.offset_x = max(0, min(self.offset_x, self.world_width - self.screen_width))
        self.offset_y = max(0, min(self.offset_y, self.world_height - self.screen_height))

    def apply(self, rect):
        """Convert a world-space rect to screen-space for drawing"""
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y,
                           rect.width, rect.height)

    def draw_background(self, screen):
        """Tile the ground image across the visible screen area"""
        tile_size = self.tile_size

        start_x = (self.offset_x // tile_size) * tile_size
        start_y = (self.offset_y // tile_size) * tile_size

        y = start_y
        while y < self.offset_y + self.screen_height:
            x = start_x
            while x < self.offset_x + self.screen_width:
                screen.blit(self.tile, (x - self.offset_x, y - self.offset_y))
                x += tile_size
            y += tile_size