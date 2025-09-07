
import pygame
from ui.settings import *
from ui.utils import *
from assets import *

class BaseBar:
    def __init__(self, image_path, pos=(10, 5)):
        self.image = import_image('assets', 'images', 'menu', image_path, alpha=True)
        self.rect = self.image.get_rect(topleft=pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class StatIcon:
    def __init__(self, image_path, pos, size=(64, 64)):
        self.image = pygame.transform.scale(import_image('assets', 'images', 'menu', image_path), size)
        self.rect = self.image.get_rect(midleft=pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class StatText:
    def __init__(self, font_size=24, color=(255, 255, 255)):
        self.font = pygame.font.Font(None, font_size)
        self.color = color

    def draw(self, surface, value, pos):
        text = self.font.render(str(value), True, self.color)
        text_rect = text.get_rect(midleft=pos)
        surface.blit(text, text_rect)

class ScoreDisplay:
    def __init__(self, pos=(31, 26)):
        self.pos_or = pos
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface, score):
        text_surface = self.font.render(str(score), True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        background = pygame.Surface((38, 22))
        background.fill((252, 248, 228))
        text_x = (background.get_width() - text_rect.width) // 2
        text_y = (background.get_height() - text_rect.height) // 2
        background.blit(text_surface, (text_x, text_y))
        surface.blit(background, self.pos_or)

class TimeDisplay:
    def __init__(self, image_path, screen_width, screen_height):
        icon_size = (64, 64)
        self.icon = pygame.transform.scale(import_image('assets', 'images', 'menu', image_path), icon_size)
        self.icon_rect = self.icon.get_rect(topright=(screen_width - 70, 15))
        self.text = StatText()

    def draw(self, surface, duration):
        surface.blit(self.icon, self.icon_rect)
        total_seconds = int(duration)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.text.draw(surface, time_str, (self.icon_rect.right + 5, self.icon_rect.centery))

class ScoreBar(BaseBar):
    def __init__(self, sunflower_frames, sun_frames):
        super().__init__('ChooserBackground')
        self.score = ScoreDisplay((31, self.rect.bottom - 21))
        self.health = 8
        self.flowers = self._init_flowers(sunflower_frames)
        self.hit_icon = StatIcon('ZombieHead_0', (self.rect.right + 20, self.rect.centery))
        self.miss_icon = StatIcon('HDZombieAndBrain', (self.hit_icon.rect.right + 70, self.rect.centery))
        self.combo_icon = Sun((self.miss_icon.rect.right + 70, self.rect.centery), sun_frames)
        self.stats_text = StatText()
        self.time = TimeDisplay('Time_Traveler2', *pygame.display.get_surface().get_size())

    def _init_flowers(self, frames):
        flowers = []
        for i in range(self.health):
            x = self.rect.left + 105 + (i * 55)
            y = self.rect.centery
            flowers.append(SunFlower((x, y), frames))
        return flowers

    def update(self, dt, health):
        for i in range(min(health, self.health)):
            self.flowers[i].update(dt)
        self.combo_icon.update(dt)

    def draw(self, surface, score, health, hits, misses, combo, duration):
        super().draw(surface)
        self.score.draw(surface, score)
        for i in range(min(health, self.health)):
            self.flowers[i].draw(surface)
        self.hit_icon.draw(surface)
        self.stats_text.draw(surface, hits, (self.hit_icon.rect.right + 5, self.hit_icon.rect.centery))
        self.miss_icon.draw(surface)
        self.stats_text.draw(surface, misses, (self.miss_icon.rect.right + 5, self.miss_icon.rect.centery))
        if combo > 0:
            self.combo_icon.draw(surface)
            self.stats_text.draw(surface, f"x{combo}", (self.combo_icon.rect.right + 5, self.combo_icon.rect.centery))
        self.time.draw(surface, duration)