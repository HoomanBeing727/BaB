from settings import * 
from biology import Circuit, Bacteria
import json
import math
import random
import os

# ============================================================================
# SMALL BACTERIA SPRITE FOR PLATE DISPLAY
# ============================================================================

class SmallBacteriaSprite:
    """Small bacteria sprite for the plate display - fits 100+ on screen"""
    
    def __init__(self, x, y, circuits, bacteria_id):
        self.x = x
        self.y = y
        self.bacteria_id = bacteria_id
        self.size = 70  # Larger size for better visibility of surface patterns
        
        # Create bacteria and apply circuits
        self.bacteria = Bacteria()
        circuits['shape'].express(self.bacteria)
        circuits['surface'].express(self.bacteria)
        circuits['color'].express(self.bacteria)
        
        # Create surface for rendering
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.shape_rect = None  # Will be set during rendering
        
        # Render the bacteria
        self._render()
        
        # Create mask for collision detection
        self.mask = pygame.mask.from_surface(self.surface)
    
    def _render(self):
        """Render the bacteria"""
        self.surface.fill((0, 0, 0, 0))
        
        visual = self.bacteria.get_visual_properties()
        
        # Get color
        color_hex = visual['color']['hex']
        color_intensity = visual['color']['intensity']
        base_color = self._hex_to_rgb(color_hex)
        final_color = self._modulate_color(base_color, color_intensity)
        
        # Draw shape
        shape_type = visual['shape']['type']
        shape_intensity = visual['shape']['intensity']
        
        if shape_type == 'spherical':
            self._draw_sphere(final_color, shape_intensity)
        else:
            self._draw_rod(final_color, shape_intensity)
        
        # Draw surface texture
        surface_type = visual['surface']['type']
        surface_intensity = visual['surface']['intensity']
        self._draw_surface_texture(surface_type, surface_intensity)
    
    def _draw_sphere(self, color, expression):
        """Draw circular bacteria"""
        center = (self.size // 2, self.size // 2)
        base_radius = int(self.size * 0.35)
        radius = int(base_radius * (0.7 + 0.3 * expression))
        
        pygame.draw.circle(self.surface, color, center, radius)
        
        # Store bounds
        self.shape_rect = pygame.Rect(
            center[0] - radius, center[1] - radius,
            radius * 2, radius * 2
        )
    
    def _draw_rod(self, color, expression):
        """Draw rod-shaped bacteria"""
        center_x = self.size // 2
        center_y = self.size // 2
        
        width = int(self.size * 0.25)
        height_ratio = 1.5 + 1.5 * expression
        height = int(width * height_ratio)
        
        rect = pygame.Rect(
            center_x - width // 2,
            center_y - height // 2,
            width,
            height
        )
        pygame.draw.rect(self.surface, color, rect, border_radius=width // 2)
        self.shape_rect = rect
    
    def _draw_surface_texture(self, surface_type, surface_intensity):
        """Draw surface texture - simplified for small bacteria"""
        if surface_type == 'smooth' or self.shape_rect is None:
            return
        
        rect = self.shape_rect
        center_x = rect.centerx
        center_y = rect.centery
        is_circular = abs(rect.width - rect.height) < 5
        
        dot_color = (0, 0, 0, 150)
        spike_color = (50, 50, 50)
        
        if surface_type == 'rough':
            if is_circular:
                # More dots for better visibility
                num_dots = 10
                radius = rect.width // 2
                
                for i in range(num_dots):
                    angle = (i / num_dots) * 2 * math.pi
                    dot_x = int(center_x + radius * math.cos(angle))
                    dot_y = int(center_y + radius * math.sin(angle))
                    pygame.draw.circle(self.surface, dot_color, (dot_x, dot_y), 2)  # Larger dots
            else:
                # More dots for rod
                num_dots = 14
                half_width = rect.width // 2
                straight_length = rect.height - rect.width
                cap_circumference = math.pi * half_width
                total_perimeter = 2 * straight_length + 2 * cap_circumference
                
                for i in range(num_dots):
                    distance = (i / num_dots) * total_perimeter
                    
                    if distance < straight_length:
                        dot_x = rect.left
                        dot_y = rect.top + half_width + (distance / straight_length) * straight_length
                    elif distance < straight_length + cap_circumference:
                        cap_distance = distance - straight_length
                        angle = math.pi + (cap_distance / cap_circumference) * math.pi
                        dot_x = center_x + half_width * math.cos(angle)
                        dot_y = rect.top + half_width + half_width * math.sin(angle)
                    elif distance < 2 * straight_length + cap_circumference:
                        side_distance = distance - straight_length - cap_circumference
                        dot_x = rect.right
                        dot_y = rect.top + half_width + straight_length - (side_distance / straight_length) * straight_length
                    else:
                        cap_distance = distance - 2 * straight_length - cap_circumference
                        angle = (cap_distance / cap_circumference) * math.pi
                        dot_x = center_x + half_width * math.cos(angle)
                        dot_y = rect.bottom - half_width + half_width * math.sin(angle)
                    
                    pygame.draw.circle(self.surface, dot_color, (int(dot_x), int(dot_y)), 2)  # Larger dots
        
        elif surface_type == 'spiky':
            spike_length = 8  # Longer spikes for better visibility
            
            if is_circular:
                num_spikes = 10  # More spikes
                radius = rect.width // 2
                
                for i in range(num_spikes):
                    angle = (i / num_spikes) * 2 * math.pi
                    base_x = int(center_x + radius * math.cos(angle))
                    base_y = int(center_y + radius * math.sin(angle))
                    tip_x = int(base_x + spike_length * math.cos(angle))
                    tip_y = int(base_y + spike_length * math.sin(angle))
                    pygame.draw.line(self.surface, spike_color, (base_x, base_y), (tip_x, tip_y), 2)  # Thicker lines
            else:
                # More spikes for rod
                num_spikes = 12
                half_width = rect.width // 2
                straight_length = rect.height - rect.width
                cap_circumference = math.pi * half_width
                total_perimeter = 2 * straight_length + 2 * cap_circumference
                
                for i in range(num_spikes):
                    distance = (i / num_spikes) * total_perimeter
                    
                    if distance < straight_length:
                        progress = distance / straight_length
                        base_x = rect.left
                        base_y = rect.top + half_width + progress * straight_length
                        tip_x = base_x - spike_length
                        tip_y = base_y
                    elif distance < straight_length + cap_circumference:
                        cap_distance = distance - straight_length
                        angle = math.pi + (cap_distance / cap_circumference) * math.pi
                        base_x = center_x + half_width * math.cos(angle)
                        base_y = rect.top + half_width + half_width * math.sin(angle)
                        tip_x = base_x + spike_length * math.cos(angle)
                        tip_y = base_y + spike_length * math.sin(angle)
                    elif distance < 2 * straight_length + cap_circumference:
                        side_distance = distance - straight_length - cap_circumference
                        progress = side_distance / straight_length
                        base_x = rect.right
                        base_y = rect.top + half_width + straight_length - progress * straight_length
                        tip_x = base_x + spike_length
                        tip_y = base_y
                    else:
                        cap_distance = distance - 2 * straight_length - cap_circumference
                        angle = (cap_distance / cap_circumference) * math.pi
                        base_x = center_x + half_width * math.cos(angle)
                        base_y = rect.bottom - half_width + half_width * math.sin(angle)
                        tip_x = base_x + spike_length * math.cos(angle)
                        tip_y = base_y + spike_length * math.sin(angle)
                    
                    pygame.draw.line(self.surface, spike_color,
                                   (int(base_x), int(base_y)),
                                   (int(tip_x), int(tip_y)), 2)  # Thicker lines
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _modulate_color(self, color, expression):
        """Modulate color brightness"""
        return tuple(int(c * expression) for c in color)
    
    def get_rect(self):
        """Get collision rect"""
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        """Draw bacteria to screen"""
        screen.blit(self.surface, (self.x, self.y))


# ============================================================================
# COLLISION DETECTION & PLACEMENT
# ============================================================================

def find_non_overlapping_position(existing_bacteria, screen_width, screen_height, max_attempts=100):
    """Find a position that doesn't overlap with existing bacteria"""
    margin = 50  # Keep away from edges
    top_margin = 150  # Space for header
    bacteria_size = 70  # Match the new bacteria size
    
    for attempt in range(max_attempts):
        # Random position
        x = random.randint(margin, screen_width - bacteria_size - margin)
        y = random.randint(top_margin, screen_height - bacteria_size - margin)
        
        # Check for overlaps
        new_rect = pygame.Rect(x, y, bacteria_size, bacteria_size)
        overlaps = False
        
        for bacteria in existing_bacteria:
            if new_rect.colliderect(bacteria.get_rect()):
                overlaps = True
                break
        
        if not overlaps:
            return (x, y)
    
    # If we can't find a spot, return None
    return None


def load_bacteria_from_json():
    """Load all bacteria from data.json"""
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ============================================================================
# PAGE AUTO-TRANSITION TIMER
# ============================================================================

# Time between page transitions in seconds
PAGE_TRANSITION_INTERVAL = 60.0


# ============================================================================
# MAIN PLATE DISPLAY WITH AUTO-CYCLING GALLERY
# ============================================================================

def create_platedisplay():
    """Create and run the plate display window with auto-cycling multi-page gallery"""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bacteria Plate Display - Gallery")
    clock = pygame.time.Clock()
    
    # Store bacteria sprites organized by pages
    # Each page is a list of bacteria sprites
    pages = [[]]  # Start with one empty page
    current_page = 0
    
    # Track last modification time of data.json to detect updates
    last_modified = 0
    
    # Timer for auto-cycling pages
    page_timer = 0.0  # Time elapsed on current page (in seconds)
    
    # Load initial bacteria
    bacteria_data_list = load_bacteria_from_json()
    for idx, bacteria_data in enumerate(bacteria_data_list):
        # Reconstruct circuits
        circuits = {
            'shape': Circuit.from_dict(bacteria_data['shape_circuit']),
            'surface': Circuit.from_dict(bacteria_data['surface_circuit']),
            'color': Circuit.from_dict(bacteria_data['color_circuit'])
        }
        
        # Try to place on current page
        current_page_bacteria = pages[current_page]
        pos = find_non_overlapping_position(current_page_bacteria, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        if pos:
            # Found space on current page
            bacteria = SmallBacteriaSprite(pos[0], pos[1], circuits, idx)
            pages[current_page].append(bacteria)
        else:
            # Current page full, create new page
            pages.append([])
            current_page += 1
            
            # Try again on new page
            pos = find_non_overlapping_position(pages[current_page], WINDOW_WIDTH, WINDOW_HEIGHT)
            if pos:
                bacteria = SmallBacteriaSprite(pos[0], pos[1], circuits, idx)
                pages[current_page].append(bacteria)
    
    # Reset to first page for viewing
    current_page = 0
    
    # Update last modified time
    if os.path.exists('data.json'):
        last_modified = os.path.getmtime('data.json')
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Auto-cycle pages if there are multiple pages
        if len(pages) > 1:
            page_timer += dt
            
            if page_timer >= PAGE_TRANSITION_INTERVAL:
                # Move to next page (loop back to first after last)
                current_page = (current_page + 1) % len(pages)
                page_timer = 0.0
        
        # Check if data.json has been updated
        if os.path.exists('data.json'):
            current_modified = os.path.getmtime('data.json')
            if current_modified > last_modified:
                # File was updated, reload bacteria
                last_modified = current_modified
                
                bacteria_data_list = load_bacteria_from_json()
                
                # Calculate total bacteria already displayed
                total_existing = sum(len(page) for page in pages)
                
                # Only add NEW bacteria (not already displayed)
                for idx in range(total_existing, len(bacteria_data_list)):
                    bacteria_data = bacteria_data_list[idx]
                    
                    # Reconstruct circuits
                    circuits = {
                        'shape': Circuit.from_dict(bacteria_data['shape_circuit']),
                        'surface': Circuit.from_dict(bacteria_data['surface_circuit']),
                        'color': Circuit.from_dict(bacteria_data['color_circuit'])
                    }
                    
                    # Try to place on last page
                    last_page_idx = len(pages) - 1
                    pos = find_non_overlapping_position(pages[last_page_idx], WINDOW_WIDTH, WINDOW_HEIGHT)
                    
                    if pos:
                        # Found space on last page
                        bacteria = SmallBacteriaSprite(pos[0], pos[1], circuits, idx)
                        pages[last_page_idx].append(bacteria)
                    else:
                        # Last page full, create new page
                        pages.append([])
                        last_page_idx += 1
                        
                        # Place on new page
                        pos = find_non_overlapping_position(pages[last_page_idx], WINDOW_WIDTH, WINDOW_HEIGHT)
                        if pos:
                            bacteria = SmallBacteriaSprite(pos[0], pos[1], circuits, idx)
                            pages[last_page_idx].append(bacteria)
        
        # Draw everything
        screen.fill((240, 235, 220))  # Petri dish color (light beige)
        
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render("Bacteria Plate Display - Gallery", True, (50, 50, 50))
        screen.blit(title, (50, 30))
        
        # Draw page info
        count_font = pygame.font.Font(None, 32)
        
        # Total bacteria count
        total_bacteria = sum(len(page) for page in pages)
        count_text = count_font.render(f"How Many Bacteria Have Been Built?: {total_bacteria}", True, (80, 80, 80))
        screen.blit(count_text, (50, 85))
        
        # Draw bacteria on current page
        for bacteria in pages[current_page]:
            bacteria.draw(screen)
        
        # Draw page indicator at bottom (only if multiple pages)
        if len(pages) > 1:
            page_indicator = count_font.render(
                f"Page {current_page + 1} / {len(pages)}", 
                True, (100, 100, 100)
            )
            indicator_rect = page_indicator.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
            screen.blit(page_indicator, indicator_rect)
        
        pygame.display.flip()
    
    pygame.quit()
