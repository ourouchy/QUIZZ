import pygame
import sys
import time
from logic import GameLogic
from ui import render_game, character_manager, common_sounds

print("Starting game initialization...")
start_time = time.time()

print("Initializing pygame...")
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound
from config import WINDOW_WIDTH, WINDOW_HEIGHT

print("Initializing character manager and common sounds...")
# Initialize character manager and common sounds after pygame mixer
character_manager.initialize()
common_sounds.initialize()

print("Creating game window...")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Mobile Game Window")

print("Selecting random character...")
# Select a random character for this session
current_character = character_manager.select_random_character()

print("Initializing game logic...")
# Game logic
logic = GameLogic()

init_end_time = time.time()
print(f"Game initialized in {init_end_time - start_time:.2f} seconds")

# Show intro state
print("Starting intro sequence...")
game_state = 'intro'
start_time = pygame.time.get_ticks()
if current_character and 'intro' in current_character.voice_sounds:
    current_character.voice_sounds['intro'].play()
while pygame.time.get_ticks() - start_time < 4000:  # Show intro for 4 seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    render_game(screen, None, False, start_time, 0, game_state)
    pygame.display.flip()
    pygame.time.wait(16)  # Cap at ~60 FPS

# Start the game after intro
game_state = 'thinking'
logic.start(pygame.time.get_ticks())
# Select initial video for first question
character_manager.select_random_video()

running = True
while running:
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    session_end, question_end = logic.update(now)
    
    # If question ended, select a new random video for the next question
    if question_end:
        character_manager.select_random_video()
        
    current = logic.get_current()
    if session_end or not current:
        # Show bye state
        game_state = 'bye'
        if current_character and 'outro' in current_character.voice_sounds:
            current_character.voice_sounds['outro'].play()
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < 6000:  # Show bye for 6 seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
            if not running:
                break
            render_game(screen, None, False, start_time, 0, game_state)
            pygame.display.flip()
            pygame.time.wait(16)
        running = False
        break
    q, show_answer, last_switch_time = current
    
    # Update game state based on show_answer
    game_state = 'correct' if show_answer else 'thinking'
    
    # Control sounds
    if show_answer:
        if 'timer' in common_sounds.sounds:
            common_sounds.stop('timer')
        if 'answer' in common_sounds.sounds:
            if not common_sounds.sounds['answer'].get_num_channels():
                common_sounds.play('answer')
                # Play the corresponding choice sound
                correct_choice = q["answer"]
                choice_letter = chr(65 + correct_choice)  # A, B, C, D
                if current_character and choice_letter in current_character.voice_sounds:
                    current_character.voice_sounds[choice_letter].play()
    elif 'timer' in common_sounds.sounds:
        if not common_sounds.sounds['timer'].get_num_channels():
            common_sounds.play('timer')
        
    render_game(screen, q, show_answer, last_switch_time, logic.question_time, game_state)
    pygame.display.flip()

# Stop all sounds when exiting
if current_character:
    for sound in current_character.voice_sounds.values():
        sound.stop()
    for sound in common_sounds.sounds.values():
        sound.stop()
    
logic.save_used()
pygame.quit()
sys.exit() 