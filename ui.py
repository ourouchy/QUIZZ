import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, RED, FONT_SIZE, FONT_PATH
import math
import cv2
import numpy as np
import os
import random
import time

# Modern color palette
BACKGROUND = (245, 247, 250)  # Light gray background
CARD_COLOR = (255, 255, 255)  # White cards
PRIMARY_COLOR = (99, 102, 241)  # Indigo
SECONDARY_COLOR = (139, 92, 246)  # Purple
SUCCESS_COLOR = (34, 197, 94)  # Green
DANGER_COLOR = (239, 68, 68)  # Red
TEXT_COLOR = (31, 41, 55)  # Dark gray
LIGHT_TEXT = (107, 114, 128)  # Light gray
SHADOW_COLOR = (0, 0, 0, 30)  # Semi-transparent black
TIMER_COLOR = (168, 85, 247)  # Purple for timer
HOVER_COLOR = (243, 244, 246)  # Light hover effect

# Animation constants
ANIMATION_DURATION = 500  # milliseconds
EASING_FUNCTION = lambda x: 1 - math.pow(1 - x, 3)  # Cubic ease-out

class CommonSounds:
    def __init__(self):
        self.sounds = {}
    
    def initialize(self):
        """Initialize the common sounds after pygame mixer is initialized"""
        print("Initializing common sounds...")
        start_time = time.time()
        self.load_common_sounds()
        end_time = time.time()
        print(f"Common sounds initialized in {end_time - start_time:.2f} seconds")
    
    def load_common_sounds(self):
        """Load common sounds used by all characters"""
        common_sounds_dir = 'common_sounds'
        if os.path.exists(common_sounds_dir):
            for sound_file in os.listdir(common_sounds_dir):
                if sound_file.endswith('.mp3'):
                    sound_name = os.path.splitext(sound_file)[0]
                    sound_path = os.path.join(common_sounds_dir, sound_file)
                    print(f"Loading common sound: {sound_name}")
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(0.5)
    
    def play(self, sound_name):
        """Play a common sound"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def stop(self, sound_name):
        """Stop a common sound"""
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()

# Create common sounds instance (will be initialized later)
common_sounds = CommonSounds()

class Character:
    def __init__(self, name):
        print(f"Initializing character: {name}")
        self.name = name
        # Video frames or images for different states
        self.intro_frames = None
        self.outro_frames = None
        self.pose_frames = None  # Will store frames for the selected pose
        self.selected_pose = None  # Store the name of selected pose
        # Voice sounds (only character-specific sounds)
        self.voice_sounds = {}
        self.load_resources()
    
    def load_resources(self):
        print(f"Loading resources for character: {self.name}")
        start_time = time.time()
        
        # Load videos or images
        video_dir = f'characters/{self.name}/video'
        image_dir = f'characters/{self.name}/image'
        
        # Check if character uses videos or images
        self.uses_videos = os.path.exists(video_dir)
        self.uses_images = os.path.exists(image_dir)
        
        if self.uses_videos:
            print("Loading video resources...")
            # Load intro video
            print("Loading intro video...")
            intro_path = os.path.join(video_dir, 'intro.mp4')
            if os.path.exists(intro_path):
                self.intro_frames = self.load_video(intro_path)
                print(f"Intro video loaded: {len(self.intro_frames)} frames")
            
            # Load outro video
            print("Loading outro video...")
            outro_path = os.path.join(video_dir, 'outro.mp4')
            if os.path.exists(outro_path):
                self.outro_frames = self.load_video(outro_path)
                print(f"Outro video loaded: {len(self.outro_frames)} frames")
            
            # Select and load a random pose video
            print("Loading pose video...")
            pose_files = [f for f in os.listdir(video_dir) if f.startswith('pose') and f.endswith('.mp4')]
            if pose_files:
                selected_pose = random.choice(pose_files)
                self.selected_pose = selected_pose
                pose_path = os.path.join(video_dir, selected_pose)
                self.pose_frames = self.load_video(pose_path)
                print(f"Pose video loaded: {len(self.pose_frames)} frames")
        
        elif self.uses_images:
            print("Loading image resources...")
            # Load intro image
            print("Loading intro image...")
            intro_path = os.path.join(image_dir, 'intro.png')
            if os.path.exists(intro_path):
                self.intro_frames = [pygame.image.load(intro_path)]
                print("Intro image loaded")
            
            # Load outro image
            print("Loading outro image...")
            outro_path = os.path.join(image_dir, 'outro.png')
            if os.path.exists(outro_path):
                self.outro_frames = [pygame.image.load(outro_path)]
                print("Outro image loaded")
            
            # Load question and answer images
            print("Loading pose images...")
            question_path = os.path.join(image_dir, 'question.png')
            answer_path = os.path.join(image_dir, 'answer.png')
            if os.path.exists(question_path) and os.path.exists(answer_path):
                self.pose_frames = [
                    pygame.image.load(question_path),  # First frame for question
                    pygame.image.load(answer_path)     # Second frame for answer
                ]
                print("Pose images loaded")
        
        # Load character-specific voice sounds
        print("Loading voice sounds...")
        voice_dir = f'characters/{self.name}/voice'
        if os.path.exists(voice_dir):
            for sound_file in os.listdir(voice_dir):
                if sound_file.endswith('.mp3'):
                    sound_name = os.path.splitext(sound_file)[0]
                    sound_path = os.path.join(voice_dir, sound_file)
                    self.voice_sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.voice_sounds[sound_name].set_volume(0.5)
                    print(f"Loaded sound: {sound_name}")
        
        end_time = time.time()
        print(f"Character resources loaded in {end_time - start_time:.2f} seconds")
    
    def get_frames_for_state(self, state):
        """Get frames for a specific game state"""
        if state == 'intro':
            return self.intro_frames
        elif state == 'bye':
            return self.outro_frames
        else:  # 'thinking' or 'correct'
            if self.uses_images:
                # For images, return question image for 'thinking' and answer image for 'correct'
                return [self.pose_frames[0]] if state == 'thinking' else [self.pose_frames[1]]
            return self.pose_frames
    
    @staticmethod
    def load_video(video_path):
        """Load video and convert frames to pygame surfaces"""
        print(f"Loading video: {video_path}")
        start_time = time.time()
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to pygame surface
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            frames.append(frame)
            frame_count += 1
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"Loaded {frame_count} frames...")
        cap.release()
        end_time = time.time()
        print(f"Video loaded in {end_time - start_time:.2f} seconds")
        return frames

class CharacterManager:
    def __init__(self):
        self.characters = {}  # Will store character names only
        self.current_character = None
        self.current_video_frames = None
    
    def initialize(self):
        """Initialize the character manager after pygame mixer is initialized"""
        self.load_character_names()
    
    def load_character_names(self):
        """Load only character names from the characters directory"""
        if os.path.exists('characters'):
            for char_name in os.listdir('characters'):
                if os.path.isdir(os.path.join('characters', char_name)):
                    self.characters[char_name] = None  # Store name only, not the full character object
    
    def select_random_character(self):
        """Select a random character for the session and load its resources"""
        if self.characters:
            char_name = random.choice(list(self.characters.keys()))
            # Create and load the selected character
            self.current_character = Character(char_name)
            return self.current_character
        return None
    
    def select_random_video(self):
        """Select a random video for the current question"""
        if self.current_character:
            self.current_video_frames = self.current_character.get_frames_for_state('thinking')
            return self.current_video_frames
        return None

# Create character manager instance
character_manager = CharacterManager()

# Video constants
VIDEO_FPS = 30  # Assuming 30 FPS
FRAME_DURATION = 1000 // VIDEO_FPS
QUESTION_DURATION = 9000  # 9 seconds for question
ANSWER_DURATION = 2000   # 2 seconds for answer

def draw_rounded_rect(surface, color, rect, radius=15):
    """Draw a rounded rectangle"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_shadow(surface, rect, offset=3, blur=6):
    """Draw a subtle shadow behind a rectangle"""
    shadow_rect = pygame.Rect(rect.x + offset, rect.y + offset, rect.width, rect.height)
    shadow_surface = pygame.Surface((rect.width + blur * 2, rect.height + blur * 2), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, SHADOW_COLOR, 
                    (blur, blur, rect.width, rect.height), border_radius=15)
    surface.blit(shadow_surface, (shadow_rect.x - blur, shadow_rect.y - blur))

def create_gradient_surface(width, height, color1, color2, vertical=True):
    """Create a gradient surface"""
    surface = pygame.Surface((width, height))
    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    return surface

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def prepare_question_render(q, FONT):
    question_max_width = WINDOW_WIDTH - 100
    question_lines = wrap_text(q["question"], FONT, question_max_width)
    question_surfaces = [FONT.render(line, True, TEXT_COLOR) for line in question_lines]
    line_height = question_surfaces[0].get_height() if question_surfaces else FONT_SIZE
    question_rect_width = question_max_width + 60
    question_rect_height = len(question_surfaces) * line_height + 70
    question_rect_x = (WINDOW_WIDTH - question_rect_width) // 2
    question_rect_y = 150
    question_rect = pygame.Rect(question_rect_x, question_rect_y, question_rect_width, question_rect_height)

    # Prepare choices with better spacing and design
    choice_max_width = WINDOW_WIDTH - 120
    choice_surfaces = []
    choice_rects = []
    choice_heights = []
    choice_spacing = 20
    start_y = question_rect.bottom + 30
    for i, choice in enumerate(q["choices"]):
        lines = wrap_text(choice, FONT, choice_max_width)
        surfaces = [FONT.render(line, True, TEXT_COLOR) for line in lines]
        ch = surfaces[0].get_height() if surfaces else FONT_SIZE
        rect_height = len(surfaces) * ch + 40
        rect_width = choice_max_width + 50
        rect_x = (WINDOW_WIDTH - rect_width) // 2
        rect_y = start_y + sum(choice_heights) + i * choice_spacing
        rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
        choice_surfaces.append(surfaces)
        choice_rects.append(rect)
        choice_heights.append(rect_height)
    return question_surfaces, question_rect, line_height, choice_surfaces, choice_rects

def lerp_color(color1, color2, t):
    """Linear interpolation between two colors"""
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

def get_animation_progress(start_time, current_time):
    """Calculate animation progress with easing"""
    elapsed = current_time - start_time
    progress = min(elapsed / ANIMATION_DURATION, 1.0)
    return EASING_FUNCTION(progress)

def draw_character(screen, x, y, scale=0.5, question_start_time=None, game_state='thinking'):
    """Draw the video frame or image centered at the given position"""
    if question_start_time is None or not character_manager.current_character:
        return
        
    current_time = pygame.time.get_ticks()
    elapsed = current_time - question_start_time
    
    # Get appropriate frames based on game state
    frames = character_manager.current_character.get_frames_for_state(game_state)
    
    if frames:
        if character_manager.current_character.uses_videos:
            if game_state in ['thinking', 'correct']:
                # For question/answer states, calculate frame based on elapsed time
                if elapsed < QUESTION_DURATION + ANSWER_DURATION:
                    frame_index = int((elapsed / (QUESTION_DURATION + ANSWER_DURATION)) * len(frames))
                    frame_index = min(frame_index, len(frames) - 1)
                    frame = frames[frame_index]
                else:
                    return
            else:
                # For intro/outro, play the entire video
                frame_index = int((elapsed / 1000) * 30)  # Assuming 30 FPS
                if frame_index >= len(frames):
                    return
                frame = frames[frame_index]
        else:
            # For images, just use the first (and only) frame
            frame = frames[0]
        
        # Scale the frame if needed
        if scale != 1.0:
            new_size = (int(frame.get_width() * scale), int(frame.get_height() * scale))
            frame = pygame.transform.scale(frame, new_size)
        # Center the frame at the given position
        rect = frame.get_rect(center=(x, y))
        screen.blit(frame, rect)

def render_game(screen, current, show_answer, last_switch_time, question_time, game_state='thinking'):
    FONT = pygame.font.Font(FONT_PATH, FONT_SIZE)
    TITLE_FONT = pygame.font.Font(FONT_PATH, 32)
    DIFF_FONT = pygame.font.Font(FONT_PATH, 24)
    
    # Fill with white background
    screen.fill(WHITE)
    
    # Draw character based on game state
    if game_state == 'intro':
        draw_character(screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150, scale=0.5, 
                      question_start_time=last_switch_time, game_state='intro')
    elif game_state == 'bye':
        draw_character(screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150, scale=0.5, 
                      question_start_time=last_switch_time, game_state='bye')
    elif game_state in ['thinking', 'correct']:
        draw_character(screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100, scale=0.3, 
                      question_start_time=last_switch_time, game_state=game_state)
    
    if not current:
        # Handle intro/outro states
        if game_state == 'intro':
            title_surface = TITLE_FONT.render("Welcome to Quiz Master!", True, PRIMARY_COLOR)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(title_surface, title_rect)
        elif game_state == 'bye':
            title_surface = TITLE_FONT.render("Thanks for playing!", True, PRIMARY_COLOR)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(title_surface, title_rect)
        return
    
    q, _, _ = current, show_answer, last_switch_time
    question_surfaces, question_rect, line_height, choice_surfaces, choice_rects = prepare_question_render(q, FONT)
    
    # Draw app title/header
    title_surface = TITLE_FONT.render("Quiz Master", True, PRIMARY_COLOR)
    title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 40))
    screen.blit(title_surface, title_rect)
    
    # Draw difficulty badge with better styling
    diff_text = q["difficulty"].upper()
    diff_surface = DIFF_FONT.render(diff_text, True, WHITE)
    diff_bg_width = diff_surface.get_width() + 30
    diff_bg_height = diff_surface.get_height() + 15
    diff_bg_rect = pygame.Rect((WINDOW_WIDTH - diff_bg_width) // 2, 75, 
                              diff_bg_width, diff_bg_height)
    
    # Choose color based on difficulty
    if q["difficulty"].lower() == "easy":
        badge_color = SUCCESS_COLOR
    elif q["difficulty"].lower() == "medium":
        badge_color = (245, 158, 11)  # Orange
    else:
        badge_color = DANGER_COLOR
    
    draw_rounded_rect(screen, badge_color, diff_bg_rect, 20)
    diff_rect = diff_surface.get_rect(center=diff_bg_rect.center)
    screen.blit(diff_surface, diff_rect)
    
    # Draw question card with shadow
    draw_shadow(screen, question_rect)
    draw_rounded_rect(screen, CARD_COLOR, question_rect, 20)
    
    # Add question number indicator
    q_number = f"Question {q.get('number', '?')}"
    q_num_surface = pygame.font.Font(FONT_PATH, 16).render(q_number, True, LIGHT_TEXT)
    q_num_rect = q_num_surface.get_rect()
    q_num_rect.x = question_rect.x + 20
    q_num_rect.y = question_rect.y + 15
    screen.blit(q_num_surface, q_num_rect)
    
    # Draw question text
    for i, surf in enumerate(question_surfaces):
        line_rect = surf.get_rect()
        line_rect.centerx = question_rect.centerx
        line_rect.y = question_rect.y + 45 + i * line_height
        screen.blit(surf, line_rect)
    
    # Get current time for animations
    current_time = pygame.time.get_ticks()
    
    # Draw choice cards with modern styling and animations
    for i, rect in enumerate(choice_rects):
        # Draw shadow first
        draw_shadow(screen, rect)
        
        # Calculate animation progress for this choice
        if show_answer and i == q["answer"]:
            anim_progress = get_animation_progress(last_switch_time, current_time)
            
            # Animate the background color
            start_color = CARD_COLOR
            end_color = SUCCESS_COLOR
            current_color = lerp_color(start_color, end_color, anim_progress)
            
            # Animate the scale
            scale = 1.0 + 0.05 * anim_progress  # Subtle scale up
            scaled_rect = pygame.Rect(
                rect.x - (rect.width * (scale - 1)) / 2,
                rect.y - (rect.height * (scale - 1)) / 2,
                rect.width * scale,
                rect.height * scale
            )
            
            # Draw the animated background
            draw_rounded_rect(screen, current_color, scaled_rect, 15)
            
        else:
            # Normal choice - white with subtle border
            draw_rounded_rect(screen, CARD_COLOR, rect, 15)
            if not show_answer:
                pygame.draw.rect(screen, (229, 231, 235), rect, 2, border_radius=15)
        
        # Choice letter (A, B, C, D)
        choice_letter = chr(65 + i)  # A, B, C, D
        letter_font = pygame.font.Font(FONT_PATH, 18)
        
        if show_answer and i == q["answer"]:
            letter_surface = letter_font.render(choice_letter, True, WHITE)
            letter_bg_color = lerp_color((237, 233, 254), (22, 163, 74), anim_progress)
        else:
            letter_surface = letter_font.render(choice_letter, True, PRIMARY_COLOR)
            letter_bg_color = (237, 233, 254)
        
        letter_bg_size = 30
        letter_bg_rect = pygame.Rect(rect.x + 15, rect.y + (rect.height - letter_bg_size) // 2, letter_bg_size, letter_bg_size)
        draw_rounded_rect(screen, letter_bg_color, letter_bg_rect, 15)
        
        letter_rect = letter_surface.get_rect(center=letter_bg_rect.center)
        screen.blit(letter_surface, letter_rect)
        
        # Draw choice text with animation
        for j, surf in enumerate(choice_surfaces[i]):
            if show_answer and i == q["answer"]:
                # Animate text color
                text_color = lerp_color(TEXT_COLOR, WHITE, anim_progress)
                original_text = q["choices"][i]
                lines = wrap_text(original_text, FONT, WINDOW_WIDTH - 120)
                if j < len(lines):
                    surf = FONT.render(lines[j], True, text_color)
            else:
                # Fix: Get the original text and re-render it
                original_text = q["choices"][i]
                lines = wrap_text(original_text, FONT, WINDOW_WIDTH - 120)
                if j < len(lines):
                    surf = FONT.render(lines[j], True, TEXT_COLOR)
            
            line_rect = surf.get_rect()
            line_rect.x = rect.x + 60  # Offset for the letter circle
            line_rect.y = rect.y + 20 + j * surf.get_height()
            screen.blit(surf, line_rect)
    
    # Draw modern timer bar (only during question, not answer)
    now = pygame.time.get_ticks()
    elapsed = now - last_switch_time
    if not show_answer:
        progress = max(0, 1 - elapsed / question_time)
        timer_width = int(progress * (WINDOW_WIDTH - 40))
        
        # Timer background
        timer_bg_rect = pygame.Rect(20, WINDOW_HEIGHT - 40, WINDOW_WIDTH - 40, 8)
        draw_rounded_rect(screen, (229, 231, 235), timer_bg_rect, 4)
        
        # Timer progress with gradient
        if timer_width > 0:
            timer_rect = pygame.Rect(20, WINDOW_HEIGHT - 40, timer_width, 8)
            if progress > 0.5:
                color = SUCCESS_COLOR
            elif progress > 0.25:
                color = (245, 158, 11)  # Orange
            else:
                color = DANGER_COLOR
            draw_rounded_rect(screen, color, timer_rect, 4)
        
        # Timer text
        time_left = max(0, question_time - elapsed) // 1000
        timer_text = f"{time_left}s"
        timer_surface = pygame.font.Font(FONT_PATH, 16).render(timer_text, True, LIGHT_TEXT)
        timer_text_rect = timer_surface.get_rect()
        timer_text_rect.centerx = WINDOW_WIDTH // 2
        timer_text_rect.y = WINDOW_HEIGHT - 25
        screen.blit(timer_surface, timer_text_rect)
    
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
                if character_manager.current_character and choice_letter in character_manager.current_character.voice_sounds:
                    character_manager.current_character.voice_sounds[choice_letter].play()
    elif 'timer' in common_sounds.sounds:
        if not common_sounds.sounds['timer'].get_num_channels():
            common_sounds.play('timer') 