import pygame
import random
import math
import time
import audio
import os
import json
from datetime import datetime
from popup_effects import CartoonPopupText

# Initialize Pygame
pygame.init()
pygame.mixer.init()
# pygame.mixer.set_num_channels(32)

sfx = audio.sfx()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GREEN = (144, 238, 144)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

# Game settings
INITIAL_HEALTH = 15
ZOMBIE_SPEED_BASE = 50  # pixels per second
DIFFICULTY_INCREASE_INTERVAL = 30000  # 30 seconds
LANES = 6
LANE_HEIGHT = 100
GROAN_TIME = 2500

class ScoreManager:
    def __init__(self):
        self.scores_file = "scores.json"
        self.scores = self.load_scores()
    
    def load_scores(self):
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_score(self, score, stats):
        score_entry = {
            'score': score,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'stats': stats
        }
        self.scores.append(score_entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]  # Keep top 10
        
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f)
        except:
            pass
    
    def get_top_scores(self):
        return self.scores


class Zombie:
    def __init__(self, lane, spawn_x=None):
        self.lane = lane
        if spawn_x is None:
            self.x = random.randint(-80, SCREEN_WIDTH // 2 - 200)  # Don't spawn past halfway
        else:
            self.x = spawn_x
        self.y = 150 + lane * LANE_HEIGHT + 25  # Center in lane
        self.spawn_time = pygame.time.get_ticks()
        self.speed = ZOMBIE_SPEED_BASE
        self.hit = False
        self.size = 60
        self.health = 1
        self.animation_frame = 0
        self.hit_effect_time = 0
    
    def update(self, game_duration):
        if not self.hit:
            speed_multiplier = 1 + (game_duration / 60000)  # Speed increases over time
            self.x += self.speed * speed_multiplier / FPS
            self.animation_frame += 0.1
        
        # Update hit effect
        if self.hit_effect_time > 0:
            self.hit_effect_time -= 1
    
    def draw(self, screen):
        if self.hit and self.hit_effect_time <= 0:
            return
            
        head_bob = math.sin(self.animation_frame) * 3 if not self.hit else 0
        head_y = self.y + head_bob
        
        # Zombie body (simple rectangle)
        body_rect = pygame.Rect(self.x - 20, self.y + 10, 40, 50)
        pygame.draw.rect(screen, DARK_GREEN, body_rect)
        
        # Zombie head
        head_color = GREEN if not self.hit else RED
        pygame.draw.circle(screen, head_color, (int(self.x), int(head_y)), self.size // 2)
        
        # Zombie features
        # Eyes
        eye_size = 6
        pygame.draw.circle(screen, RED, (int(self.x - 12), int(head_y - 8)), eye_size)
        pygame.draw.circle(screen, RED, (int(self.x + 12), int(head_y - 8)), eye_size)
        
        # Mouth
        pygame.draw.arc(screen, BLACK, (self.x - 10, head_y - 5, 20, 15), 0, math.pi, 2)
        
        # Hit effect
        if self.hit_effect_time > 0:
            effect_radius = self.size // 2 + (10 - self.hit_effect_time) * 2
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(head_y)), effect_radius, 3)
    
    def get_hit_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
    
    def is_clickable(self):
        return not self.hit and self.x > 0
    
    def take_hit(self):
        self.hit = True
        self.hit_effect_time = 10
        
        # Calculate time alive to determine score category
        current_time = pygame.time.get_ticks()
        time_alive = (current_time - self.spawn_time) / 1000.0  # Convert to seconds
        
        # Determine score and category based on timing
        if time_alive <= 0.5:
            score = 100
            category = "PERFECT"
            color = GOLD
        elif time_alive <= 1.5:
            score = 75
            category = "GREAT"
            color = GREEN
        elif time_alive <= 3.0:
            score = 60
            category = "GOOD"
            color = BLUE
        else:
            score = 50
            category = "NOT BAD"
            color = WHITE
            
        return score, category, color

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

class Game:
    def __init__(self):
        sfx.play_background()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Whack A Zombie")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game managers
        self.score_manager = ScoreManager()
        self.menu = Menu(self.screen, self.font_large, self.font_medium, self.font_small)
        
        # Game state
        self.state = "menu"  # menu, playing, game_over
        self.reset_game()
        
        self.grave_positions = {}  # Track grave positions for each lane
        self.last_spawn_per_grave = {}  # Track last spawn time for each grave
        self.spawn_delay = 300  # 0.3 seconds delay between spawns from same grave
        
        # Load sounds
        try:
            self.hit_sound = self.create_hit_sound()
        except:
            self.hit_sound = None
    
    def create_hit_sound(self):
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 4096 * math.sin(2 * math.pi * 440 * i / sample_rate)
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        
        return sound
    
    def reset_game(self):
        self.health = INITIAL_HEALTH
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.combo = 0
        self.max_combo = 0
        self.game_start_time = pygame.time.get_ticks()
        self.game_end_time = None
        self.last_zombie_spawn = 0
        self.zombie_spawn_interval = 2000  # 2 seconds initially
        self.zombies = []
        self.hit_effects = []
        self.cartoon_popups = []
        self.grave_positions = {}
        self.last_spawn_per_grave = {}
        self.spawn_delay = 300  # 0.3 seconds delay between spawns from same grave
        for lane in range(LANES):
            # Random grave position in first half of screen for each lane
            self.grave_positions[lane] = random.randint(-80, SCREEN_WIDTH // 2 - 200)

    def spawn_zombie(self):
        current_time = pygame.time.get_ticks()
        game_duration = current_time - self.game_start_time
        
        if game_duration < DIFFICULTY_INCREASE_INTERVAL:  # 0-30s
            spawn_interval = 2000
        elif game_duration < 2*DIFFICULTY_INCREASE_INTERVAL:  # 30-60s
            spawn_interval = 1000
        if game_duration < 3*DIFFICULTY_INCREASE_INTERVAL:  # 60-90s
            spawn_interval = 500
        elif game_duration < 4*DIFFICULTY_INCREASE_INTERVAL:  # 90-120s
            spawn_interval = 450
        else:  # 120s+
            spawn_interval = 400
        
        if current_time - self.last_zombie_spawn >= spawn_interval:
            lane = random.randint(0, LANES - 1)
            grave_key = f"grave_{lane}"
            
            if grave_key not in self.last_spawn_per_grave or \
                current_time - self.last_spawn_per_grave[grave_key] >= self.spawn_delay:
                
                # Spawn zombie at the grave position for this lane
                zombie = Zombie(lane, self.grave_positions[lane])
                # play sounds
                sfx.play_zombie_appear()
                self.zombies.append(zombie)
                self.last_zombie_spawn = current_time
                self.last_spawn_per_grave[grave_key] = current_time
    
    def handle_click(self, pos):
        hit_zombie = False
        for zombie in self.zombies[:]:
            if zombie.is_clickable() and zombie.get_hit_rect().collidepoint(pos):
                score, category, category_color = zombie.take_hit()
                
                # Combo bonus
                combo_bonus = int(score * (self.combo * 0.1))
                final_score = score + combo_bonus
                
                self.score += final_score
                self.hits += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                
                # Create cartoon popup for category
                popup = CartoonPopupText(
                    zombie.x, 
                    zombie.y - 60,  # Position above zombie
                    category, 
                    category_color
                )
                self.cartoon_popups.append(popup)
                
                # Keep old hit effect for score display
                self.hit_effects.append({
                    'x': zombie.x,
                    'y': zombie.y,
                    'time': pygame.time.get_ticks(),
                    'score': final_score
                })
                
                # if self.hit_sound:
                #     self.hit_sound.play()
                sfx.play_bonk_sound()
                
                hit_zombie = True
                break
        
        if not hit_zombie:
            self.misses += 1
            self.combo = 0
    
    def update_zombies(self):
        current_time = pygame.time.get_ticks()
        game_duration = current_time - self.game_start_time
        
        for zombie in self.zombies[:]:
            zombie.update(game_duration)
            
            if zombie.x > SCREEN_WIDTH - 100 and not zombie.hit:
                sfx.play_eat_sound()
                self.health -= 1
                self.zombies.remove(zombie)
                self.combo = 0
                if (self.health==0):
                    sfx.play_lose_sound()
            elif zombie.hit and zombie.hit_effect_time <= 0:
                self.zombies.remove(zombie)
    
    def update_hit_effects(self):
        current_time = pygame.time.get_ticks()
        self.hit_effects = [effect for effect in self.hit_effects 
                            if current_time - effect['time'] < 1000]
    
    def update_cartoon_popups(self):
        # Update all cartoon popups and remove expired ones
        self.cartoon_popups = [popup for popup in self.cartoon_popups if popup.update()]
    
    def calculate_final_score(self):
        total_shots = self.hits + self.misses
        accuracy = (self.hits / total_shots) if total_shots > 0 else 0
        
        end_time = self.game_end_time if self.game_end_time else pygame.time.get_ticks()
        game_duration = (end_time - self.game_start_time) / 1000
        
        time_bonus = int(game_duration * 10)
        accuracy_bonus = int(self.score * accuracy)
        combo_bonus = self.max_combo * 50
        
        final_score = self.score + time_bonus + accuracy_bonus + combo_bonus
        return final_score
    
    def draw_game_background(self):
        self.screen.fill(DARK_GREEN)
        
        # Draw lanes
        for i in range(LANES):
            lane_y = 150 + i * LANE_HEIGHT
            lane_rect = pygame.Rect(0, lane_y, SCREEN_WIDTH - 150, LANE_HEIGHT - 10)
            
            # Alternate lane colors
            lane_color = LIGHT_GREEN if i % 2 == 0 else DARK_GREEN
            pygame.draw.rect(self.screen, lane_color, lane_rect)
            pygame.draw.rect(self.screen, BROWN, lane_rect, 2)
        
        # Draw house
        house_rect = pygame.Rect(SCREEN_WIDTH - 150, 100, 140, 600)
        pygame.draw.rect(self.screen, BROWN, house_rect)
        
        # House details
        for i in range(LANES):
            window_y = 150 + i * LANE_HEIGHT + 30
            window_rect = pygame.Rect(SCREEN_WIDTH - 120, window_y, 40, 40)
            pygame.draw.rect(self.screen, YELLOW, window_rect)
            pygame.draw.rect(self.screen, BLACK, window_rect, 2)
    
    def draw_game_ui(self):
        # UI Background
        ui_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), ui_rect)
        
        # Health bar
        health_bg = pygame.Rect(20, 20, 200, 25)
        pygame.draw.rect(self.screen, RED, health_bg)
        
        health_fill = pygame.Rect(20, 20, (self.health / INITIAL_HEALTH) * 200, 25)
        health_color = GREEN if self.health > 10 else ORANGE if self.health > 5 else RED
        pygame.draw.rect(self.screen, health_color, health_fill)
        
        health_text = self.font_small.render(f"Health: {self.health}/{INITIAL_HEALTH}", True, WHITE)
        self.screen.blit(health_text, (25, 50))
        
        # Score with glow effect
        score_text = f"Score: {self.score}"
        score_surface = self.font_medium.render(score_text, True, GOLD)
        self.screen.blit(score_surface, (250, 25))
        
        # Combo indicator
        if self.combo > 0:
            combo_text = f"COMBO x{self.combo}!"
            combo_color = YELLOW if self.combo < 5 else ORANGE if self.combo < 10 else RED
            combo_surface = self.font_medium.render(combo_text, True, combo_color)
            self.screen.blit(combo_surface, (450, 25))
        
        # Stats
        stats_text = f"Hits: {self.hits} | Misses: {self.misses} | Max Combo: {self.max_combo}"
        stats_surface = self.font_small.render(stats_text, True, WHITE)
        self.screen.blit(stats_surface, (250, 55))
        
        # Game time
        current_time = pygame.time.get_ticks()
        game_duration = (current_time - self.game_start_time) / 1000
        time_text = f"Time: {game_duration:.1f}s"
        time_surface = self.font_small.render(time_text, True, WHITE)
        self.screen.blit(time_surface, (SCREEN_WIDTH - 150, 25))
    
    def draw_hit_effects(self):
        current_time = pygame.time.get_ticks()
        for effect in self.hit_effects:
            time_diff = current_time - effect['time']
            alpha = max(0, 255 - time_diff * 0.5)
            
            if alpha > 0:
                y_offset = time_diff * 0.1
                
                # Draw only score text (category is now handled by speech bubbles)
                score_text = f"+{effect['score']}"
                score_surface = self.font_small.render(score_text, True, GOLD)
                score_rect = score_surface.get_rect(center=(int(effect['x']), int(effect['y'] - y_offset + 20)))
                self.screen.blit(score_surface, score_rect)
    
    def draw_cartoon_popups(self):
        for popup in self.cartoon_popups:
            popup.draw(self.screen, self.font_medium, self.font_small)
    
    def draw_game_over(self):
        sfx.stop_looboon()
        sfx.stop_brain_maniac()
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text with glow
        game_over_text = "GAME OVER"
        shadow = self.font_large.render(game_over_text, True, BLACK)
        main_text = self.font_large.render(game_over_text, True, RED)
        
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 - 147))
        
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(main_text, text_rect)
        
        # Final score
        final_score = self.calculate_final_score()
        score_text = f"Final Score: {final_score}"
        score_surface = self.font_medium.render(score_text, True, GOLD)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(score_surface, score_rect)
        
        # Detailed stats
        total_shots = self.hits + self.misses
        accuracy = (self.hits / total_shots * 100) if total_shots > 0 else 0
        
        game_duration = (self.game_end_time - self.game_start_time) / 1000 if self.game_end_time else 0
        
        stats = [
            f"Zombies Defeated: {self.hits}",
            f"Shots Missed: {self.misses}",
            f"Accuracy: {accuracy:.1f}%",
            f"Max Combo: {self.max_combo}",
            f"Time Survived: {game_duration:.1f}s"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font_small.render(stat, True, WHITE)
            stat_rect = stat_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * 25))
            self.screen.blit(stat_surface, stat_rect)
        
        # Save score (only once)
        if not hasattr(self, 'score_saved'):
            stats_dict = {
                'accuracy': accuracy,
                'max_combo': self.max_combo,
                'hits': self.hits,
                'misses': self.misses,
                'time': game_duration
            }
            self.score_manager.save_score(final_score, stats_dict)
            self.score_saved = True

    def run(self):
        change_music = False
        running = True
        groan_count = 0
        
        while running:
            for event in pygame.event.get():
                # print(self.state)
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.state == "menu":
                            if self.menu.state == "main":
                                buttons = self.menu.draw_main_menu()
                                for button in buttons:
                                    if button["rect"].collidepoint(event.pos):
                                        if button["action"] == "play":
                                            sfx.stop_looboon()
                                            sfx.stop_brain_maniac()
                                            sfx.stop_background()
                                            sfx.play_looboon()
                                            self.state = "playing"
                                            self.reset_game()
                                        elif button["action"] == "scores":
                                            self.menu.state = "scores"
                                        elif button["action"] == "quit":
                                            running = False
                            
                            elif self.menu.state == "scores":
                                back_rect = self.menu.draw_scores_menu(self.score_manager)
                                if back_rect.collidepoint(event.pos):
                                    self.menu.state = "main"
                        
                        elif self.state == "playing":
                            self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "menu":
                            running = False
                        else:
                            sfx.stop_looboon()
                            sfx.stop_brain_maniac()
                            sfx.play_background()

                            self.state = "menu"
                            self.menu.state = "main"
                    
                    elif event.key == pygame.K_r:
                        if self.state == "game_over":
                            sfx.stop_looboon()
                            sfx.stop_brain_maniac()
                            sfx.play_looboon()
                            self.state = "playing"
                            self.reset_game()
                    
                    elif event.key == pygame.K_m:
                        if self.state == "game_over":
                            sfx.stop_looboon()
                            sfx.stop_brain_maniac()
                            sfx.play_background()
                            
                            self.state = "menu"
                            self.menu.state = "main"
            
            # Update game logic
            if self.state == "playing":
                if self.health <= 0:
                    if not self.game_end_time:
                        self.game_end_time = pygame.time.get_ticks()
                    self.state = "game_over"
                else:
                    self.spawn_zombie()
                    self.update_zombies()
                    self.update_hit_effects()
                    self.update_cartoon_popups()

                    # change music and zombie groaning
                    current_time = pygame.time.get_ticks()
                    game_duration = current_time - self.game_start_time
                    if not change_music:
                        if (game_duration >= 90000):
                            sfx.play_brain_maniac()
                            sfx.stop_looboon()
                            change_music = True
                    if game_duration/GROAN_TIME>groan_count:
                        sfx.play_zombie_groan()
                        groan_count+=1
            
            # Draw everything
            if self.state == "menu":
                if self.menu.state == "main":
                    self.menu.draw_main_menu()
                elif self.menu.state == "scores":
                    self.menu.draw_scores_menu(self.score_manager)
            
            elif self.state == "playing":
                self.draw_game_background()
                
                # Draw zombies
                for zombie in self.zombies:
                    zombie.draw(self.screen)
                
                self.draw_hit_effects()
                self.draw_cartoon_popups()
                self.draw_game_ui()
            
            elif self.state == "game_over":
                self.draw_game_background()
                
                # Draw zombies
                for zombie in self.zombies:
                    zombie.draw(self.screen)
                
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
