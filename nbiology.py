from abc import ABC, abstractmethod
from typing import Dict, Any, Literal

''' Parts Classes '''
class Part(ABC): 
    
    @abstractmethod
    def get_info(self):
        pass 

class Promoter(Part): 
    def __init__(self, strength: Literal['weak', 'medium', 'strong']):
            if strength not in ['weak', 'medium', 'strong']:
                raise ValueError(f"Invalid promoter strength: {strength}")
            self.strength = strength
    
    def get_expression_level(self) -> float:
        multipliers = {
            'weak': 0.3,
            'medium': 0.7,
            'strong': 1.0
        }
        return multipliers[self.strength]
    
    def get_info(self): 
        pass 

# Promoter Test
strength = input('Enter Promoter: ')

try:
    promoter = Promoter(strength)
    print(promoter.get_expression_level())
except ValueError as e: 
    print('Error')
    
class RBS(Part):
    """Ribosome Binding Site - fixed for educational simplicity"""
    
    def __init__(self):
        self.efficiency = "standard"
    
    def get_info(self) -> str:
        return f"RBS (Efficiency: {self.efficiency})"


class Terminator(Part):
    """Transcription terminator - fixed for educational simplicity"""
    
    def __init__(self):
        self.terminator_type = "standard"
    
    def get_info(self) -> str:
        return f"Terminator (Type: {self.terminator_type})"

class CodingSequence(Part):
    """Abstract base for all coding sequences"""
    
    def __init__(self, category: Literal['shape', 'surface', 'color']):
        self.category = category

class ShapeCDS(CodingSequence):
    """Coding sequence that affects bacteria shape"""
    
    def __init__(self, shape: Literal['spherical', 'rod']):
        super().__init__('shape')
        if shape not in ['spherical', 'rod']:
            raise ValueError(f"Invalid shape: {shape}")
        self.shape = shape
    
    def get_info(self) -> str:
        return f"Shape CDS (Shape: {self.shape})"

class ColourCDS(CodingSequence):
    """Coding sequence that affects bacteria colour"""
    
    colour_choices = {
        'green': (0, 255, 0),     # GFP - Green Fluorescent Protein
        'yellow': (255, 255, 0),    # YFP - Yellow Fluorescent Protein
        'red': (255, 0, 0),      # RFP - Red Fluorescent Protein
        'blue': (0,0,255)    # BFP - Blue Fluorescent Protein
    } 
    
    def __init__(self, colours: Literal['green', 'yellow', 'red', 'blue']):
        super().__init__('colours')
        if colours not in ['green', 'yellow', 'red', 'blue']:
            raise ValueError(f"Invalid shape: {colours}")
        self.colours = colours
    
    def get_info(self) -> str:
        return f"Colour CDS (Colour: {self.colours})"

class SurfaceCDS(CodingSequence):
    """Coding sequence that affects bacteria surface texture"""
    
    def __init__(self, surface: Literal['smooth', 'rough', 'spiky']):
        super().__init__('surface')
        if surface not in ['smooth', 'rough', 'spiky']:
            raise ValueError(f"Invalid surface: {surface}")
        self.surface = surface
    
    def get_info(self) -> str:
        return f"Surface CDS (Surface: {self.surface})"
    
''' Circuit Class'''

class Circuit:
    """Represents a genetic circuit with promoter, RBS, CDS, and terminator"""
    
    def __init__(self, 
                 promoter: Promoter,
                 cds: CodingSequence,
                 circuit_type: Literal['shape', 'surface', 'color']):
        
        if circuit_type not in ['shape', 'surface', 'color']:
            raise ValueError(f"Invalid circuit type: {circuit_type}")
        
        if cds.category != circuit_type:
            raise ValueError(f"CDS category ({cds.category}) must match circuit type ({circuit_type})")
        
        self.promoter = promoter
        self.rbs = RBS()  # Auto-added, fixed
        self.cds = cds
        self.terminator = Terminator()  # Auto-added, fixed
        self.circuit_type = circuit_type
    
    def get_expression_level(self) -> float:
        """Get expression level from promoter"""
        return self.promoter.get_expression_level()
    
    def express(self, bacteria: 'Bacteria') -> None:
        """Express the circuit on the bacteria"""
        expression_level = self.get_expression_level()
        self.cds.apply_effect(bacteria, expression_level)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize circuit to flat dictionary structure"""
        result = {
            'promoter_strength': self.promoter.strength,
            'circuit_type': self.circuit_type
        }
        
        # Add CDS-specific property based on circuit type
        if self.circuit_type == 'shape' and isinstance(self.cds, ShapeCDS):
            result['shape'] = self.cds.shape
        elif self.circuit_type == 'surface' and isinstance(self.cds, SurfaceCDS):
            result['surface'] = self.cds.surface
        elif self.circuit_type == 'color' and isinstance(self.cds, ColourCDS):
            result['color_name'] = self.cds.color_name
        
        return result
    
    def get_info(self) -> str:
        """Get human-readable circuit information"""
        parts = [
            self.promoter.get_info(),
            self.rbs.get_info(),
            self.cds.get_info(),
            self.terminator.get_info()
        ]
        return f"{self.circuit_type.capitalize()} Circuit: " + " → ".join(parts)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Circuit':
        """Reconstruct circuit from flat dictionary structure"""
        promoter = Promoter(data['promoter_strength'])
        circuit_type = data['circuit_type']
        
        # Create appropriate CDS based on circuit type
        if circuit_type == 'shape':
            cds = ShapeCDS(data['shape'])
        elif circuit_type == 'surface':
            cds = SurfaceCDS(data['surface'])
        elif circuit_type == 'color':
            cds = ColourCDS(data['color_name'])
        else:
            raise ValueError(f"Unknown circuit type: {circuit_type}")
        
        return Circuit(promoter, cds, circuit_type)

''' Actual Bacteria '''
class Bacteria:
    def __init__(self):
        # Default state: medium rod, medium smooth surface, strong green color
        self.shape = 'rod'
        self.shape_expression = 0.7  # medium expression
        
        self.surface = 'smooth'
        self.surface_expression = 0.7  # medium expression
        
        self.color = 'green'  # green (GFP)
        self.color_expression = 1.0  # strong expression
    
    def update_shape(self, shape, expression_level) -> None:
        """Update shape and its expression level"""
        self.shape = shape
        self.shape_expression = expression_level
    
    def update_surface(self, surface, expression_level) -> None:
        """Update surface and its expression level"""
        self.surface = surface
        self.surface_expression = expression_level
    
    def update_color(self, color_hex, expression_level) -> None:
        """Update color and its expression level"""
        self.color = color_hex
        self.color_expression = expression_level
    
    def get_phenotype(self):
        """Get current phenotype (observable characteristics)"""
        return {
            'shape': self.shape,
            'shape_expression': self.shape_expression,
            'surface': self.surface,
            'surface_expression': self.surface_expression,
            'color': self.color,
            'color_expression': self.color_expression
        }
    
    def get_visual_properties(self):
        """
        Get properties formatted for rendering with pygame sprites.
        Expression levels modulate visual intensity/opacity.
        """
        return {
            'shape': {
                'type': self.shape,
                'intensity': self.shape_expression  
            },
            'surface': {
                'type': self.surface,
                'intensity': self.surface_expression
            },
            'color': {
                'hex': self.color,
                'intensity': self.color_expression  
            }
        }
    
    def reset(self) -> None:
        """Reset bacteria to default state"""
        self.__init__()
