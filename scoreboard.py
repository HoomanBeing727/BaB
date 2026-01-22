import pygame
import json
from os.path import join
import os

# ============================================================================
# SCREEN SCALER
# ============================================================================

class ScreenScaler:
    """Handles responsive scaling for different screen sizes"""
    
    def __init__(self, screen_width, screen_height, reference_width=1920, reference_height=1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reference_width = reference_width
        self.reference_height = reference_height
        
        self.width_scale = screen_width / reference_width
        self.height_scale = screen_height / reference_height
        self.uniform_scale = min(self.width_scale, self.height_scale)
    
    def scale_width(self, value, min_val=None, max_val=None):
        """Scale a width value proportionally"""
        scaled = int(value * self.width_scale)
        if min_val is not None: 
            scaled = max(scaled, min_val)
        if max_val is not None: 
            scaled = min(scaled, max_val)
        return scaled
    
    def scale_height(self, value, min_val=None, max_val=None):
        """Scale a height value proportionally"""
        scaled = int(value * self.height_scale)
        if min_val is not None: 
            scaled = max(scaled, min_val)
        if max_val is not None: 
            scaled = min(scaled, max_val)
        return scaled
    
    def scale_uniform(self, value, min_val=None, max_val=None):
        """Scale maintaining aspect ratio (uses minimum of width/height scale)"""
        scaled = int(value * self.uniform_scale)
        if min_val is not None: 
            scaled = max(scaled, min_val)
        if max_val is not None: 
            scaled = min(scaled, max_val)
        return scaled
    
    def scale_font(self, size, min_size=16):
        """Scale font size with readability minimum"""
        return max(int(size * self.uniform_scale), min_size)

# ============================================================================
# SCOREBOARD DISPLAY
# ============================================================================

def load_scores():
    """Load scores from data.json"""
    try:
        with open('data.json', 'r') as f:
            scores = json.load(f)
        # Ensure it's sorted by score (highest first)
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def draw_scoreboard_table(screen, scores, start_rank, end_rank, font, title_font, scaler, window_width, window_height):
    """Draw scoreboard table for specified rank range"""
    screen.fill((245, 245, 245))  # Light gray background
        
    # Title
    title_text = "TOP SCORES LEADERBOARD"
    title_surface = title_font.render(title_text, True, (50, 50, 50))
    title_rect = title_surface.get_rect(center=(window_width // 2, scaler.scale_height(60, min_val=40)))
    screen.blit(title_surface, title_rect)
    
    # Subtitle (which ranks)
    if start_rank == 1:
        subtitle = "Top 10 Players"
    else:
        subtitle = f"Ranks {start_rank}-{end_rank}"
    
    subtitle_surface = font.render(subtitle, True, (80, 80, 80))
    subtitle_rect = subtitle_surface.get_rect(center=(window_width // 2, scaler.scale_height(120, min_val=80)))
    screen.blit(subtitle_surface, subtitle_rect)
    
    # Table headers
    header_y = scaler.scale_height(180, min_val=120)
    header_font = pygame.font.Font(None, scaler.scale_font(32, min_size=20))
    
    col_rank_x = scaler.scale_width(150, min_val=80)
    col_name_x = scaler.scale_width(300, min_val=150)
    col_score_x = scaler.scale_width(750, min_val=400)
    col_build_x = scaler.scale_width(1100, min_val=600)
    
    headers = [
        ("Rank", col_rank_x),
        ("Name", col_name_x),
        ("Score", col_score_x),
        ("Build", col_build_x)
    ]
    
    for text, x in headers:
        header_text = header_font.render(text, True, (50, 50, 50))
        screen.blit(header_text, (x, header_y))
    
    # Draw header underline
    pygame.draw.line(screen, (100, 100, 100), (scaler.scale_width(100, min_val=50), header_y + scaler.scale_height(40, min_val=30)), (window_width - scaler.scale_width(100, min_val=50), header_y + scaler.scale_height(40, min_val=30)), 2)
    
    # Draw scores
    row_height = scaler.scale_height(75, min_val=50)
    row_start_y = header_y + scaler.scale_height(60, min_val=45)
    row_font = pygame.font.Font(None, scaler.scale_font(28, min_size=18))
    
    # Get scores for this screen
    displayed_scores = scores[start_rank-1:end_rank]
    
    for idx, score_entry in enumerate(displayed_scores):
        rank = start_rank + idx
        row_y = row_start_y + idx * row_height
        
        # Alternate row colors
        if idx % 2 == 0:
            row_rect = pygame.Rect(scaler.scale_width(100, min_val=50), row_y - scaler.scale_height(10, min_val=5), window_width - scaler.scale_width(200, min_val=100), row_height - scaler.scale_height(5, min_val=3))
            pygame.draw.rect(screen, (255, 255, 255), row_rect)
        
        # Rank
        rank_text = row_font.render(str(rank), True, (50, 50, 50))
        screen.blit(rank_text, (col_rank_x, row_y))
        
        # Name
        name = score_entry.get('name', 'Anonymous')
        name_text = row_font.render(name[:30], True, (50, 50, 50))  # Truncate to 30 chars
        screen.blit(name_text, (col_name_x, row_y))
        
        # Score
        score = score_entry.get('score', 0)
        score_text = row_font.render(str(score), True, (50, 50, 50))
        screen.blit(score_text, (col_score_x, row_y))
        
        # Build summary
        gameplay = score_entry.get('gameplay_circuits', {})
        life_promoter = gameplay.get('life', {}).get('promoter_strength', 'N/A')
        speed_promoter = gameplay.get('speed', {}).get('promoter_strength', 'N/A')
        small_promoter = gameplay.get('small', {}).get('promoter_strength', 'N/A')
        
        # Convert to stats
        lives_map = {'weak': 1, 'medium': 2, 'strong': 3}
        speed_map = {'weak': '70%', 'medium': '100%', 'strong': '130%'}
        size_map = {'weak': '130%', 'medium': '100%', 'strong': '70%'}
        
        lives = lives_map.get(life_promoter)
        speed = speed_map.get(speed_promoter)
        size = size_map.get(small_promoter)
        
        build_str = f"Life Gene: {lives}      Speed Gene: {speed}      Small Gene: {size}"
        build_text = pygame.font.Font(None, scaler.scale_font(24, min_size=16)).render(build_str, True, (80, 80, 80))
        screen.blit(build_text, (col_build_x, row_y + 2))
    
    # If no scores
    if len(displayed_scores) == 0:
        no_scores_text = font.render("No scores yet. Play to set a high score!", True, (100, 100, 100))
        no_scores_rect = no_scores_text.get_rect(center=(window_width // 2, window_height // 2))
        screen.blit(no_scores_text, no_scores_rect)
    
    # Footer
    footer_text = pygame.font.Font(None, scaler.scale_font(24, min_size=16)).render(
        "Play the game to compete for the top spot!", 
        True, (120, 120, 120)
    )
    footer_rect = footer_text.get_rect(center=(window_width // 2, window_height - scaler.scale_height(50, min_val=30)))
    screen.blit(footer_text, footer_rect)


def create_scoreboard():
    """Create and run the scoreboard display with auto-switching screens"""
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    screen_size = pygame.display.get_window_size()
    WINDOW_WIDTH = screen_size[0]
    WINDOW_HEIGHT = screen_size[1]
    
    # Create the screen scaler
    scaler = ScreenScaler(WINDOW_WIDTH, WINDOW_HEIGHT, reference_width=1920, reference_height=1080)

    pygame.display.set_caption("Scoreboard - Build-a-Bacteria")
    clock = pygame.time.Clock()
    
    # Fonts - now scaled
    try:
        title_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), scaler.scale_font(56, min_size=32))
        font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), scaler.scale_font(36, min_size=22))
    except:
        title_font = pygame.font.Font(None, scaler.scale_font(56, min_size=32))
        font = pygame.font.Font(None, scaler.scale_font(36, min_size=22))
    
    # Track file modification time
    last_modified = 0
    if os.path.exists('data.json'):
        last_modified = os.path.getmtime('data.json')
    
    # Load initial scores
    scores = load_scores()
    
    # Screen switching
    current_screen = 0  # 0 = ranks 1-10, 1 = ranks 11-20
    screen_switch_interval = 30.0  # 30 seconds
    screen_timer = 0.0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Check for file updates every 5 seconds
        if pygame.time.get_ticks() % 5000 < 50:  # Approximate every 5 seconds
            if os.path.exists('data.json'):
                current_modified = os.path.getmtime('data.json')
                if current_modified > last_modified:
                    last_modified = current_modified
                    scores = load_scores()
        
        # Auto-switch screens
        screen_timer += dt
        if screen_timer >= screen_switch_interval:
            current_screen = 1 - current_screen  # Toggle between 0 and 1
            screen_timer = 0.0          
        
        # Draw current screen
        if current_screen == 0:
            # Ranks 1-10
            draw_scoreboard_table(screen, scores, 1, 10, font, title_font, scaler, WINDOW_WIDTH, WINDOW_HEIGHT)
        else:
            # Ranks 11-20
            draw_scoreboard_table(screen, scores, 11, 20, font, title_font, scaler, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Draw screen indicator dots at bottom
        dot_y = WINDOW_HEIGHT - scaler.scale_height(80, min_val=50)
        dot_spacing = scaler.scale_width(20, min_val=15)
        dot_radius = scaler.scale_uniform(8, min_val=5)
        
        for i in range(2):
            dot_x = WINDOW_WIDTH // 2 - dot_spacing // 2 + i * dot_spacing
            if i == current_screen:
                pygame.draw.circle(screen, (70, 130, 180), (dot_x, dot_y), dot_radius)
            else:
                pygame.draw.circle(screen, (200, 200, 200), (dot_x, dot_y), dot_radius)
        
        time_remaining = int(screen_switch_interval - screen_timer)
        timer_text = str(time_remaining)
        timer_surf = pygame.font.Font(None, scaler.scale_font(24, min_size=16)).render(timer_text, True, (120, 120, 120))
        timer_rect = timer_surf.get_rect(center = (dot_x + scaler.scale_width(40, min_val=25), dot_y))
        screen.blit(timer_surf, timer_rect)
        
        pygame.display.flip()
    
    pygame.quit()
