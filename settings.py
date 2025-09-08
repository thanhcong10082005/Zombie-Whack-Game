import pygame
import random
import math
import time
import audio
import os
import json
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()
# pygame.mixer.set_num_channels(32)

audio = audio.audio()

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
LANES = 5
LANE_HEIGHT = 100
GROAN_TIME = 2500