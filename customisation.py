from settings import *
from biology import Circuit, Bacteria, Promoter, ShapeCDS, SurfaceCDS, ColorCDS
import json
import math
from os.path import join

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
    """Simplified button widget"""
    
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 32)
    
    def handle_event(self, event):
        """Returns True if button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.rect.collidepoint(event.pos)
        return False
    
    def draw(self, screen):
        pygame.draw.rect(screen, (70, 130, 180), self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class CircuitPanel:
    """Panel with horizontally arranged circuit components"""
    
    def __init__(self, x, y, width, circuit_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = 110  # Slightly taller for better visual proportions
        self.circuit_type = circuit_type
        
        # Fonts
        self.title_font = pygame.font.Font(None, 34)  # Slightly larger title
        self.label_font = pygame.font.Font(None, 26)  # Slightly larger labels
        
        # Colors
        self.title_color = (50, 50, 50)
        self.label_color = (80, 80, 80)
        self.bg_color = (255, 255, 255)
        self.border_color = (180, 180, 180)
        
        # Horizontal layout spacing
        selector_width = 220  # Adjusted for better fit
        selector_height = 45  # Taller for easier clicking
        spacing = 45  # Balanced spacing between components
        label_width = 95  # Slightly narrower labels
        
        # Starting position for components (after title)
        component_y = y + 50  # More space below title
        current_x = x + 25  # More padding from left edge
        
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


class BacteriaPreviewSprite:
    """Renders bacteria using pygame drawing functions"""
    
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Use Bacteria class from biology.py
        self.bacteria = Bacteria()
        
        # Store shape boundary for surface patterns
        self.shape_rect = None  # Will be set by _draw_sphere or _draw_rod
    
    def update(self, circuits):
        """Update bacteria appearance based on circuits"""
        # Reset bacteria to default state
        self.bacteria.reset()
        
        # Express all three circuits on the bacteria
        circuits['shape'].express(self.bacteria)
        circuits['surface'].express(self.bacteria)
        circuits['color'].express(self.bacteria)
        
        # Re-render
        self._render()
    
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
        """Draw bacteria to screen"""
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
    """Create and run the customisation window"""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Synthetic Biology Circuit Designer")
    clock = pygame.time.Clock()
    
    # Calculate layout (50/50 split)
    left_panel_width = WINDOW_WIDTH // 2
    right_panel_x = left_panel_width + 50
    
    # Create circuit panels (centered vertically with nice spacing)
    panel_x = 50
    panel_width = left_panel_width - 100
    panel_spacing = 150  # Increased spacing for better visual breathing room
    starting_y = 150  # Start lower to balance with title
    
    shape_panel = CircuitPanel(panel_x, starting_y, panel_width, 'shape')
    surface_panel = CircuitPanel(panel_x, starting_y + panel_spacing, panel_width, 'surface')
    color_panel = CircuitPanel(panel_x, starting_y + 2*panel_spacing, panel_width, 'color')
    
    # Build initial circuits
    circuits = {
        'shape': shape_panel.build_circuit(),
        'surface': surface_panel.build_circuit(),
        'color': color_panel.build_circuit()
    }
    
    save_button = Button(panel_x, starting_y + 3*panel_spacing + 40, panel_width, 60, "Build your Bacteria!")
    
    # Right panel (Preview) - larger and centered
    preview_size = 350  # Increased from 250 for better visibility
    preview_x = right_panel_x + (WINDOW_WIDTH // 2 - preview_size) // 2 - 50
    preview_y = 200  # Centered vertically in available space
    
    bacteria_preview = BacteriaPreviewSprite(preview_x, preview_y, preview_size)
    bacteria_preview.update(circuits)

    # Confirmation message
    confirmation = ConfirmationMessage()
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle panel events
            state_changed = False
            state_changed |= shape_panel.handle_event(event)
            state_changed |= surface_panel.handle_event(event)
            state_changed |= color_panel.handle_event(event)
            
            # If state changed, rebuild circuits and update preview IMMEDIATELY
            if state_changed:
                # Rebuild circuits from current selections
                circuits['shape'] = shape_panel.build_circuit()
                circuits['surface'] = surface_panel.build_circuit()
                circuits['color'] = color_panel.build_circuit()
                
                # Update bacteria preview
                bacteria_preview.update(circuits)
                
            # Handle build button
            if save_button.handle_event(event):
                # Create bacteria data
                bacteria_data = {
                    'shape_circuit': circuits['shape'].to_dict(),
                    'surface_circuit': circuits['surface'].to_dict(),
                    'color_circuit': circuits['color'].to_dict()
                }
                
                # Load existing bacteria or create new list
                try:
                    with open('data.json', 'r') as f:
                        all_bacteria = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    all_bacteria = []
                
                # Append new bacteria
                all_bacteria.append(bacteria_data)
                
                # Save back to file
                with open('data.json', 'w') as f:
                    json.dump(all_bacteria, f, indent=2)
                
                confirmation.show("Bacteria Built!")
        
        # Update confirmation message
        confirmation.update()
        
        # Draw everything
        screen.fill((245, 245, 245))  # Light gray background
        
        # Draw vertical separator line
        separator_start_y = 100
        pygame.draw.line(screen, (180, 180, 180), 
                        (left_panel_width, separator_start_y), 
                        (left_panel_width, WINDOW_HEIGHT - 50), 3)
        
        # Draw main title (centered with better spacing)
        title_y = 40
        draw_title(screen, "Synthetic Biology Circuit Designer", 50, title_y)
        
        # Draw left panel
        shape_panel.draw(screen)
        surface_panel.draw(screen)
        color_panel.draw(screen)
        save_button.draw(screen)
        
        # Draw right panel
        preview_title_y = 120
        draw_section_title(screen, "Live Preview", right_panel_x + 50, preview_title_y)
        bacteria_preview.draw(screen)
        
        # Draw confirmation message (on top of everything)
        confirmation.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
