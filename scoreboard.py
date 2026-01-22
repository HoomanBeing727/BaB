import pygame
import json
from os.path import join
import os

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


def draw_scoreboard_table(screen, scores, start_rank, end_rank, font, title_font):
    """Draw scoreboard table for specified rank range"""
    screen.fill((245, 245, 245))  # Light gray background
        
    # Title
    title_text = "TOP SCORES LEADERBOARD"
    title_surface = title_font.render(title_text, True, (50, 50, 50))
    title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 60))
    screen.blit(title_surface, title_rect)
    
    # Subtitle (which ranks)
    if start_rank == 1:
        subtitle = "Top 10 Players"
    else:
        subtitle = f"Ranks {start_rank}-{end_rank}"
    
    subtitle_surface = font.render(subtitle, True, (80, 80, 80))
    subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, 120))
    screen.blit(subtitle_surface, subtitle_rect)
    
    # Table headers
    header_y = 180
    header_font = pygame.font.Font(None, 32)
    
    col_rank_x = 150
    col_name_x = 300
    col_score_x = 750
    col_build_x = 1100
    
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
    pygame.draw.line(screen, (100, 100, 100), (100, header_y + 40), (WINDOW_WIDTH - 100, header_y + 40), 2)
    
    # Draw scores
    row_height = 75
    row_start_y = header_y + 60
    row_font = pygame.font.Font(None, 28)
    
    # Get scores for this screen
    displayed_scores = scores[start_rank-1:end_rank]
    
    for idx, score_entry in enumerate(displayed_scores):
        rank = start_rank + idx
        row_y = row_start_y + idx * row_height
        
        # Alternate row colors
        if idx % 2 == 0:
            row_rect = pygame.Rect(100, row_y - 10, WINDOW_WIDTH - 200, row_height - 5)
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
        build_text = pygame.font.Font(None, 24).render(build_str, True, (80, 80, 80))
        screen.blit(build_text, (col_build_x, row_y + 2))
    
    # If no scores
    if len(displayed_scores) == 0:
        no_scores_text = font.render("No scores yet. Play to set a high score!", True, (100, 100, 100))
        no_scores_rect = no_scores_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(no_scores_text, no_scores_rect)
    
    # Footer
    footer_text = pygame.font.Font(None, 24).render(
        "Play the game to compete for the top spot!", 
        True, (120, 120, 120)
    )
    footer_rect = footer_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
    screen.blit(footer_text, footer_rect)


def create_scoreboard():
    """Create and run the scoreboard display with auto-switching screens"""
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    screen_size = pygame.display.get_window_size()
    global WINDOW_WIDTH
    global WINDOW_HEIGHT
    WINDOW_WIDTH = screen_size[0]
    WINDOW_HEIGHT = screen_size[1]

    pygame.display.set_caption("Scoreboard - Build-a-Bacteria")
    clock = pygame.time.Clock()
    
    # Fonts
    try:
        title_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 56)
        font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 36)
    except:
        title_font = pygame.font.Font(None, 56)
        font = pygame.font.Font(None, 36)
    
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
            draw_scoreboard_table(screen, scores, 1, 10, font, title_font)
        else:
            # Ranks 11-20
            draw_scoreboard_table(screen, scores, 11, 20, font, title_font)
        
        # Draw screen indicator dots at bottom
        dot_y = WINDOW_HEIGHT - 80
        dot_spacing = 20
        dot_radius = 8
        
        for i in range(2):
            dot_x = WINDOW_WIDTH // 2 - dot_spacing // 2 + i * dot_spacing
            if i == current_screen:
                pygame.draw.circle(screen, (70, 130, 180), (dot_x, dot_y), dot_radius)
            else:
                pygame.draw.circle(screen, (200, 200, 200), (dot_x, dot_y), dot_radius)
        
        time_remaining = int(screen_switch_interval - screen_timer)
        timer_text = str(time_remaining)
        timer_surf = pygame.font.Font(None, 24).render(timer_text, True, (120, 120, 120))
        timer_rect = timer_surf.get_rect(center = (dot_x + 40, dot_y))
        screen.blit(timer_surf, timer_rect)
        
        pygame.display.flip()
    
    pygame.quit()
