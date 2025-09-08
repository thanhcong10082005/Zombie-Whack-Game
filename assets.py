from settings import *
from ui.utils import *

class Animated:
    def __init__(self, pos, frames):
        self.frames = frames
        self.frame_index = 0
        
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=pos)
        
        self.finished = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class CherryBomb(Animated):
    def __init__(self, zombie, frames, func):
        self.target = zombie
        self.animation_speed = 30  
        super().__init__(self.target.rect.center, frames)
        self.rect.midbottom = self.target.rect.midbottom
        self.func = func


    def update(self, dt):
        if self.finished:
            return

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.finished = True
            if self.func:
                self.func(self.target)
        else:
            self.image = self.frames[int(self.frame_index)]

class BoomDie(Animated):
    def __init__(self, pos, frames):
        super().__init__(pos, frames)
        self.animation_speed = 15  

    def update(self, dt):
        if self.finished:
            return
            
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.finished = True
        else:
            self.image = self.frames[int(self.frame_index)]

class SunFlower(Animated):
    def __init__(self, pos, frames):
        super().__init__(pos, frames)
        self.animation_speed = 7  

    def update(self, dt):
        self.frame_index += self.animation_speed * dt
        
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
            
        self.image = self.frames[int(self.frame_index)]

class Boom:
    def __init__(self, image, func, zombie):
        self.image = image
        self.rect = self.image.get_rect(center=zombie.rect.center) 
        
        self.duration = 100 
        self.start_time = pygame.time.get_ticks()
        
        self.finished = False
        self.func = func
        self.target = zombie 

    def update(self, dt):
        if self.finished:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.finished = True
            if self.func:
                self.func(self.target)

    def draw(self, screen):
        self.image.set_alpha(150) 
        screen.blit(self.image, self.rect)

class Sun(Animated):
    def __init__(self, pos, frames):
        super().__init__(pos, frames)
        self.animation_speed = 10 # Tốc độ quay của mặt trời

    def update(self, dt):
        self.frame_index += self.animation_speed * dt
        
        # Đảm bảo hoạt ảnh lặp lại
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
            
        self.image = self.frames[int(self.frame_index)]

