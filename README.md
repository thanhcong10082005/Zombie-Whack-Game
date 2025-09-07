# 🧟 Zombie Whack Game

A fast-paced whack-a-mole style game built with Python and Pygame where players must defend their house from approaching zombies!

## 🎮 Game Overview

When the game starts, zombies randomly appear from graves scattered across 6 lanes. Each zombie begins moving toward your house to eat brains. Your mission: click on the zombies to whack them before they reach your house!

### 🎯 Objective

- Click on zombies to eliminate them before they reach your house
- Survive as long as possible while maintaining your health
- Build combos for higher scores
- Set new high score records

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Pygame library

### Installation

1. **Clone or download this repository**

   ```bash
   git clone <repository-url>
   cd game_prj_1
   ```

2. **Install Pygame**

   ```bash
   pip install pygame
   ```

3. **Run the game**
   ```bash
   python main.py
   ```

## 🕹️ How to Play

### Controls

- **Left Mouse Click**: Whack zombies
- **ESC**: Return to main menu or exit
- **R**: Restart game (on game over screen)
- **M**: Return to main menu (on game over screen)

### Game Rules

- **Starting Health**: 15 hearts
- **Zombie Behavior**: Each zombie takes 1 or more hits to kill and has 2-5 seconds to reach your house
- **Health Loss**: Lose 1 heart when a zombie reaches your house
- **Game Over**: When all hearts are depleted

## 🎨 Features

### Visual Effects

- Animated zombie movement with head bobbing
- Hit effects with score popups
- Color-coded health bar
- Lane-based gameplay with alternating colors
- Combo indicators

### Audio

- Procedurally generated hit sound effects
- Sound feedback on successful zombie elimination

### Persistent High Scores

- Top 10 scores saved locally
- Detailed statistics including accuracy and max combo
- Date and time tracking for each score

## 🏗️ Technical Details

### Architecture

- **Object-Oriented Design**: Separate classes for Game, Zombie, Menu, and ScoreManager
- **State Management**: Clean separation between menu, playing, and game over states
- **Event-Driven**: Pygame event handling for user interactions

### Key Components

- `Game`: Main game controller and display manager
- `Zombie`: Individual zombie entity with AI and animation
- `Menu`: User interface for main menu and high scores
- `ScoreManager`: Persistent score storage and retrieval

### Performance

- 60 FPS gameplay
- Efficient sprite rendering
- Optimized collision detection
- Memory-conscious effect management

## 📁 Project Structure

```
game_prj_1/
├── main.py                    # Complete game implementation
├── project+describtion.md     # Original assignment requirements
├── scores.json               # High score data (auto-generated)
├── README.md                 # This file
└── CLAUDE.md                 # Development guidance
```

## 🎯 Assignment Requirements Met

### Required Features ✅

- **Background Design**: Multiple zombie spawn locations (6 lanes)
- **Zombie Design**: Animated zombie sprites with distinct features
- **Zombie Head**: Timed appearance with 5-second countdown
- **Mouse Interaction**: Precise click detection and hit registration
- **Player Score**: Comprehensive scoring with hits/misses tracking

### Bonus Features ✅

- **Sound Effects**: Procedural audio generation for hits
- **Visual Effects**: Hit animations and score popups
- **Animations**: Zombie movement and head bobbing effects
- **High Score System**: Persistent leaderboard with statistics
- **Combo System**: Score multipliers for consecutive hits

## 🛠️ Development

### Running Tests

Currently, this is a single-file game without separate test files. To test functionality:

1. Run the game with `python main.py`
2. Test all menu interactions
3. Verify gameplay mechanics
4. Check score persistence

### Modifying Game Settings

Key constants can be adjusted at the top of `main.py`:

- `INITIAL_HEALTH`: Starting player health (default: 15)
- `LANES`: Number of gameplay lanes (default: 6)
- `ZOMBIE_SPEED_BASE`: Base movement speed (default: 50)
- `SCREEN_WIDTH/HEIGHT`: Display dimensions (default: 1200x800)
