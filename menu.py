from settings import *

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

class Menu:
    def __init__(self, screen, font_large, font_medium, font_small):
        self.screen = screen
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small
        self.state = "main"  # main, scores
        
    def draw_main_menu(self):
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(25 + color_ratio * 30)
            g = int(25 + color_ratio * 100)
            b = int(50 + color_ratio * 50)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Game title with shadow effect
        title_text = "WHACK A ZOMBIE"
        shadow = self.font_large.render(title_text, True, BLACK)
        title = self.font_large.render(title_text, True, GOLD)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 153))
        
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Menu buttons
        buttons = [
            {"text": "PLAY GAME", "y": 350, "color": GREEN, "action": "play"},
            {"text": "HIGH SCORES", "y": 420, "color": BLUE, "action": "scores"},
            {"text": "QUIT", "y": 490, "color": RED, "action": "quit"}
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for button in buttons:
            # Button background with hover effect
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button["y"] - 25, 300, 50)
            hover = button_rect.collidepoint(mouse_pos)
            
            button_color = button["color"] if not hover else tuple(min(255, c + 50) for c in button["color"])
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, button_rect, 3, border_radius=10)
            
            # Button text
            text_surface = self.font_medium.render(button["text"], True, WHITE)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            button["rect"] = button_rect
        
        return buttons
    
    def draw_scores_menu(self, score_manager):
        # Background
        self.screen.fill(DARK_GRAY)
        
        # Title
        title = self.font_large.render("HIGH SCORES", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Scores table
        scores = score_manager.get_top_scores()
        
        if not scores:
            no_scores = self.font_medium.render("No scores yet! Play a game to set a record.", True, WHITE)
            no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.screen.blit(no_scores, no_scores_rect)
        else:
            # Table headers
            headers = ["Rank", "Score", "Date", "Accuracy", "Max Combo"]
            header_y = 150
            col_widths = [80, 120, 200, 120, 120]
            col_x = [SCREEN_WIDTH // 2 - 320 + sum(col_widths[:i]) for i in range(len(headers))]
            
            for i, header in enumerate(headers):
                header_text = self.font_medium.render(header, True, YELLOW)
                self.screen.blit(header_text, (col_x[i], header_y))
            
            for i, score_entry in enumerate(scores):
                y = header_y + 50 + i * 40
                rank_color = GOLD if i == 0 else WHITE
                
                # Rank
                rank_text = self.font_small.render(f"#{i+1}", True, rank_color)
                self.screen.blit(rank_text, (col_x[0], y))
                
                # Score
                score_text = self.font_small.render(str(score_entry['score']), True, rank_color)
                self.screen.blit(score_text, (col_x[1], y))
                
                # Date
                date_text = self.font_small.render(score_entry['date'], True, WHITE)
                self.screen.blit(date_text, (col_x[2], y))
                
                # Stats
                stats = score_entry.get('stats', {})
                accuracy = f"{stats.get('accuracy', 0):.1f}%"
                accuracy_text = self.font_small.render(accuracy, True, WHITE)
                self.screen.blit(accuracy_text, (col_x[3], y))
                
                combo = str(stats.get('max_combo', 0))
                combo_text = self.font_small.render(combo, True, WHITE)
                self.screen.blit(combo_text, (col_x[4], y))

        # Back button
        back_rect = pygame.Rect(50, SCREEN_HEIGHT - 80, 100, 40)
        pygame.draw.rect(self.screen, BLUE, back_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, back_rect, 2, border_radius=5)
        
        back_text = self.font_medium.render("BACK", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        return back_rect