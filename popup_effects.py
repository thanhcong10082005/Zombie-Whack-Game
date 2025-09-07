"""
Popup Effects Module for Zombie Whack Game

This module contains visual effect classes for displaying animated text popups,
specifically the cartoon-style 3D text effects used for hit feedback.
"""

import pygame
import math

# Color constants (copied from main for independence)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class CartoonPopupText:
    """
    Plants vs Zombies style cartoon text popup with 3D effects.
    
    Features:
    - Bold 3D letters with thick black outlines
    - Colorful gradient fills
    - Explosive bounce-in animation
    - Gentle bobbing during display
    - Pop-out shrink exit animation
    """
    
    def __init__(self, x, y, text, category_color):
        self.x = x
        self.y = y
        self.original_y = y
        self.text = text
        self.category_color = category_color
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2500  # 2.5 seconds
        self.scale = 0.0
        self.target_scale = 1.2
        self.bounce_phase = 0.0
        self.rotation = 0.0
        
        # Color gradients for each category
        self.gradients = {
            GOLD: [(255, 255, 100), (255, 215, 0), (255, 165, 0)],  # Perfect - Gold gradient
            GREEN: [(144, 238, 144), (0, 255, 0), (0, 200, 0)],      # Great - Green gradient  
            BLUE: [(173, 216, 230), (0, 191, 255), (0, 100, 255)],   # Good - Blue gradient
            WHITE: [(255, 255, 255), (230, 230, 230), (200, 200, 200)]  # Not Bad - White gradient
        }
        
    def update(self):
        """Update animation state and return True if still alive"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.spawn_time
        
        # Animation phases
        if elapsed < 300:  # First 0.3 seconds - explosive entrance
            progress = elapsed / 300.0
            self.scale = self.ease_out_back(progress) * self.target_scale
            self.rotation = math.sin(progress * math.pi * 4) * 10  # Wobble effect
        elif elapsed < self.lifetime - 500:  # Middle phase - stable with gentle bob
            self.scale = self.target_scale
            self.bounce_phase += 0.15
            self.y = self.original_y - 20 + math.sin(self.bounce_phase) * 3
            self.rotation = math.sin(self.bounce_phase * 0.5) * 2
        else:  # Last 0.5 seconds - pop-out shrink
            fade_progress = (elapsed - (self.lifetime - 500)) / 500.0
            self.scale = self.target_scale * (1.0 - fade_progress)  # Shrink to 0
            self.y -= 1.0  # Gentle float upward
            self.rotation = 0  # No rotation during exit
        
        return elapsed < self.lifetime
    
    def ease_out_back(self, t):
        """Back easing for explosive entrance animation"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    def draw_3d_text(self, screen, font, text, x, y, colors, outline_thickness=4):
        """Draw 3D cartoon text with thick outlines and gradient"""
        if self.scale <= 0:
            return
            
        # Create multiple layers for 3D depth effect
        depth_layers = 6
        
        # Draw depth layers (back to front)
        for depth in range(depth_layers, 0, -1):
            depth_color = (max(0, colors[2][0] - depth * 20), 
                          max(0, colors[2][1] - depth * 20), 
                          max(0, colors[2][2] - depth * 20))
            
            offset_x = depth * 2
            offset_y = depth * 2
            
            # Create text surface
            text_surface = font.render(text, True, depth_color)
            
            # Apply rotation if any
            if abs(self.rotation) > 0.1:
                text_surface = pygame.transform.rotate(text_surface, self.rotation)
            
            # Scale the text
            if self.scale != 1.0:
                scaled_width = max(1, int(text_surface.get_width() * self.scale))
                scaled_height = max(1, int(text_surface.get_height() * self.scale))
                text_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))
            
            # Position with depth offset
            final_x = x - text_surface.get_width() // 2 + offset_x
            final_y = y - text_surface.get_height() // 2 + offset_y
            
            screen.blit(text_surface, (final_x, final_y))
        
        # Draw main text with thick black outline
        main_font = font
        
        # Draw thick black outline
        for dx in range(-outline_thickness, outline_thickness + 1):
            for dy in range(-outline_thickness, outline_thickness + 1):
                if dx*dx + dy*dy <= outline_thickness*outline_thickness:
                    outline_surface = main_font.render(text, True, BLACK)
                    
                    if abs(self.rotation) > 0.1:
                        outline_surface = pygame.transform.rotate(outline_surface, self.rotation)
                    
                    if self.scale != 1.0:
                        scaled_width = max(1, int(outline_surface.get_width() * self.scale))
                        scaled_height = max(1, int(outline_surface.get_height() * self.scale))
                        outline_surface = pygame.transform.scale(outline_surface, (scaled_width, scaled_height))
                    
                    outline_x = x - outline_surface.get_width() // 2 + dx
                    outline_y = y - outline_surface.get_height() // 2 + dy
                    screen.blit(outline_surface, (outline_x, outline_y))
        
        # Draw main gradient text (simulate gradient with multiple colors)
        for i, color in enumerate(colors):
            main_surface = main_font.render(text, True, color)
            
            if abs(self.rotation) > 0.1:
                main_surface = pygame.transform.rotate(main_surface, self.rotation)
            
            if self.scale != 1.0:
                scaled_width = max(1, int(main_surface.get_width() * self.scale))
                scaled_height = max(1, int(main_surface.get_height() * self.scale))
                main_surface = pygame.transform.scale(main_surface, (scaled_width, scaled_height))
            
            # Slight offset for gradient effect
            main_x = x - main_surface.get_width() // 2 - i
            main_y = y - main_surface.get_height() // 2 - i
            screen.blit(main_surface, (main_x, main_y))
    
    def draw(self, screen, font_medium, font_small):
        """Draw the cartoon popup text effect"""
        if self.scale <= 0:
            return
        
        # Use larger font for cartoon effect
        big_font = pygame.font.Font(None, 48)
        
        # Get gradient colors for this category
        gradient_colors = self.gradients.get(self.category_color, self.gradients[WHITE])
        
        # Draw 3D cartoon text (no background burst)
        self.draw_3d_text(screen, big_font, self.text, int(self.x), int(self.y), 
                         gradient_colors, outline_thickness=5)