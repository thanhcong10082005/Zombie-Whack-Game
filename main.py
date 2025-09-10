from settings import *

from ui.utils import *
from assets import *
from menu import *
from zombie import *
from popup_effects import CartoonPopupText
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
class Game:
    def __init__(self):
        # sfx.play_background()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Whack A Zombie")
        self.clock = pygame.time.Clock()

        self.load_assets()

        # Score bar
        self.score_bar = ScoreBar(self.sunflower_frames, self.sun_frames)
        
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
        self.effects = []
        
        self.grave_positions = {}  # Track grave positions for each lane
        self.last_spawn_per_grave = {}  # Track last spawn time for each grave
        self.spawn_delay = 150  # 0.3 seconds delay between spawns from same grave
        
        # Load sounds
        audio.play_background()
        try:
            self.hit_sound = self.create_hit_sound()
        except:
            self.hit_sound = None

    def load_assets(self):
        # graphics
        self.zombie_frames = import_folder('assets', 'images', 'Zombie')
        self.cherry_frames = import_folder('assets', 'images', 'CherryBomb')
        self.explosion_frames = import_folder('assets', 'images', 'BoomDie')
        self.boom_surf = import_image('assets', 'images', 'screen', 'Boom')
        self.sunflower_frames = import_folder('assets', 'images', 'menu', 'SunFlower')
        self.sun_frames = import_folder('assets', 'images', 'menu', 'Sun')

        # crop road of background
        background_surf = import_image('assets', 'images', 'screen', 'Background', format='jpg')

        width = background_surf.get_width()
        height = background_surf.get_height()
        crop_width = int(width * 0.76)

        self.background_surf = pygame.transform.scale(background_surf.subsurface((0, 0, crop_width, height)), (SCREEN_WIDTH, SCREEN_HEIGHT))

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
        self.zombie_spawn_interval = 2000
        self.zombies = []
        self.effects = []
        self.hit_effects = []
        self.cartoon_popups = []
        self.graves = []  # List of graves: each is a dict with x, y, lane, last_spawn
        self.grave_images = import_folder('assets', 'images', 'Grave')
        self.grave_spawn_delay = 200  # ms
        self.grave_count = 6
        self.max_graves = 18
        self.last_grave_add_time = self.game_start_time
        self.init_graves()

    def init_graves(self):
        self.graves = []
        used_positions = set()
        for i in range(self.grave_count):
            while True:
                lane = random.randint(0, LANES - 1)
                x = random.randint(int(SCREEN_WIDTH * 0.7), SCREEN_WIDTH - 80)
                pos = (lane, x)
                if pos not in used_positions:
                    used_positions.add(pos)
                    break
            y = 150 + lane * LANE_HEIGHT + 25
            self.graves.append({'lane': lane, 'x': x, 'y': y, 'last_spawn': 0, 'img_idx': i % len(self.grave_images)})

    def add_graves(self, n=2):
        min_distance = 80  # Khoảng cách tối thiểu giữa các mộ cùng lane
        used_positions = set((g['lane'], g['x']) for g in self.graves)
        added = 0
        tries = 0
        while added < n and len(self.graves) < self.max_graves and tries < 200:
            lane = random.randint(0, LANES - 1)
            x = random.randint(int(SCREEN_WIDTH * 0.7), SCREEN_WIDTH - 80)
            # Kiểm tra khoảng cách với các mộ cũ cùng lane
            too_close = False
            for g in self.graves:
                if g['lane'] == lane and abs(g['x'] - x) < min_distance:
                    too_close = True
                    break
            if not too_close:
                y = 150 + lane * LANE_HEIGHT + 25
                self.graves.append({'lane': lane, 'x': x, 'y': y, 'last_spawn': 0, 'img_idx': len(self.graves) % len(self.grave_images)})
                used_positions.add((lane, x))
                added += 1
            tries += 1

    def spawn_zombie(self):
        current_time = pygame.time.get_ticks()
        game_duration = current_time - self.game_start_time
        # Thêm mộ mới mỗi 30s
        if (current_time - self.last_grave_add_time) >= 30000:
            self.add_graves(2)
            self.last_grave_add_time = current_time
        # Tính toán spawn_interval như cũ
        if game_duration < DIFFICULTY_INCREASE_INTERVAL:
            spawn_interval = 3000
        elif game_duration < 2*DIFFICULTY_INCREASE_INTERVAL:
            spawn_interval = 2000
        elif game_duration < 3*DIFFICULTY_INCREASE_INTERVAL:
            spawn_interval = 1000
        elif game_duration < 4*DIFFICULTY_INCREASE_INTERVAL:
            spawn_interval = 750
        else:
            spawn_interval = 500
        if current_time - self.last_zombie_spawn >= spawn_interval and self.graves:
            grave = random.choice(self.graves)
            if current_time - grave['last_spawn'] >= self.grave_spawn_delay:
                lane = grave['lane']
                spawn_x = grave['x']
                zombie = Zombie(lane, spawn_x, self.zombie_frames)
                audio.play_zombie_appear()
                self.zombies.append(zombie)
                self.last_zombie_spawn = current_time
                grave['last_spawn'] = current_time

    def handle_click(self, pos):
        hit_zombie = False
        for zombie in self.zombies[:]:
            if zombie.is_clickable() and zombie.get_hit_rect().collidepoint(pos):

                zombie.target = True

                bomb = CherryBomb(zombie, self.cherry_frames, func=self.create_boom)
                self.effects.append(bomb)

                audio.play_bonk_sound()

                hit_zombie = True
                break
        
        if not hit_zombie:
            self.misses += 1
            self.combo = 0

    def create_boom(self, zombie):
        boom = Boom(self.boom_surf, self.create_explosion, zombie)
        self.effects.append(boom)

    def create_explosion(self, zombie):
        if not zombie.hit: 
            score, category, category_color = zombie.take_hit()
        
            explosion = BoomDie(zombie.rect.center, self.explosion_frames)
            self.effects.append(explosion)
            
            combo_bonus = int(score * (self.combo * 0.1))
            final_score = score + combo_bonus
            
            self.score += final_score
            self.hits += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            
            # Create cartoon popup for category
            popup = CartoonPopupText(
                zombie.rect.centerx, 
                zombie.rect.centery - 60,
                category, 
                category_color
            )
            self.cartoon_popups.append(popup)
            
            # Hit effect (điểm bay lên)
            self.hit_effects.append({
                'x': zombie.rect.centerx,
                'y': zombie.rect.centery,
                'time': pygame.time.get_ticks(),
                'score': final_score
            })
        
            audio.play_cherrybomb()

    def update_effects(self):
        """Cập nhật tất cả các hiệu ứng đang hoạt động."""
        dt = self.clock.get_time() / 1000.0 # Delta time in seconds
        
        # Duyệt qua bản sao của danh sách để có thể xóa phần tử
        for effect in self.effects[:]:
            effect.update(dt)
            if effect.finished:
                self.effects.remove(effect)

    def draw_effects(self):
        """Vẽ tất cả các hiệu ứng."""
        for effect in self.effects:
            effect.draw(self.screen)
    
    def update_zombies(self):
        current_time = pygame.time.get_ticks()
        game_duration = current_time - self.game_start_time
        
        for zombie in self.zombies[:]:
            zombie.update(game_duration)
            
            # Thua khi zombie đi được 80% màn hình (không cần tới sát mép)
            if zombie.rect.right < int(SCREEN_WIDTH * 0.2) and not zombie.hit:
                audio.play_eat_sound()
                self.health -= 1
                self.zombies.remove(zombie)
                self.combo = 0
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
        self.screen.blit(self.background_surf, (0, 0))
        # Draw graves
        for grave in self.graves:
            img = self.grave_images[grave['img_idx']]
            rect = img.get_rect(center=(grave['x'], grave['y'] + 30))
            self.screen.blit(img, rect)
    
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

        audio.stop_grasswalk()
        audio.stop_looboon()
        audio.stop_brain_maniac()

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

    def draw_pause_menu(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = "PAUSED"
        shadow = self.font_large.render(pause_text, True, BLACK)
        main_text = self.font_large.render(pause_text, True, GOLD)
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 - 117))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(main_text, text_rect)

        # Buttons
        button_w, button_h = 220, 60
        gap = 30
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        resume_rect = pygame.Rect(center_x - button_w//2, center_y - button_h - gap//2, button_w, button_h)
        menu_rect = pygame.Rect(center_x - button_w//2, center_y + gap//2, button_w, button_h)

        pygame.draw.rect(self.screen, (60, 180, 60), resume_rect, border_radius=12)
        pygame.draw.rect(self.screen, (180, 60, 60), menu_rect, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, resume_rect, 3, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 3, border_radius=12)

        resume_text = self.font_medium.render("Resume", True, WHITE)
        menu_text = self.font_medium.render("Main Menu", True, WHITE)
        self.screen.blit(resume_text, resume_text.get_rect(center=resume_rect.center))
        self.screen.blit(menu_text, menu_text.get_rect(center=menu_rect.center))

        return {'resume': resume_rect, 'menu': menu_rect}

    def run(self):
        change_music_0 = False
        change_music_1 = False
        running = True
        groan_count = 0
        pause_buttons = None
        while running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
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

                                            audio.play_awooga_sound()
                                            audio.play_grasswalk()
                                            audio.stop_looboon()
                                            audio.stop_brain_maniac()
                                            audio.stop_background()

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
                        elif self.state == "paused":
                            if pause_buttons:
                                if pause_buttons['resume'].collidepoint(event.pos):
                                    self.state = "playing"
                                elif pause_buttons['menu'].collidepoint(event.pos):
                                    audio.stop_grasswalk()
                                    audio.stop_looboon()
                                    audio.stop_brain_maniac()
                                    audio.play_background()
                                    self.state = "menu"
                                    self.menu.state = "main"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "menu":
                            running = False
                        elif self.state == "playing":
                            self.state = "paused"
                        elif self.state == "paused":
                            self.state = "playing"
                    
                    elif event.key == pygame.K_r:
                        if self.state == "game_over":
                            audio.stop_grasswalk()
                            audio.stop_looboon()
                            audio.stop_brain_maniac()
                            audio.play_grasswalk()
                            self.state = "playing"
                            self.reset_game()
                    
                    elif event.key == pygame.K_m:
                        if self.state == "game_over":
                            audio.stop_grasswalk()
                            audio.stop_looboon()
                            audio.stop_brain_maniac()
                            audio.play_background()
                            
                            self.state = "menu"
                            self.menu.state = "main"
            
            # Update game logic
            if self.state == "playing":
                if self.health <= 0:
                    audio.play_losemusic_sound()
                    audio.play_scream_sound()

                    if not self.game_end_time:
                        self.game_end_time = pygame.time.get_ticks()
                    self.state = "game_over"
                else:
                    self.spawn_zombie()
                    self.update_zombies()
                    self.update_hit_effects()

                    self.update_effects()
                    self.score_bar.update(dt, self.health)

                    self.update_cartoon_popups()

                    # change music and zombie groaning
                    current_time = pygame.time.get_ticks()
                    game_duration = current_time - self.game_start_time
                    if not change_music_0:
                        if (game_duration >= 2*DIFFICULTY_INCREASE_INTERVAL):
                            audio.play_looboon()
                            audio.stop_grasswalk()
                            change_music_0 = True
                    if not change_music_1:
                        if (game_duration >= 4*DIFFICULTY_INCREASE_INTERVAL):
                            audio.stop_looboon()
                            audio.play_brain_maniac()
                            change_music_1 = True
                    if game_duration/GROAN_TIME>groan_count:
                        audio.play_zombie_groan()
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

                self.draw_effects()
                current_time = pygame.time.get_ticks()
                game_duration = (current_time - self.game_start_time) / 1000
                
                # Gọi draw của score_bar với đủ các tham số
                self.score_bar.draw(self.screen, self.score, self.health, self.hits, self.misses, self.combo, game_duration)
                self.draw_cartoon_popups()
                self.draw_game_ui()
            
            elif self.state == "paused":
                self.draw_game_background()
                for zombie in self.zombies:
                    zombie.draw(self.screen)
                self.draw_hit_effects()
                self.draw_effects()
                self.score_bar.draw(self.screen, self.score, self.health, self.hits, self.misses, self.combo, (pygame.time.get_ticks() - self.game_start_time)/1000)
                self.draw_cartoon_popups()
                self.draw_game_ui()
                pause_buttons = self.draw_pause_menu()
            
            elif self.state == "game_over":
                self.draw_game_background()
                
                # Draw zombies
                for zombie in self.zombies:
                    zombie.draw(self.screen)
                
                # sounds
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()