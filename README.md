# Zombie Survival Game Using Python

## Description
A 2D Zombie Survival Game built with Python and Pygame. The player fights off waves of zombies using melee attacks, with a complete gameplay loop including health tracking and win/lose conditions.

## Features
- WASD movement clamped to world boundaries
- SPACE melee attack with directional hitbox and cooldown
- Zombies that chase and damage the player
- Health system for player and zombies
- Win screen (all zombies defeated) and Game Over screen
- Custom pixel-art sprites with directional rendering
- Camera system 

## Requirements
- Python 3.x
- Pygame

## Setup
```bash
git clone https://github.com/Sailorship/Zombie-Survival-Game-Using-Python
pip install -r requirements.txt
python main.py
```

## Project Structure
```
main.py       # Game loop
player.py     # Player movement, attack, health
npc.py        # Zombie AI, health, removal
ui.py         # HUD, Win/Game Over screens
camera.py     # Scrolling camera
settings.py   # Constants
```