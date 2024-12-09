import pygame
import random
import time
import math
import os

# Game Configuration
class GameConfig:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    RESOURCE_INTERVAL = 1  # seconds between resource collection

# Color Palette
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GRAY = (128, 128, 128)
    YELLOW = (255, 255, 0)

class ResourceManager:
    def __init__(self):
        self.resources = 50  # Start with some initial resources
        self.mining_rate = 1
        self.multiplier = 1

    def collect_resources(self, num_ships):
        self.resources += self.mining_rate * num_ships * self.multiplier

    def can_afford(self, cost):
        return self.resources >= cost

    def spend(self, amount):
        if self.can_afford(amount):
            self.resources -= amount
            return True
        return False

class UpgradeManager:
    def __init__(self):
        self.upgrades = [
            {
                'name': 'Free Initial Boost',
                'cost': 0,  # Free first upgrade
                'description': 'Starter boost for your galactic empire',
                'effect': self.first_free_upgrade,
                'purchased': False
            },
            {
                'name': 'Mining Efficiency',
                'cost': 50,
                'description': 'Increases resource collection rate',
                'effect': self.upgrade_mining_rate,
                'purchased': False
            },
            {
                'name': 'Ship Production',
                'cost': 100,
                'description': 'Increases maximum ship capacity',
                'effect': self.upgrade_ship_production,
                'purchased': False
            }
        ]

    def first_free_upgrade(self, resource_manager, ship_manager):
        # Free initial boost: Add 2 ships and increase initial mining rate
        resource_manager.mining_rate += 0.1
        resource_manager.multiplier *= 0.01
        for _ in range(2):
            ship_manager.create_ship()
        self.upgrades[0]['purchased'] = True

    def upgrade_mining_rate(self, resource_manager, ship_manager):
        resource_manager.mining_rate += 0.3
        resource_manager.multiplier *= 0.5
        self.upgrades[1]['purchased'] = True

    def upgrade_ship_production(self, resource_manager, ship_manager):
        ship_manager.max_ships += 2
        self.upgrades[2]['purchased'] = True

class ShipManager:
    def __init__(self, screen):
        self.screen = screen
        self.ships = []
        self.max_ships = 3  # Increased initial max ships
        self.ship_image = pygame.image.load(os.path.join("assets", "neon-valorant.gif"))  # Load ship image

    def create_ship(self):
        if len(self.ships) < self.max_ships:
            ship = Ship(random.randint(50, 200), random.randint(50, GameConfig.HEIGHT - 50), self.ship_image)
            self.ships.append(ship)
            return True
        return False

    def update_ships(self):
        for ship in self.ships:
            ship.update()

    def draw_ships(self):
        for ship in self.ships:
            ship.draw(self.screen)

class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (50, 50))  # Scale ship image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(0.5, 2)
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Wrap around screen
        self.rect.x %= GameConfig.WIDTH
        self.rect.y %= GameConfig.HEIGHT

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (40, 40))  # Scale asteroid image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(1, 3)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.left = GameConfig.WIDTH

class GalacticEmpireGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GameConfig.WIDTH, GameConfig.HEIGHT))
        pygame.display.set_caption("Galactic Empire: Infinite Expansion")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 15)

        self.resource_manager = ResourceManager()
        self.ship_manager = ShipManager(self.screen)
        self.upgrade_manager = UpgradeManager()

        # Load images for asteroids
        self.asteroid_image = pygame.image.load(os.path.join("assets", "Rock-PNG-Photos.webp"))
        self.asteroids = [Asteroid(random.randint(GameConfig.WIDTH, GameConfig.WIDTH + 200),
                                   random.randint(50, GameConfig.HEIGHT - 50), self.asteroid_image) for _ in range(5)]

        self.last_resource_collection_time = time.time()
        self.game_time = 0  # Track total game time

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_upgrade_clicks(mouse_pos)
                self.handle_ship_production(mouse_pos)

        return True

    def handle_upgrade_clicks(self, mouse_pos):
        for index, upgrade in enumerate(self.upgrade_manager.upgrades):
            rect = pygame.Rect(10, 150 + index * 50, 250, 40)
            if rect.collidepoint(mouse_pos):
                if upgrade['cost'] == 0 and not upgrade['purchased']:
                    upgrade['effect'](self.resource_manager, self.ship_manager)
                elif self.resource_manager.spend(upgrade['cost']):
                    upgrade['effect'](self.resource_manager, self.ship_manager)

    def handle_ship_production(self, mouse_pos):
        ship_rect = pygame.Rect(10, 100, 150, 40)
        if ship_rect.collidepoint(mouse_pos):
            if self.resource_manager.spend(50):
                self.ship_manager.create_ship()

    def update(self):
        current_time = time.time()
        
        if current_time - self.last_resource_collection_time >= GameConfig.RESOURCE_INTERVAL:
            self.resource_manager.collect_resources(len(self.ship_manager.ships))
            self.last_resource_collection_time = current_time
            self.game_time += 1  # Increment game time

        for asteroid in self.asteroids:
            asteroid.update()

        self.ship_manager.update_ships()

    def draw(self):
        self.screen.fill(Colors.BLACK)

        # Draw game information
        resources_text = self.font.render(f"Resources: {int(self.resource_manager.resources)}", True, Colors.WHITE)
        ships_text = self.font.render(f"Ships: {len(self.ship_manager.ships)}/{self.ship_manager.max_ships}", True, Colors.WHITE)
        time_text = self.font.render(f"Time: {self.game_time} sec", True, Colors.WHITE)
        
        self.screen.blit(resources_text, (10, 10))
        self.screen.blit(ships_text, (10, 50))
        self.screen.blit(time_text, (10, GameConfig.HEIGHT - 40))

        # Draw asteroids
        for asteroid in self.asteroids:
            self.screen.blit(asteroid.image, asteroid.rect)

        # Draw ships
        self.ship_manager.draw_ships()

        # Draw upgrades
        for index, upgrade in enumerate(self.upgrade_manager.upgrades):
            rect = pygame.Rect(10, 150 + index * 50, 250, 40)
            color = Colors.YELLOW if upgrade['cost'] == 0 and not upgrade['purchased'] else Colors.GREEN
            pygame.draw.rect(self.screen, color, rect, border_radius=10)  # Rounded corners
            
            status = "FREE" if upgrade['cost'] == 0 and not upgrade['purchased'] else f"Cost: {upgrade['cost']}"
            upgrade_text = self.font.render(f"{upgrade['name']} - {status}", True, Colors.BLACK)
            description_text = pygame.font.SysFont("Arial", 18).render(upgrade['description'], True, Colors.BLACK)
            
            self.screen.blit(upgrade_text, (rect.x + 10, rect.y + 10))
            self.screen.blit(description_text, (rect.x + 10, rect.y + 35))

        # Draw ship production button
        ship_rect = pygame.Rect(10, 100, 150, 40)
        pygame.draw.rect(self.screen, Colors.RED, ship_rect, border_radius=10)  # Rounded corners
        ship_text = self.font.render("Build Ship (50 Res)", True, Colors.WHITE)
        self.screen.blit(ship_text, (ship_rect.x + 10, ship_rect.y + 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(GameConfig.FPS)

        pygame.quit()

def main():
    game = GalacticEmpireGame()
    game.run()

if __name__ == "__main__":
    main()
