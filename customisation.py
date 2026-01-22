import pygame
from biology import Circuit, Bacteria, Promoter, ShapeCDS, SurfaceCDS, ColorCDS, LifeCDS, SpeedCDS, SmallCDS
import json
import math
from os.path import join
from random import randint, uniform, choice
from datetime import datetime

# Game States
CUSTOMISATION = 0
GAME = 1
GAMEOVER = 2
THANKYOU = 3



# ============================================================================
# UI COMPONENTS
# ============================================================================

class ArrowSelector:
    """Arrow-based selector with left/right arrows using images"""
    
    # Class variable: load arrow images once for all instances
    _arrow_images = None
    
    @classmethod
    def _load_arrow_images(cls):
        """Load and prepare arrow images (called once)"""
        if cls._arrow_images is None:
            # Load the original arrow image
            arrow_img = pygame.image.load(join('images', 'arrow.png')).convert_alpha()
            
            # Scale it down to fit in button (30x30 pixels for example)
            arrow_size = 30
            arrow_img = pygame.transform.scale(arrow_img, (arrow_size, arrow_size))
            
            # Create right arrow (original direction)
            right_arrow = arrow_img
            
            # Create left arrow (flip horizontally)
            left_arrow = pygame.transform.flip(arrow_img, True, False)
            
            cls._arrow_images = {
                'left': left_arrow,
                'right': right_arrow
            }
    
    def __init__(self, x, y, width, height, options, selected_index=0):
        # Load arrow images if not already loaded
        ArrowSelector._load_arrow_images()
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected_index = selected_index
        self.font = pygame.font.Font(None, 28)
        
        # Arrow button size
        self.arrow_width = 40
        
        # Create arrow button rects
        self.left_arrow_rect = pygame.Rect(x, y, self.arrow_width, height)
        self.right_arrow_rect = pygame.Rect(x + width - self.arrow_width, y, self.arrow_width, height)
        self.display_rect = pygame.Rect(x + self.arrow_width, y, 
                                        width - 2 * self.arrow_width, height)
    
    def get_selected(self):
        return self.options[self.selected_index]
    
    def handle_event(self, event):
        """Returns True if selection changed."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Check left arrow click
            if self.left_arrow_rect.collidepoint(pos):
                if self.selected_index > 0:
                    self.selected_index -= 1
                    return True
            
            # Check right arrow click
            elif self.right_arrow_rect.collidepoint(pos):
                if self.selected_index < len(self.options) - 1:
                    self.selected_index += 1
                    return True
        
        return False
    
    def draw(self, screen):
        # Ensure images are loaded
        if ArrowSelector._arrow_images is None:
            ArrowSelector._load_arrow_images()
        
        # Get images (safe after check above)
        images = ArrowSelector._arrow_images
        assert images is not None  # Type checker hint
        
        # Draw left arrow button background
        left_color = (100, 100, 100) if self.selected_index == 0 else (70, 130, 180)
        pygame.draw.rect(screen, left_color, self.left_arrow_rect, border_radius=5)
        
        # Draw left arrow image (centered in button)
        left_arrow_img = images['left']
        left_img_rect = left_arrow_img.get_rect(center=self.left_arrow_rect.center)
        screen.blit(left_arrow_img, left_img_rect)
        
        # Draw display box
        pygame.draw.rect(screen, (255, 255, 255), self.display_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.display_rect, 2)
        
        # Draw selected text (centered)
        selected_text = self.font.render(self.options[self.selected_index], True, (0, 0, 0))
        text_rect = selected_text.get_rect(center=self.display_rect.center)
        screen.blit(selected_text, text_rect)
        
        # Draw right arrow button background
        right_color = (100, 100, 100) if self.selected_index == len(self.options) - 1 else (70, 130, 180)
        pygame.draw.rect(screen, right_color, self.right_arrow_rect, border_radius=5)
        
        # Draw right arrow image (centered in button)
        right_arrow_img = images['right']
        right_img_rect = right_arrow_img.get_rect(center=self.right_arrow_rect.center)
        screen.blit(right_arrow_img, right_img_rect)


class Button:
    def __init__(self, x, y, width, height, text, elevation):
        # core attributes 
        self.rect = pygame.Rect(x, y, width, height)
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = y
        
        # Colors
        self.color_idle = (70, 130, 180)      # Steel blue
        self.color_hover = (90, 160, 210)     # Lighter blue
        self.color_pressed = (50, 110, 160)   # Darker blue
        
        # top part of button
        self.top_rect = pygame.FRect((x,y), (width,height))
        self.top_color = self.color_idle
        
        # bottom part of button
        self.bottom_rect = pygame.Rect((x,y), (width,elevation))
        self.bottom_color = 'gray'
    
        # text
        self.font = pygame.font.Font(None, 32)
        self.text_surf = self.font.render(text, True, (255,255,255))
        self.text_rect = self.text_surf.get_frect(center = self.top_rect.center)

        self.pressed = False
    
    def handle_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = self.color_hover
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elevation = True
                self.pressed = True
                self.top_color = self.color_pressed
                             
                
            else: 
                self.dynamic_elevation = self.elevation
                if self.pressed == True: 
                    self.pressed = False
                    return True
                
        else: 
            self.dynamic_elevation = self.elevation
            self.top_color = self.color_pressed
    
    def draw(self, screen):
        # elevation logic 
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center
        
        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation
        
        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius = 5)
        pygame.draw.rect(screen,self.top_color,self.top_rect, border_radius= 5)
        screen.blit(self.text_surf, self.text_rect)
        self.handle_click()

class ProgressBar:
    """Visual progress bar showing promoter strength with smooth animations"""
    
    def __init__(self, x, y, width, height, fill_color=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = 0.0  # Current displayed value (0.0 to 1.0)
        self.target_value = 0.0  # Target value to animate towards
        self.animation_speed = 0.15  # Speed of animation (0.1 = slower, 0.2 = faster)
        self.font = pygame.font.Font(None, 20)
        
        # Colors
        self.bg_color = (220, 220, 220)
        self.border_color = (150, 150, 150)
        self.fill_color = fill_color if fill_color else (70, 180, 130)  # Default green fill
        self.text_color = (50, 50, 50)
    
    def set_value(self, value):
        """Set target progress value (0.0 to 1.0) - will animate to this value"""
        self.target_value = max(0.0, min(1.0, value))
    
    def update(self):
        """Update animation - call every frame"""
        # Smoothly interpolate towards target value
        if abs(self.target_value - self.value) > 0.001:
            self.value += (self.target_value - self.value) * self.animation_speed
        else:
            self.value = self.target_value
    
    def draw(self, screen):
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect, border_radius=3)
        pygame.draw.rect(screen, self.border_color, bg_rect, 2, border_radius=3)
        
        # Draw fill (using current animated value)
        if self.value > 0:
            fill_width = int(self.width * self.value)
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=3)
        
        # Draw percentage text (showing target value for accuracy)
        percentage = int(self.target_value * 100)
        text = self.font.render(f"{percentage}%", True, self.text_color)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)


class HeartDisplay:
    """Display showing 1-3 heart icons for life gene"""
    
    def __init__(self, x, y, width, height, heart_surf):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.heart_surf = heart_surf
        self.heart_count = 1  # Default
        self.heart_size = 25  # Size in pixels
        self.heart_spacing = 5
    
    def set_lives(self, lives: int):
        """Set number of hearts (1-3)"""
        self.heart_count = max(1, min(3, lives))
    
    def draw(self, screen):
        # No background bar - just draw hearts directly
        # Calculate starting position to center hearts horizontally
        total_width = self.heart_count * self.heart_size + (self.heart_count - 1) * self.heart_spacing
        start_x = self.x + (self.width - total_width) // 2
        heart_y = self.y + (self.height - self.heart_size) // 2
        
        # Draw hearts
        for i in range(self.heart_count):
            scaled_heart = pygame.transform.scale(
                self.heart_surf, 
                (self.heart_size, self.heart_size)
            )
            x_pos = start_x + i * (self.heart_size + self.heart_spacing)
            screen.blit(scaled_heart, (x_pos, heart_y))


class CircuitStatsDisplay:
    """Display showing expression levels for all six circuits below bacteria preview"""
    
    def __init__(self, x, y, width, life_surf):
        self.x = x
        self.y = y
        self.width = width
        self.life_surf = life_surf
        
        # Fonts (smaller for 6 bars)
        self.title_font = pygame.font.Font(None, 28)
        self.label_font = pygame.font.Font(None, 25)
        self.desc_font = pygame.font.Font(None, 20)
        
        # Colors for each circuit type
        self.shape_color = (70, 180, 130)      # Green
        self.surface_color = (70, 130, 180)    # Blue
        self.color_color = (180, 100, 70)      # Orange/brown
        self.life_color = (200, 50, 50)        # Red
        self.speed_color = (50, 150, 200)      # Light blue
        self.small_color = (150, 100, 200)     # Purple
        
        # Bar dimensions (smaller for 6 bars)
        bar_width = width - 40
        bar_height = 20
        bar_spacing = 85
        
        # Create six progress bars
        bar_x = x + 20
        bar_y_start = y
        
        # Visual circuits
        self.shape_bar = ProgressBar(bar_x, bar_y_start, bar_width, bar_height, self.shape_color)
        self.shape_label_pos = (bar_x, bar_y_start - 22)
        self.shape_desc_pos = (bar_x, bar_y_start + bar_height + 3)
        
        self.surface_bar = ProgressBar(bar_x, bar_y_start + bar_spacing, bar_width, bar_height, self.surface_color)
        self.surface_label_pos = (bar_x, bar_y_start + bar_spacing - 22)
        self.surface_desc_pos = (bar_x, bar_y_start + bar_spacing + bar_height + 3)
        
        self.color_bar = ProgressBar(bar_x, bar_y_start + 2*bar_spacing, bar_width, bar_height, self.color_color)
        self.color_label_pos = (bar_x, bar_y_start + 2*bar_spacing - 22)
        self.color_desc_pos = (bar_x, bar_y_start + 2*bar_spacing + bar_height + 3)
        
        # Gameplay circuits
        self.life_display = HeartDisplay(bar_x, bar_y_start + 3*bar_spacing, bar_width, bar_height, life_surf)
        self.life_label_pos = (bar_x, bar_y_start + 3*bar_spacing - 22)
        self.life_desc_pos = (bar_x, bar_y_start + 3*bar_spacing + bar_height + 3)
        
        self.speed_bar = ProgressBar(bar_x, bar_y_start + 4*bar_spacing, bar_width, bar_height, self.speed_color)
        self.speed_label_pos = (bar_x, bar_y_start + 4*bar_spacing - 22)
        self.speed_desc_pos = (bar_x, bar_y_start + 4*bar_spacing + bar_height + 3)
        
        self.small_bar = ProgressBar(bar_x, bar_y_start + 5*bar_spacing, bar_width, bar_height, self.small_color)
        self.small_label_pos = (bar_x, bar_y_start + 5*bar_spacing - 22)
        self.small_desc_pos = (bar_x, bar_y_start + 5*bar_spacing + bar_height + 3)
        
        # Store current circuit info for descriptions
        self.shape_info = {'promoter': 'medium', 'trait': 'rod'}
        self.surface_info = {'promoter': 'medium', 'trait': 'smooth'}
        self.color_info = {'promoter': 'medium', 'trait': 'green'}
        self.life_info = {'promoter': 'weak', 'lives': 1}
        self.speed_info = {'promoter': 'medium', 'speed': 'average'}
        self.small_info = {'promoter': 'strong', 'size': 'small'}
        
        # Total height
        self.height = bar_y_start + 5*bar_spacing + bar_height + 25
    
    def update(self, circuits):
        """Update progress bars based on current circuit selections"""
        # Map promoter strength to expression level
        strength_map = {
            'weak': 0.3,
            'medium': 0.7,
            'strong': 1.0
        }
        
        # Extract info from visual circuits
        shape_circuit = circuits['shape']
        surface_circuit = circuits['surface']
        color_circuit = circuits['color']
        
        shape_promoter = shape_circuit.promoter.strength
        surface_promoter = surface_circuit.promoter.strength
        color_promoter = color_circuit.promoter.strength
        
        shape_trait = shape_circuit.cds.shape
        surface_trait = surface_circuit.cds.surface
        color_trait = color_circuit.cds.color_name
        
        # Update visual bars
        self.shape_bar.set_value(strength_map[shape_promoter])
        self.surface_bar.set_value(strength_map[surface_promoter])
        self.color_bar.set_value(strength_map[color_promoter])
        
        self.shape_info = {'promoter': shape_promoter, 'trait': shape_trait}
        self.surface_info = {'promoter': surface_promoter, 'trait': surface_trait}
        self.color_info = {'promoter': color_promoter, 'trait': color_trait}
        
        # Extract info from gameplay circuits
        life_circuit = circuits['life']
        speed_circuit = circuits['speed']
        small_circuit = circuits['small']
        
        life_promoter = life_circuit.promoter.strength
        speed_promoter = speed_circuit.promoter.strength
        small_promoter = small_circuit.promoter.strength
        
        # Calculate gameplay stats
        life_cds = life_circuit.cds
        speed_cds = speed_circuit.cds
        small_cds = small_circuit.cds
        
        lives = life_cds.get_lives_from_expression(strength_map[life_promoter])
        speed_mult = speed_cds.get_speed_multiplier(strength_map[speed_promoter])
        size_mult = small_cds.get_size_multiplier(strength_map[small_promoter])
        
        # Update gameplay displays
        # For life: set number of hearts (1-3)
        self.life_display.set_lives(lives)
        # For speed: normalize around 70-130% range
        self.speed_bar.set_value(speed_mult - 0.3)  # Maps 0.7->0, 1.0->0.5, 1.3->1.0
        # For small: invert since smaller is "better" (70% is strong)
        self.small_bar.set_value(1.6 - size_mult)  # Maps 1.3->0, 1.0->0.5, 0.7->1.0
        
        self.life_info = {'promoter': life_promoter, 'lives': lives}
        self.speed_info = {'promoter': speed_promoter, 'speed': f"{int(speed_mult * 100)}%"}
        self.small_info = {'promoter': small_promoter, 'size': f"{int(size_mult * 100)}%"}
    
    def update_animations(self):
        """Update bar animations - call every frame"""
        self.shape_bar.update()
        self.surface_bar.update()
        self.color_bar.update()
        # life_display doesn't have animations
        self.speed_bar.update()
        self.small_bar.update()
    
    def draw(self, screen):
        """Draw the circuit stats display"""
        # Draw Shape bar and labels
        shape_label = self.label_font.render("Shape Expression:", True, (50, 50, 50))
        screen.blit(shape_label, self.shape_label_pos)
        self.shape_bar.draw(screen)
        shape_desc = self.desc_font.render(
            f"({self.shape_info['promoter'].capitalize()} promoter affecting {self.shape_info['trait']} bacteria)",
            True, (100, 100, 100)
        )
        screen.blit(shape_desc, self.shape_desc_pos)
        
        # Draw Surface bar and labels
        surface_label = self.label_font.render("Surface Expression:", True, (50, 50, 50))
        screen.blit(surface_label, self.surface_label_pos)
        self.surface_bar.draw(screen)
        surface_desc = self.desc_font.render(
            f"({self.surface_info['promoter'].capitalize()} promoter showing {self.surface_info['trait']} texture)",
            True, (100, 100, 100)
        )
        screen.blit(surface_desc, self.surface_desc_pos)
        
        # Draw Color bar and labels
        color_label = self.label_font.render("Color Expression:", True, (50, 50, 50))
        screen.blit(color_label, self.color_label_pos)
        self.color_bar.draw(screen)
        color_desc = self.desc_font.render(
            f"({self.color_info['promoter'].capitalize()} promoter with {self.color_info['trait']} fluorescence)",
            True, (100, 100, 100)
        )
        screen.blit(color_desc, self.color_desc_pos)
        
        # Draw Life display and labels
        life_label = self.label_font.render("Life Gene:", True, (50, 50, 50))
        screen.blit(life_label, self.life_label_pos)
        self.life_display.draw(screen)
        life_desc = self.desc_font.render(
            f"({self.life_info['promoter'].capitalize()} promoter gives {self.life_info['lives']} live(s))",
            True, (100, 100, 100)
        )
        screen.blit(life_desc, self.life_desc_pos)
        
        # Draw Speed bar and labels
        speed_label = self.label_font.render("Speed Gene:", True, (50, 50, 50))
        screen.blit(speed_label, self.speed_label_pos)
        self.speed_bar.draw(screen)
        speed_desc = self.desc_font.render(
            f"({self.speed_info['promoter'].capitalize()} expression sets {self.speed_info['speed']} speed)",
            True, (100, 100, 100)
        )
        screen.blit(speed_desc, self.speed_desc_pos)
        
        # Draw Small bar and labels
        small_label = self.label_font.render("Small Gene:", True, (50, 50, 50))
        screen.blit(small_label, self.small_label_pos)
        self.small_bar.draw(screen)
        small_desc = self.desc_font.render(
            f"({self.small_info['promoter'].capitalize()} expression sets {self.small_info['size']} size)",
            True, (100, 100, 100)
        )
        screen.blit(small_desc, self.small_desc_pos)


class CircuitPanel:
    """Panel with horizontally arranged circuit components"""
    
    def __init__(self, x, y, width, circuit_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = 110  # Back to original height without progress bar
        self.circuit_type = circuit_type
        
        # Fonts
        self.title_font = pygame.font.Font(None, 34)
        self.label_font = pygame.font.Font(None, 26)
        
        # Colors
        self.title_color = (50, 50, 50)
        self.label_color = (80, 80, 80)
        self.bg_color = (255, 255, 255)
        self.border_color = (180, 180, 180)
        
        # Horizontal layout spacing
        selector_width = 220
        selector_height = 45
        spacing = 45
        label_width = 95
        
        # Starting position for components (after title)
        component_y = y + 50
        current_x = x + 25
        
        # Promoter selector
        self.promoter_selector = ArrowSelector(
            current_x + label_width, component_y, selector_width, selector_height,
            ['weak', 'medium', 'strong'],
            selected_index=1  # Default to 'medium'
        )
        self.promoter_label_pos = (current_x, component_y + 10)
        
        # Move to next position
        current_x += label_width + selector_width + spacing
        
        # CDS selector
        self.cds_selector = self._create_cds_selector(current_x + label_width, component_y, selector_width, selector_height)
        self.cds_label_pos = (current_x, component_y + 10)
    
    def _create_cds_selector(self, x, y, width, height):
        """Create CDS selector based on circuit type"""
        if self.circuit_type == 'shape':
            return ArrowSelector(x, y, width, height, ['rod', 'spherical'], selected_index=0)
        elif self.circuit_type == 'surface':
            return ArrowSelector(x, y, width, height, ['smooth', 'rough', 'spiky'], selected_index=0)
        elif self.circuit_type == 'color':
            return ArrowSelector(x, y, width, height, ['cyan', 'green', 'yellow', 'red', 'blue'], selected_index=1)
        else:
            raise ValueError(f"Unknown circuit type: {self.circuit_type}")
    
    def handle_event(self, event):
        """Handle events. Returns True if any selection changed."""
        changed = False
        changed |= self.promoter_selector.handle_event(event)
        changed |= self.cds_selector.handle_event(event)
        return changed
    
    def draw(self, screen):
        """Draw the circuit panel with horizontal layout"""
        # Draw background panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect, border_radius=8)
        pygame.draw.rect(screen, self.border_color, panel_rect, 2, border_radius=8)
        
        # Draw title
        title_text = f"{self.circuit_type.capitalize()} Circuit"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        screen.blit(title_surface, (self.x + 20, self.y + 10))
        
        # Draw labels
        promoter_label = self.label_font.render("Promoter:", True, self.label_color)
        screen.blit(promoter_label, self.promoter_label_pos)
        
        cds_label_text = f"{self.circuit_type.capitalize()}:" if self.circuit_type != 'shape' else "Shape:"
        cds_label = self.label_font.render(cds_label_text, True, self.label_color)
        screen.blit(cds_label, self.cds_label_pos)
        
        # Draw selectors
        self.promoter_selector.draw(screen)
        self.cds_selector.draw(screen)
    
    def build_circuit(self):
        """Build a Circuit object from current selections"""
        promoter_strength = self.promoter_selector.get_selected()
        cds_value = self.cds_selector.get_selected()
        
        promoter = Promoter(promoter_strength)
        
        if self.circuit_type == 'shape':
            cds = ShapeCDS(cds_value)
        elif self.circuit_type == 'surface':
            cds = SurfaceCDS(cds_value)
        elif self.circuit_type == 'color':
            cds = ColorCDS(cds_value)
        else:
            raise ValueError(f"Unknown circuit type: {self.circuit_type}")
        
        return Circuit(promoter, cds, self.circuit_type)


class GameplayCircuitPanel:
    """Panel for gameplay circuits with radio button promoter selection and swap logic"""
    
    def __init__(self, x, y, width, circuit_type, promoter_assignments):
        self.x = x
        self.y = y
        self.width = width
        self.height = 110
        self.circuit_type = circuit_type  # 'life', 'speed', or 'small'
        
        # Reference to shared promoter assignments dict
        # Format: {'weak': 'life', 'medium': 'speed', 'strong': 'small'}
        self.promoter_assignments = promoter_assignments
        
        # Fonts
        self.title_font = pygame.font.Font(None, 34)
        self.label_font = pygame.font.Font(None, 24)
        
        # Colors
        self.title_color = (50, 50, 50)
        self.bg_color = (255, 255, 255)
        self.border_color = (180, 180, 180)
        self.button_active_color = (70, 180, 130)
        self.button_inactive_color = (200, 200, 200)
        self.button_text_color = (50, 50, 50)
        
        # Radio button layout (3 buttons horizontally)
        button_width = 90
        button_height = 40
        button_spacing = 20
        buttons_y = y + 55
        
        # Calculate starting x to center the three buttons
        total_buttons_width = 3 * button_width + 2 * button_spacing
        buttons_start_x = x + (width - total_buttons_width) // 2
        
        # Create radio button rects
        self.weak_button = pygame.Rect(buttons_start_x, buttons_y, button_width, button_height)
        self.medium_button = pygame.Rect(buttons_start_x + button_width + button_spacing, buttons_y, button_width, button_height)
        self.strong_button = pygame.Rect(buttons_start_x + 2 * (button_width + button_spacing), buttons_y, button_width, button_height)
        
        self.buttons = {
            'weak': self.weak_button,
            'medium': self.medium_button,
            'strong': self.strong_button
        }
    
    def get_current_promoter(self):
        """Get the promoter strength currently assigned to this circuit"""
        for strength, circuit in self.promoter_assignments.items():
            if circuit == self.circuit_type:
                return strength
        return 'medium'  # Fallback
    
    def handle_event(self, event):
        """Handle click events on radio buttons. Returns True if selection changed."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            current_promoter = self.get_current_promoter()
            
            for strength, button_rect in self.buttons.items():
                if button_rect.collidepoint(pos):
                    # If clicking the already-assigned promoter, do nothing
                    if strength == current_promoter:
                        return False
                    
                    # Swap: find circuit that currently has the target strength
                    circuit_with_target = self.promoter_assignments[strength]
                    
                    # Perform the swap
                    self.promoter_assignments[strength] = self.circuit_type
                    self.promoter_assignments[current_promoter] = circuit_with_target
                    
                    return True
        
        return False
    
    def draw(self, screen):
        """Draw the gameplay circuit panel"""
        # Draw background panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect, border_radius=8)
        pygame.draw.rect(screen, self.border_color, panel_rect, 2, border_radius=8)
        
        # Draw title
        title_map = {
            'life': 'Life Circuit',
            'speed': 'Speed Circuit',
            'small': 'Small Circuit'
        }
        title_text = title_map.get(self.circuit_type, 'Gameplay Circuit')
        title_surface = self.title_font.render(title_text, True, self.title_color)
        screen.blit(title_surface, (self.x + 20, self.y + 10))
        
        # Draw radio buttons
        current_promoter = self.get_current_promoter()
        
        for strength, button_rect in self.buttons.items():
            # Determine button color based on whether it's selected
            if strength == current_promoter:
                button_color = self.button_active_color
                text_color = (255, 255, 255)
            else:
                button_color = self.button_inactive_color
                text_color = self.button_text_color
            
            # Draw button
            pygame.draw.rect(screen, button_color, button_rect, border_radius=5)
            pygame.draw.rect(screen, self.border_color, button_rect, 2, border_radius=5)
            
            # Draw button label
            label_text = strength.capitalize()
            label_surface = self.label_font.render(label_text, True, text_color)
            label_rect = label_surface.get_rect(center=button_rect.center)
            screen.blit(label_surface, label_rect)
    
    def build_circuit(self):
        """Build a Circuit object from current promoter assignment"""
        promoter_strength = self.get_current_promoter()
        promoter = Promoter(promoter_strength)
        
        if self.circuit_type == 'life':
            cds = LifeCDS()
        elif self.circuit_type == 'speed':
            cds = SpeedCDS()
        elif self.circuit_type == 'small':
            cds = SmallCDS()
        else:
            raise ValueError(f"Unknown gameplay circuit type: {self.circuit_type}")
        
        return Circuit(promoter, cds, self.circuit_type)


class BacteriaPreviewSprite:
    """Renders bacteria using pygame drawing functions with glow effect"""
    
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.base_size = size  # Store base size
        self.size = size  # Current size (will be modified by small gene)
        self.size_multiplier = 1.0  # Size multiplier from small gene
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Use Bacteria class from biology.py
        self.bacteria = Bacteria()
        
        # Store shape boundary for surface patterns
        self.shape_rect = None  # Will be set by _draw_sphere or _draw_rod
        
        # Glow effect state
        self.glow_active = False
        self.glow_timer = 0
        self.glow_duration = 500  # milliseconds
        self.glow_max_intensity = 0.6  # Maximum glow brightness (0.0 to 1.0)
    
    def update(self, circuits):
        """Update bacteria appearance based on circuits"""
        # Reset bacteria to default state
        self.bacteria.reset()
        
        # Express visual circuits on the bacteria
        circuits['shape'].express(self.bacteria)
        circuits['surface'].express(self.bacteria)
        circuits['color'].express(self.bacteria)
        
        # Get size multiplier from small gene
        small_circuit = circuits['small']
        strength_map = {'weak': 0.3, 'medium': 0.7, 'strong': 1.0}
        expression = strength_map[small_circuit.promoter.strength]
        self.size_multiplier = small_circuit.cds.get_size_multiplier(expression)
        
        # Update size and recreate surface
        self.size = int(self.base_size * self.size_multiplier)
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Re-render
        self._render()
        
        # Trigger glow effect
        self.trigger_glow()
    
    def trigger_glow(self):
        """Start the glow effect animation"""
        self.glow_active = True
        self.glow_timer = pygame.time.get_ticks()
    
    def get_glow_intensity(self):
        """Calculate current glow intensity (0.0 to 1.0)"""
        if not self.glow_active:
            return 0.0
        
        elapsed = pygame.time.get_ticks() - self.glow_timer
        
        if elapsed > self.glow_duration:
            self.glow_active = False
            return 0.0
        
        # Smooth fade in and out (bell curve-like)
        progress = elapsed / self.glow_duration
        # Use sine wave for smooth fade in and out
        intensity = math.sin(progress * math.pi) * self.glow_max_intensity
        return intensity
    
    def _render(self):
        """Render the bacteria based on current bacteria state"""
        self.surface.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Get visual properties from bacteria
        visual = self.bacteria.get_visual_properties()
        
        # Get color
        color_hex = visual['color']['hex']
        color_intensity = visual['color']['intensity']
        base_color = self._hex_to_rgb(color_hex)
        final_color = self._modulate_color(base_color, color_intensity)
        
        # Draw shape (this will set self.shape_rect)
        shape_type = visual['shape']['type']
        shape_intensity = visual['shape']['intensity']
        
        if shape_type == 'spherical':
            self._draw_sphere(final_color, shape_intensity)
        else:  # rod
            self._draw_rod(final_color, shape_intensity)
        
        # Draw surface texture using the shape_rect
        surface_type = visual['surface']['type']
        surface_intensity = visual['surface']['intensity']
        self._draw_surface_texture(surface_type, surface_intensity)
    
    def _draw_sphere(self, color, expression):
        """Draw circular bacteria and store its bounds"""
        center = (self.size // 2, self.size // 2)
        base_radius = int(self.size * 0.35)
        radius = int(base_radius * (0.7 + 0.3 * expression))
        
        pygame.draw.circle(self.surface, color, center, radius)
        
        # Store circle bounds as a rect for surface patterns
        self.shape_rect = pygame.Rect(
            center[0] - radius,
            center[1] - radius,
            radius * 2,
            radius * 2
        )
        
        if expression > 0.5:
            highlight_color = tuple(min(255, int(c * 1.3)) for c in color)
            highlight_radius = int(radius * 0.3)
            highlight_pos = (center[0] - radius // 3, center[1] - radius // 3)
            pygame.draw.circle(self.surface, highlight_color, highlight_pos, highlight_radius)
    
    def _draw_rod(self, color, expression):
        """Draw rod-shaped bacteria and store its rect"""
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
        
        # Store rect for surface patterns
        self.shape_rect = rect
        
        if expression > 0.5:
            highlight_color = tuple(min(255, int(c * 1.2)) for c in color)
            highlight_rect = pygame.Rect(
                rect.x + width // 4,
                rect.y + height // 8,
                width // 3,
                height // 4
            )
            pygame.draw.ellipse(self.surface, highlight_color, highlight_rect)
    
    def _draw_surface_texture(self, surface_type, expression):
        """Draw surface texture overlay on the shape_rect"""
        if surface_type == 'smooth' or self.shape_rect is None:
            return  # No texture for smooth
        
        dot_color = (0, 0, 0, 100)
        spike_color = (50, 50, 50)
        
        # Get rect properties
        rect = self.shape_rect
        center_x = rect.centerx
        center_y = rect.centery
        
        # Determine if shape is circular (width ~= height) or rod (height > width)
        is_circular = abs(rect.width - rect.height) < 10
        
        if surface_type == 'rough':
            if is_circular:
                # Circular pattern AROUND spherical bacteria (on the edge)
                num_dots = int(8 + 12 * expression)
                radius = rect.width // 2
                
                for i in range(num_dots):
                    angle = (i / num_dots) * 2 * math.pi
                    # Place dots ON the circle edge (radius), not inside
                    dot_x = int(center_x + radius * math.cos(angle))
                    dot_y = int(center_y + radius * math.sin(angle))
                    dot_radius = int(2 + 2 * expression)
                    pygame.draw.circle(self.surface, dot_color, (dot_x, dot_y), dot_radius)
            else:
                # Dots ALL AROUND the rod perimeter (following capsule shape with rounded caps)
                num_dots = int(15 + 25 * expression)
                
                rod_width = rect.width
                rod_height = rect.height
                half_width = rod_width // 2
                
                # Calculate perimeter segments
                straight_length = rod_height - rod_width  # Length of straight sides
                cap_circumference = math.pi * half_width  # Half circle on each end
                total_perimeter = 2 * straight_length + 2 * cap_circumference
                
                for i in range(num_dots):
                    # Position along perimeter (0 to total_perimeter)
                    distance = (i / num_dots) * total_perimeter
                    
                    # Determine which segment we're on
                    if distance < straight_length:
                        # Left side (straight)
                        progress = distance / straight_length
                        dot_x = rect.left
                        dot_y = rect.top + half_width + progress * straight_length
                        
                    elif distance < straight_length + cap_circumference:
                        # Top cap (semicircle) - curve from left to right
                        cap_distance = distance - straight_length
                        angle = math.pi + (cap_distance / cap_circumference) * math.pi
                        dot_x = center_x + half_width * math.cos(angle)
                        dot_y = rect.top + half_width + half_width * math.sin(angle)
                        
                    elif distance < 2 * straight_length + cap_circumference:
                        # Right side (straight) - going down
                        side_distance = distance - straight_length - cap_circumference
                        progress = side_distance / straight_length
                        dot_x = rect.right
                        dot_y = rect.top + half_width + straight_length - progress * straight_length
                        
                    else:
                        # Bottom cap (semicircle) - curve from right to left
                        cap_distance = distance - 2 * straight_length - cap_circumference
                        angle = (cap_distance / cap_circumference) * math.pi
                        dot_x = center_x + half_width * math.cos(angle)
                        dot_y = rect.bottom - half_width + half_width * math.sin(angle)
                    
                    dot_radius = int(2 + 2 * expression)
                    pygame.draw.circle(self.surface, dot_color, (int(dot_x), int(dot_y)), dot_radius)
        
        elif surface_type == 'spiky':
            spike_length = int(10 + 20 * expression)
            
            if is_circular:
                # Radial spikes for spherical bacteria
                num_spikes = 10
                radius = rect.width // 2
                
                for i in range(num_spikes):
                    angle = (i / num_spikes) * 2 * math.pi
                    base_distance = radius
                    
                    base_x = int(center_x + base_distance * math.cos(angle))
                    base_y = int(center_y + base_distance * math.sin(angle))
                    
                    tip_distance = base_distance + spike_length
                    tip_x = int(center_x + tip_distance * math.cos(angle))
                    tip_y = int(center_y + tip_distance * math.sin(angle))
                    
                    pygame.draw.line(self.surface, spike_color, (base_x, base_y), (tip_x, tip_y), 2)
            else:
                # Spikes ALL AROUND the rod perimeter (symmetrically distributed)
                num_spikes = 16  # Fixed even number for symmetry
                
                rod_width = rect.width
                rod_height = rect.height
                half_width = rod_width // 2
                
                # Calculate perimeter segments
                straight_length = rod_height - rod_width
                cap_circumference = math.pi * half_width
                total_perimeter = 2 * straight_length + 2 * cap_circumference
                
                for i in range(num_spikes):
                    # Position along perimeter (0 to total_perimeter)
                    distance = (i / num_spikes) * total_perimeter
                    
                    # Determine which segment and calculate spike direction
                    if distance < straight_length:
                        # Left side (straight) - spikes point left
                        progress = distance / straight_length
                        base_x = rect.left
                        base_y = rect.top + half_width + progress * straight_length
                        # Spike points perpendicular (left)
                        tip_x = base_x - spike_length
                        tip_y = base_y
                        
                    elif distance < straight_length + cap_circumference:
                        # Top cap (semicircle) - spikes radiate outward
                        cap_distance = distance - straight_length
                        angle = math.pi + (cap_distance / cap_circumference) * math.pi
                        base_x = center_x + half_width * math.cos(angle)
                        base_y = rect.top + half_width + half_width * math.sin(angle)
                        # Spike points radially outward from center
                        tip_x = base_x + spike_length * math.cos(angle)
                        tip_y = base_y + spike_length * math.sin(angle)
                        
                    elif distance < 2 * straight_length + cap_circumference:
                        # Right side (straight) - spikes point right
                        side_distance = distance - straight_length - cap_circumference
                        progress = side_distance / straight_length
                        base_x = rect.right
                        base_y = rect.top + half_width + straight_length - progress * straight_length
                        # Spike points perpendicular (right)
                        tip_x = base_x + spike_length
                        tip_y = base_y
                        
                    else:
                        # Bottom cap (semicircle) - spikes radiate outward
                        cap_distance = distance - 2 * straight_length - cap_circumference
                        angle = (cap_distance / cap_circumference) * math.pi
                        base_x = center_x + half_width * math.cos(angle)
                        base_y = rect.bottom - half_width + half_width * math.sin(angle)
                        # Spike points radially outward from center
                        tip_x = base_x + spike_length * math.cos(angle)
                        tip_y = base_y + spike_length * math.sin(angle)
                    
                    pygame.draw.line(self.surface, spike_color, 
                                   (int(base_x), int(base_y)), 
                                   (int(tip_x), int(tip_y)), 2)
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _modulate_color(self, color, expression):
        """Adjust color brightness based on expression level"""
        return tuple(int(c * expression) for c in color)
    
    def draw(self, screen):
        """Draw bacteria to screen with glow effect"""
        # Get current glow intensity
        glow_intensity = self.get_glow_intensity()
        
        # If glowing, draw glow layers first
        if glow_intensity > 0:
            # Draw multiple glow rings around bacteria for smooth effect
            glow_color = (255, 255, 200, int(50 * glow_intensity))  # Soft yellow glow
            
            # Draw 3 expanding rings for smooth glow
            for i in range(3, 0, -1):
                glow_size = int(15 * i * glow_intensity)
                glow_surface = pygame.Surface((self.size + glow_size*2, self.size + glow_size*2), pygame.SRCALPHA)
                
                # Draw semi-transparent circle for glow
                center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
                radius = self.size // 2 + glow_size
                alpha = int(30 * glow_intensity / i)  # Fade out as we go outward
                
                pygame.draw.circle(glow_surface, (*glow_color[:3], alpha), center, radius)
                
                # Blit glow layer
                glow_x = self.x - glow_size
                glow_y = self.y - glow_size
                screen.blit(glow_surface, (glow_x, glow_y))
        
        # Draw the actual bacteria on top
        screen.blit(self.surface, (self.x, self.y))


class ConfirmationMessage:
    """Temporary confirmation message"""
    
    def __init__(self):
        self.active = False
        self.timer = 0
        self.duration = 2000  # 2 seconds
        self.message = ""
        self.font = pygame.font.Font(None, 36)
        self.text_color = (0, 150, 0)
        self.bg_color = (230, 255, 230)
        self.border_color = (0, 200, 0)
    
    def show(self, message):
        """Show a confirmation message"""
        self.message = message
        self.active = True
        self.timer = pygame.time.get_ticks()
    
    def update(self):
        """Update the message timer"""
        if self.active and pygame.time.get_ticks() - self.timer > self.duration:
            self.active = False
    
    def draw(self, screen):
        """Draw the confirmation message"""
        if not self.active:
            return
        
        text_surface = self.font.render(self.message, True, self.text_color)
        padding = 20
        box_width = text_surface.get_width() + padding * 2
        box_height = text_surface.get_height() + padding * 2
        
        screen_width, screen_height = screen.get_size()
        box_x = (screen_width - box_width) // 2
        box_y = screen_height - 100
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        pygame.draw.rect(screen, self.bg_color, box_rect, border_radius=10)
        pygame.draw.rect(screen, self.border_color, box_rect, 3, border_radius=10)
        
        text_x = box_x + padding
        text_y = box_y + padding
        screen.blit(text_surface, (text_x, text_y))


class TextInput:
    """Text input component for name entry"""
    
    def __init__(self, x, y, width, height, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.max_length = max_length
        self.active = True
        self.font = pygame.font.Font(None, 36)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500  # Blink every 500ms
        
        # Colors
        self.bg_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.border_color = (100, 100, 100)
        self.border_active_color = (70, 130, 180)
    
    def handle_event(self, event):
        """Handle keyboard events for text input"""
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True  # Signal submission
            elif len(self.text) < self.max_length:
                # Add character if it's printable
                if event.unicode.isprintable():
                    self.text += event.unicode
        return False
    
    def update(self):
        """Update cursor blink animation"""
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
    
    def draw(self, screen):
        """Draw the text input box"""
        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        border_color = self.border_active_color if self.active else self.border_color
        pygame.draw.rect(screen, border_color, self.rect, 3)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw cursor
        if self.cursor_visible and self.active:
            cursor_x = self.rect.x + 10 + text_surface.get_width() + 2
            cursor_y = self.rect.y + 10
            pygame.draw.line(screen, self.text_color, 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + text_surface.get_height()), 2)


# ============================================================================
# GAME CLASSES (from work.py)
# ============================================================================

class Player(pygame.sprite.Sprite):
    """Player controlled bacteria sprite with gameplay stats"""
    
    def __init__(self, groups, circuits):
        super().__init__(groups)
        
        # Generate bacteria sprite from circuits
        self.circuits = circuits
        self.base_size = 80  # Base bacteria size
        
        # Get gameplay stats from circuits
        strength_map = {'weak': 0.3, 'medium': 0.7, 'strong': 1.0}
        
        life_circuit = circuits['life']
        speed_circuit = circuits['speed']
        small_circuit = circuits['small']
        
        life_expr = strength_map[life_circuit.promoter.strength]
        speed_expr = strength_map[speed_circuit.promoter.strength]
        small_expr = strength_map[small_circuit.promoter.strength]
        
        self.max_lives = life_circuit.cds.get_lives_from_expression(life_expr)
        self.lives = self.max_lives
        self.speed_multiplier = speed_circuit.cds.get_speed_multiplier(speed_expr)
        self.size_multiplier = small_circuit.cds.get_size_multiplier(small_expr)
        
        # Generate bacteria image
        self._generate_bacteria_image()
        
        # Position
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 200 * self.speed_multiplier
        
        # Shooting cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        
        # Invincibility after hit
        self.invincible = False
        self.invincible_time = 0
        self.invincible_duration = 1000  # 1 second
        
        # Store base values for powerup reversion
        self.base_speed = self.speed
        self.base_cooldown = self.cooldown_duration
        self.base_size_multiplier = self.size_multiplier
        
        # Track active powerups with end times
        self.active_powerups = {
            'speedup': {'active': False, 'end_time': 0},
            'shrinkdown': {'active': False, 'end_time': 0},
            'morelasers': {'active': False, 'end_time': 0},
            'timefreeze': {'active': False, 'end_time': 0}
        }
        
        # Mask for collision
        self.mask = pygame.mask.from_surface(self.image)
    
    def _generate_bacteria_image(self):
        """Generate bacteria sprite using proven BacteriaPreviewSprite rendering"""
        # Calculate final size based on small gene
        final_size = int(self.base_size * self.size_multiplier)
        
        # Create a temporary BacteriaPreviewSprite to render the bacteria
        preview = BacteriaPreviewSprite(x=0, y=0, size=final_size)
        
        # Prepare circuits dict for preview (needs all 4 for proper rendering)
        preview_circuits = {
            'shape': self.circuits['shape'],
            'surface': self.circuits['surface'],
            'color': self.circuits['color'],
            'small': self.circuits['small']
        }
        
        # Let the preview sprite render the bacteria
        preview.update(preview_circuits)
        
        # Extract the perfectly rendered surface
        self.image = preview.surface.copy()
        
        # preview goes out of scope and gets garbage collected
    
    def laser_timer(self):
        """Update laser cooldown"""
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
    
    def invincibility_timer(self):
        """Update invincibility status"""
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_time >= self.invincible_duration:
                self.invincible = False
    
    def take_damage(self):
        """Take damage if not invincible"""
        if not self.invincible:
            self.lives -= 1
            if self.lives > 0:
                self.invincible = True
                self.invincible_time = pygame.time.get_ticks()
            return True
        return False
    
    def apply_powerup(self, powerup_type):
        """Apply powerup effect for 5 seconds"""
        current_time = pygame.time.get_ticks()
        duration = 5000  # 5 seconds
        
        # Reset timer if already active, or activate new powerup
        self.active_powerups[powerup_type]['active'] = True
        self.active_powerups[powerup_type]['end_time'] = current_time + duration
        
        # Apply immediate effects
        if powerup_type == 'speedup':
            self.speed = self.base_speed * 1.5
        
        elif powerup_type == 'shrinkdown':
            # Reduce size to 70% of current
            self.size_multiplier = self.size_multiplier * 0.7
            self._generate_bacteria_image()
            self.rect = self.image.get_frect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)
        
        elif powerup_type == 'morelasers':
            self.cooldown_duration = int(self.base_cooldown * 0.7)
        
        # timefreeze has no player-side effect (handled in main loop)
    
    def update_powerups(self):
        """Check and expire powerup effects"""
        current_time = pygame.time.get_ticks()
        
        # Check speedup expiration
        if self.active_powerups['speedup']['active']:
            if current_time >= self.active_powerups['speedup']['end_time']:
                self.active_powerups['speedup']['active'] = False
                self.speed = self.base_speed
        
        # Check shrinkdown expiration
        if self.active_powerups['shrinkdown']['active']:
            if current_time >= self.active_powerups['shrinkdown']['end_time']:
                self.active_powerups['shrinkdown']['active'] = False
                # Restore original size
                self.size_multiplier = self.base_size_multiplier
                self._generate_bacteria_image()
                self.rect = self.image.get_frect(center=self.rect.center)
                self.mask = pygame.mask.from_surface(self.image)
        
        # Check morelasers expiration
        if self.active_powerups['morelasers']['active']:
            if current_time >= self.active_powerups['morelasers']['end_time']:
                self.active_powerups['morelasers']['active'] = False
                self.cooldown_duration = self.base_cooldown
        
        # Check timefreeze expiration
        if self.active_powerups['timefreeze']['active']:
            if current_time >= self.active_powerups['timefreeze']['end_time']:
                self.active_powerups['timefreeze']['active'] = False
    
    def update(self, dt):
        """Update player state"""
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        
        self.laser_timer()
        self.invincibility_timer()
        self.update_powerups()

class Laser(pygame.sprite.Sprite):
    """Laser projectile"""
    
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    """Falling enemy"""
    
    def __init__(self, surf, pos, groups, facing, scale):
        super().__init__(groups)
        self.scale = scale 
        enemy_size = surf.get_size()
        self.image = pygame.transform.scale(surf, (self.scale * enemy_size[0], self.scale * enemy_size[1]))
        self.rect = self.image.get_frect(topleft=pos)
        
        self.start_time = pygame.time.get_ticks()
        self.life = 5000
        
        self.facing = facing
        
        if facing == 'up': 
            self.direction = pygame.Vector2((uniform(-0.3, 0.3), 1))
        
        if facing == 'left': 
            self.direction = pygame.Vector2((1, uniform(-0.3, 0.3)))
        
        if facing == 'right':
            self.direction = pygame.Vector2((-1, uniform(-0.3, 0.3)))
        
        # movement 
        self.speed = randint(400, 600)
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.life:
            self.kill()


class Powerup(pygame.sprite.Sprite):
    """Collectible powerup sprite"""
    
    def __init__(self, powerup_type, surf, pos, groups):
        super().__init__(groups)
        self.powerup_type = powerup_type  # 'speedup', 'shrinkdown', 'morelasers', 'timefreeze'
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, dt):
        # Powerups don't move or expire (user chose "Forever")
        pass

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def draw_title(screen, text, x, y):
    """Draw main title"""
    font = pygame.font.Font(None, 48)
    text_surface = font.render(text, True, (40, 40, 40))
    screen.blit(text_surface, (x, y))


def draw_section_title(screen, text, x, y):
    """Draw section title"""
    font = pygame.font.Font(None, 40)
    text_surface = font.render(text, True, (60, 60, 60))
    screen.blit(text_surface, (x, y))


# ============================================================================
# MAIN CUSTOMISATION WINDOW
# ============================================================================

def create_customisation():
    """Create and run the main application with multiple states"""
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Build-a-Bacteria Game")
    clock = pygame.time.Clock()
    
    # Game state
    current_state = CUSTOMISATION
    
    # ========================================================================
    # CUSTOMISATION STATE SETUP
    # ========================================================================
    
    screen_size = pygame.display.get_window_size()
    global WINDOW_WIDTH
    global WINDOW_HEIGHT
    WINDOW_WIDTH = screen_size[0]
    WINDOW_HEIGHT = screen_size[1]
    
    # Layout for 6 circuits vertically stacked
    left_panel_width = WINDOW_WIDTH // 2
    right_panel_x = left_panel_width + 50
    panel_x = 50
    panel_width = left_panel_width - 100
    panel_spacing = 150  # Reduced to fit 6 circuits
    starting_y = 100
    
    # Visual circuit panels
    shape_panel = CircuitPanel(panel_x, starting_y, panel_width, 'shape')
    surface_panel = CircuitPanel(panel_x, starting_y + panel_spacing, panel_width, 'surface')
    color_panel = CircuitPanel(panel_x, starting_y + 2*panel_spacing, panel_width, 'color')
    
    # Gameplay circuit panels with shared promoter assignments
    promoter_assignments = {'weak': 'life', 'medium': 'speed', 'strong': 'small'}
    life_panel = GameplayCircuitPanel(panel_x, starting_y + 3*panel_spacing, panel_width, 'life', promoter_assignments)
    speed_panel = GameplayCircuitPanel(panel_x, starting_y + 4*panel_spacing, panel_width, 'speed', promoter_assignments)
    small_panel = GameplayCircuitPanel(panel_x, starting_y + 5*panel_spacing, panel_width, 'small', promoter_assignments)
    
    # Build initial circuits
    circuits = {
        'shape': shape_panel.build_circuit(),
        'surface': surface_panel.build_circuit(),
        'color': color_panel.build_circuit(),
        'life': life_panel.build_circuit(),
        'speed': speed_panel.build_circuit(),
        'small': small_panel.build_circuit()
    }
    
    # Play button (was "Build your Bacteria!")
    play_button = Button(panel_x, starting_y + 6*panel_spacing + 20, panel_width, 60, "Build the Bacteria!", 6)
    
    # Preview and stats (smaller to fit with 6 circuits stats)
    preview_size = 230
    preview_x = right_panel_x + (WINDOW_WIDTH / 2 - preview_size) // 2 - 50
    preview_y = 150
    
    bacteria_preview = BacteriaPreviewSprite(preview_x, preview_y, preview_size)
    bacteria_preview.update(circuits)
    
    # Load heart image for life display (needed by CircuitStatsDisplay)
    life_surf = pygame.image.load(join('images', 'heart.png')).convert_alpha()
    
    stats_width = 400
    stats_x = right_panel_x + (WINDOW_WIDTH // 2 - stats_width) // 2 - 50
    stats_y = preview_y + preview_size + 50
    circuit_stats = CircuitStatsDisplay(stats_x, stats_y, stats_width, life_surf)
    circuit_stats.update(circuits)
    
    # ========================================================================
    # GAME STATE SETUP
    # ========================================================================
    
    # Visual assets
    bacteria1_surf = pygame.image.load(join('images', 'bacteria1.png')).convert_alpha()
    bacteria2_surf = pygame.image.load(join('images', 'bacteria2.png')).convert_alpha()
    bacteria3_surf = pygame.image.load(join('images', 'bacteria3.png')).convert_alpha()
    laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
    game_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
    lives_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 32)
    
    # Powerup assets
    speedup_surf = pygame.image.load(join('images', 'speedup.png')).convert_alpha()
    
    shrinkdown_surf = pygame.image.load(join('images', 'shrinkdown.png')).convert_alpha()
    
    morelasers_surf = pygame.image.load(join('images', 'morelasers.png')).convert_alpha()
    
    timefreeze_surf = pygame.image.load(join('images', 'timefreeze.png')).convert_alpha()
    
    powerup_images = {
        'speedup': speedup_surf,
        'shrinkdown': shrinkdown_surf,
        'morelasers': morelasers_surf,
        'timefreeze': timefreeze_surf
    }
    
    # sound assets
    laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
    laser_sound.set_volume(0.8)
    
    menu_music = pygame.mixer.Sound(join('audio', 'menu.mp3'))
    stage1music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
    stage2music = pygame.mixer.Sound(join('audio', 'chrono.mp3'))
    stage3music = pygame.mixer.Sound(join('audio', 'castlevania.mp3'))
    stage4music = pygame.mixer.Sound(join('audio', 'ken.mp3'))
    stage5music =pygame.mixer.Sound(join('audio', 'megaman.mp3'))
    
    # Game variables (initialized when entering GAME state)
    player = None
    all_sprites = None
    obstacle_sprites = None
    laser_sprites = None
    powerup_sprites = None
    obstacle_event = None
    powerup_event = None
    game_start_time = 0
    final_score = 0
    current_score = 0
    current_stage = 0
    
    # ========================================================================
    # GAME OVER STATE SETUP
    # ========================================================================
    
    text_input = None
    thankyou_timer = 0
    gameover_timer = 0
    
    # ========================================================================
    # MAIN LOOP
    # ========================================================================
    
    menu_music.play(loops=-1)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # ====================================================================
        # EVENT HANDLING
        # ====================================================================
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # CUSTOMISATION STATE EVENTS
            if current_state == CUSTOMISATION:
                state_changed = False
                state_changed |= shape_panel.handle_event(event)
                state_changed |= surface_panel.handle_event(event)
                state_changed |= color_panel.handle_event(event)
                state_changed |= life_panel.handle_event(event)
                state_changed |= speed_panel.handle_event(event)
                state_changed |= small_panel.handle_event(event)
                
                if state_changed:
                    circuits['shape'] = shape_panel.build_circuit()
                    circuits['surface'] = surface_panel.build_circuit()
                    circuits['color'] = color_panel.build_circuit()
                    circuits['life'] = life_panel.build_circuit()
                    circuits['speed'] = speed_panel.build_circuit()
                    circuits['small'] = small_panel.build_circuit()
                    
                    bacteria_preview.update(circuits)
                    circuit_stats.update(circuits)
                
                # Play button clicked - transition to GAME
                if play_button.handle_click():
                    current_state = GAME
                    menu_music.stop()
                    stage1music.play(loops = -1, fade_ms=500)
                    current_stage = 1
                    
                    # Initialize game
                    all_sprites = pygame.sprite.Group()
                    obstacle_sprites = pygame.sprite.Group()
                    laser_sprites = pygame.sprite.Group()
                    powerup_sprites = pygame.sprite.Group()
                    
                    # Create player with circuits
                    player = Player(all_sprites, circuits)
                    
                    # Setup enemy spawn event
                    obstacle_event = pygame.event.custom_type()
                    pygame.time.set_timer(obstacle_event, 300)
                    
                    # Setup powerup spawn event (will be started at stage 2)
                    powerup_event = pygame.event.custom_type()
                    
                    game_start_time = pygame.time.get_ticks()
                    
            
            # GAME STATE EVENTS
            elif current_state == GAME:
                if event.type == obstacle_event and not player.active_powerups['timefreeze']['active']:
                    if current_stage == 1: 
                        x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                        Obstacle(bacteria1_surf, (x, y), (all_sprites, obstacle_sprites), 'up', uniform(0.8, 1.0))   
                    
                    elif current_stage == 2: 
                        x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                        pygame.time.set_timer(obstacle_event, 250)
                        surf = choice([bacteria1_surf ,bacteria2_surf])
                        Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'up', uniform(0.6, 1.0))    
                        
                    elif current_stage == 3: 
                        x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                        pygame.time.set_timer(obstacle_event, 200)
                        surf = choice([bacteria1_surf ,bacteria2_surf, bacteria3_surf])
                        Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'up', uniform(0.6, 1.2)) 
                    
                    elif current_stage == 4: 
                        x1, y1 = randint(0, WINDOW_WIDTH), randint(-200, -100)
                        x2, y2 = randint(-200, -100), randint(0, WINDOW_HEIGHT)
                        x3, y3 = randint(WINDOW_WIDTH + 100, WINDOW_WIDTH + 200), randint(-200, WINDOW_HEIGHT)
                        x, y = choice([(x1,y1), (x2,y2), (x3,y3)])
                        pygame.time.set_timer(obstacle_event, 200)
                        surf = choice([bacteria1_surf ,bacteria2_surf, bacteria3_surf])
                        if x == x1 and y == y1:
                            Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'up', uniform(0.6, 1.2))
                        elif x == x2 and y == y2:
                            Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'left', uniform(0.6, 1.0))
                        elif x == x3 and y == y3:
                            Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'right', uniform(0.6, 1.0))
                    
                    elif current_stage == 5: 
                        x1, y1 = randint(0, WINDOW_WIDTH), randint(-200, -100)
                        x2, y2 = randint(-200, -100), randint(0, WINDOW_HEIGHT)
                        x3, y3 = randint(100, 200), randint(-200, WINDOW_HEIGHT)
                        x, y = choice([(x1,y1), (x2,y2), (x3,y3)])
                        pygame.time.set_timer(obstacle_event, 150)
                        surf = choice([bacteria1_surf ,bacteria2_surf, bacteria3_surf])
                        
                        if x == x1 and y == y1:
                            Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'up', uniform(0.8, 1.6))
                        elif x == x2 and y == y2:
                            Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'left', uniform(0.8, 1.2))
                        elif x == x3 and y == y3:
                            Obstacle(surf, (x, y), (all_sprites, obstacle_sprites), 'right', uniform(0.8, 1.2))
                
                # Powerup spawning (starts in stage 2)
                if event.type == powerup_event and current_stage >= 2:
                    # Random powerup type
                    powerup_type = choice(['speedup', 'shrinkdown', 'morelasers', 'timefreeze'])
                    powerup_surf = powerup_images[powerup_type]
                    
                    # Random position (avoid edges)
                    x = randint(100, WINDOW_WIDTH - 100)
                    y = randint(100, WINDOW_HEIGHT - 100)
                    
                    Powerup(powerup_type, powerup_surf, (x, y), (all_sprites, powerup_sprites))
            
            # GAMEOVER STATE EVENTS
            elif current_state == GAMEOVER:
                if text_input and text_input.handle_event(event):
                    # Name submitted
                    player_name = text_input.text if text_input.text else "Anonymous"
                    
                    # Save score to data.json
                    score_entry = {
                        'name': player_name,
                        'score': final_score,
                        'visual_circuits': {
                            'shape': circuits['shape'].to_dict(),
                            'surface': circuits['surface'].to_dict(),
                            'color': circuits['color'].to_dict()
                        },
                        'gameplay_circuits': {
                            'life': circuits['life'].to_dict(),
                            'speed': circuits['speed'].to_dict(),
                            'small': circuits['small'].to_dict()
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Load existing scores
                    try:
                        with open('data.json', 'r') as f:
                            scores = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        scores = []
                    
                    # Add new score
                    scores.append(score_entry)
                    
                    # Sort by score (highest first)
                    scores.sort(key=lambda x: x['score'], reverse=True)
                    
                    # Save back
                    with open('data.json', 'w') as f:
                        json.dump(scores, f, indent=2)
                    
                    # Transition to THANKYOU
                    current_state = THANKYOU
                    thankyou_timer = pygame.time.get_ticks()
        
        # ====================================================================
        # UPDATE LOGIC
        # ====================================================================
        
        if current_state == CUSTOMISATION:
            circuit_stats.update_animations()
        
        elif current_state == GAME:
            current_score = (pygame.time.get_ticks() - game_start_time) // 100
            if current_score == 200 and current_stage == 1: 
                # Start powerup spawning every 15 seconds
                pygame.time.set_timer(powerup_event, 10000)  
            
            # handle stages (using == to ensure transitions only happen once)
            if current_score > 500 and current_stage == 1:
                current_stage = 2
                stage1music.fadeout(500)
                stage2music.play(loops=-1, fade_ms=500)
                
            elif current_score > 1200 and current_stage == 2: 
                current_stage = 3
                stage2music.fadeout(500)
                stage3music.play(loops=-1, fade_ms=500)
               
            elif current_score > 2000 and current_stage == 3: 
                current_stage = 4
                stage3music.fadeout(500)  
                stage4music.play(loops=-1, fade_ms=500) 
                
            elif current_score > 4000 and current_stage == 4: 
                current_stage = 5
                stage4music.fadeout(500)
                stage5music.play(loops=-1, fade_ms=500)
                            
            # Handle shooting
            recent_keys = pygame.key.get_just_pressed()
            if recent_keys[pygame.K_SPACE] and player.can_shoot:
                laser_scale = 35
                transformed_laser = pygame.transform.scale(laser_surf, (laser_scale, laser_scale))
                Laser(transformed_laser, player.rect.midtop, (all_sprites, laser_sprites))
                player.can_shoot = False
                player.laser_shoot_time = pygame.time.get_ticks()
                laser_sound.play()
            
            # Update all sprites
            all_sprites.update(dt)
            player.update(dt)
            
            # Check collisions
            # Player-obstacle collision
            collision_sprites = pygame.sprite.spritecollide(player, obstacle_sprites, True, pygame.sprite.collide_mask)
            if collision_sprites:
                player.take_damage()
                
                
                if player.lives <= 0:
                    # Game over
                    final_score = pygame.time.get_ticks() // 100 - game_start_time // 100
                    current_state = GAMEOVER
                    
                    stage1music.stop()
                    stage2music.stop()
                    stage3music.stop()
                    stage4music.stop()
                    stage5music.stop()
                        
                    
                    # Stop obstacle spawning
                    pygame.time.set_timer(obstacle_event, 0)
                    pygame.time.set_timer(powerup_event, 0)
                    
                    # Create text input
                    text_input = TextInput(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 + 150, 400, 50)
                    gameover_timer = pygame.time.get_ticks()
                    
            
            
            # Laser-obstacle collisions
            for laser in laser_sprites:
                collided = pygame.sprite.spritecollide(laser, obstacle_sprites, True)
                if collided:
                    laser.kill()
            
            # Player-powerup collisions
            powerup_collisions = pygame.sprite.spritecollide(player, powerup_sprites, True, pygame.sprite.collide_mask)
            for powerup in powerup_collisions:
                player.apply_powerup(powerup.powerup_type)
        
        elif current_state == GAMEOVER:
            if text_input:
                text_input.update()
        
        elif current_state == THANKYOU:
            # Show thank you for 2 seconds, then return to customisation
            if pygame.time.get_ticks() - thankyou_timer > 2000:
                current_state = CUSTOMISATION
                menu_music.play(loops=-1)
        
        # ====================================================================
        # RENDERING
        # ====================================================================
        
        if current_state == CUSTOMISATION:
            screen.fill((245, 245, 245))
            
            # Separator line
            pygame.draw.line(screen, (180, 180, 180), 
                           (left_panel_width, 80), 
                           (left_panel_width, WINDOW_HEIGHT - 50), 3)
            
            # Title
            draw_title(screen, "Build-a-Bacteria Game", 50, 30)
            
            # Left panels (all 6 circuits)
            shape_panel.draw(screen)
            surface_panel.draw(screen)
            color_panel.draw(screen)
            life_panel.draw(screen)
            speed_panel.draw(screen)
            small_panel.draw(screen)
            play_button.draw(screen)
            
            # Right panel
            draw_section_title(screen, "Live Preview", right_panel_x + 50, 90)
            bacteria_preview.draw(screen)
            circuit_stats.draw(screen)
        
        elif current_state == GAME:
            screen.fill('#F3E5AB')
            
            # Draw score
            score_text = game_font.render(str(current_score), True, 'Black')
            score_rect = score_text.get_frect(midbottom=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
            screen.blit(score_text, score_rect)
            pygame.draw.rect(screen, 'Black', score_rect.inflate(20, 16).move(0, -8), 5, 10)
            
            # Draw sprites
            all_sprites.draw(screen)           
            
            # Draw timefreeze overlay
            if player.active_powerups['timefreeze']['active']:
                timefreeze_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                timefreeze_overlay.fill((173, 216, 230, 80))  # Light blue with transparency
                screen.blit(timefreeze_overlay, (0, 0))
            
            # Draw lives (bacteria icons)
            lives_x = 50
            lives_y = 40
            lives_label = lives_font.render("Lives:", True, 'black')
            screen.blit(lives_label, (lives_x, lives_y))
            
            # Draw hearts for life
            for i in range(player.lives):
                life_scale = 50
                life_rect = pygame.transform.scale(life_surf, (life_scale, life_scale))
                screen.blit(life_rect, (lives_x + 100 + i * 40, lives_y - 10))
            
            # Flash player if invincible
            if player.invincible: 
                if (pygame.time.get_ticks() // 100) % 2:
                    flash_surface = player.image.copy()
                    flash_surface.fill((255,255,255,128), special_flags=pygame.BLEND_RGBA_ADD)
                    screen.blit(flash_surface, player.rect)                
                
        
        elif current_state == GAMEOVER:
            screen.fill((50, 50, 70))
            
            # Game Over text
            title_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 72) if 'Oxanium' in str(game_font) else pygame.font.Font(None, 72)
            gameover_text = title_font.render("GAME OVER", True, (255, 100, 100))
            gameover_rect = gameover_text.get_rect(center=(WINDOW_WIDTH//2, 200))
            screen.blit(gameover_text, gameover_rect)
            
            # Final score
            score_text = game_font.render(f"Final Score: {final_score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, 300))
            screen.blit(score_text, score_rect)
            
            # Circuit summary
            summary_font = pygame.font.Font(None, 28)
            y_offset = 380
            
            summary_lines = [
                "Your Bacteria Build:",
                f"Visual: {circuits['shape'].cds.shape} / {circuits['surface'].cds.surface} / {circuits['color'].cds.color_name}",
                f"Gameplay: Lives={player.max_lives} | Speed={int(player.speed_multiplier*100)}% | Size={int(player.size_multiplier*100)}%"
            ]
            
            for line in summary_lines:
                text = summary_font.render(line, True, (200, 200, 200))
                text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y_offset))
                screen.blit(text, text_rect)
                y_offset += 35
            
            # Name input
            if text_input:
                prompt_text = summary_font.render("Enter Your Name:", True, (255, 255, 255))
                prompt_rect = prompt_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))
                screen.blit(prompt_text, prompt_rect)
                
                text_input.draw(screen)
                
                hint_text = pygame.font.Font(None, 20).render("Press ENTER to submit", True, (150, 150, 150))
                hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 220))
                screen.blit(hint_text, hint_rect)
        
        elif current_state == THANKYOU:
            screen.fill((70, 120, 80))
            
            thank_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 60) if 'Oxanium' in str(game_font) else pygame.font.Font(None, 60)
            thank_text = thank_font.render("Thank you for playing!", True, (255, 255, 255))
            thank_rect = thank_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(thank_text, thank_rect)
        
        pygame.display.flip()
    
    pygame.quit()
