from settings import *

class Zombie:
    def __init__(self, lane, spawn_x=None, frames=[]):
        self.lane = lane
        self.spawn_time = pygame.time.get_ticks()
        self.speed = ZOMBIE_SPEED_BASE
        self.hit = False
        self.target = False
        self.size = 60
        self.health = 1
        self.animation_frame = 0
        self.hit_effect_time = 0

        # ui
        self.frames, self.frame_index, self.animation_speed = frames, 0, 0
        self.image = self.frames[self.frame_index] 
        self.rect = self.image.get_rect()

        # Spawn zombie at a random position in the right half (50%-100% of screen width)
        if spawn_x is None:
            self.rect.centerx = random.randint(int(SCREEN_WIDTH * 0.5), SCREEN_WIDTH + 200)
        else:
            self.rect.centerx = spawn_x
        self.rect.centery = 150 + lane * LANE_HEIGHT + 25
    
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, game_duration):
        self.speed_multiplier = 1 + (game_duration / DIFFICULTY_INCREASE_INTERVAL)  
        self.rect.x -= self.speed * (self.speed_multiplier / (FPS/1.5))
        self.animation_frame += 0.1

    def update(self, game_duration):
        if not self.hit:
            # move
            self.move(game_duration)

            # animate 
            self.animation_speed = self.speed_multiplier / 5
            self.animate(self.speed_multiplier)
        
        # Update hit effect
        if self.hit_effect_time > 0:
            self.hit_effect_time -= 1
    
    def draw(self, screen):
        if self.hit and self.hit_effect_time <= 0:
            return
        
        if not self.hit:
            screen.blit(self.image, self.rect)
        
        # Hit effect
        if self.hit_effect_time > 0:
            effect_radius = self.rect.width // 2 + (10 - self.hit_effect_time) * 2
            pygame.draw.circle(screen, YELLOW, self.rect.center, effect_radius, 3)
    
    def get_hit_rect(self):
        return self.rect
    
    def is_clickable(self):
        return not self.hit and not self.target and self.rect.right > 0
    
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