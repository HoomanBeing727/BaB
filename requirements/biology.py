# biology.py
# Core biological classes for Synthetic Biology Interactive Program

from abc import ABC, abstractmethod
from typing import Literal, Dict, Any

# ============================================================================
# PART CLASSES
# ============================================================================

class Part(ABC):
    """Abstract base class for all biological parts"""
    
    @abstractmethod
    def get_info(self) -> str:
        """Get human-readable information"""
        pass


class Promoter(Part):
    """Controls expression level of the circuit"""
    
    def __init__(self, strength: Literal['weak', 'medium', 'strong']):
        if strength not in ['weak', 'medium', 'strong']:
            raise ValueError(f"Invalid promoter strength: {strength}")
        self.strength = strength
    
    def get_expression_level(self) -> float:
        """Returns expression multiplier based on strength"""
        multipliers = {
            'weak': 0.3,
            'medium': 0.7,
            'strong': 1.0
        }
        return multipliers[self.strength]
    
    def get_info(self) -> str:
        return f"Promoter (Strength: {self.strength})"


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


class CodingSequence(Part, ABC):
    """Abstract base for all coding sequences"""
    
    def __init__(self, category: Literal['shape', 'surface', 'color']):
        self.category = category
    
    @abstractmethod
    def apply_effect(self, bacteria: 'Bacteria', expression_level: float) -> None:
        """Apply the CDS effect to bacteria with given expression level"""
        pass


class ShapeCDS(CodingSequence):
    """Coding sequence that affects bacteria shape"""
    
    def __init__(self, shape: Literal['spherical', 'rod']):
        super().__init__('shape')
        if shape not in ['spherical', 'rod']:
            raise ValueError(f"Invalid shape: {shape}")
        self.shape = shape
    
    def apply_effect(self, bacteria: 'Bacteria', expression_level: float) -> None:
        bacteria.update_shape(self.shape, expression_level)
    
    def get_info(self) -> str:
        return f"Shape CDS (Shape: {self.shape})"


class SurfaceCDS(CodingSequence):
    """Coding sequence that affects bacteria surface texture"""
    
    def __init__(self, surface: Literal['smooth', 'rough', 'spiky']):
        super().__init__('surface')
        if surface not in ['smooth', 'rough', 'spiky']:
            raise ValueError(f"Invalid surface: {surface}")
        self.surface = surface
    
    def apply_effect(self, bacteria: 'Bacteria', expression_level: float) -> None:
        bacteria.update_surface(self.surface, expression_level)
    
    def get_info(self) -> str:
        return f"Surface CDS (Surface: {self.surface})"


class ColorCDS(CodingSequence):
    """Coding sequence that affects bacteria color"""
    
    # Biologically-inspired fluorescent protein colors
    VALID_COLORS = {
        'cyan': '#00FFFF',      # CFP - Cyan Fluorescent Protein
        'green': '#00FF00',     # GFP - Green Fluorescent Protein
        'yellow': '#FFFF00',    # YFP - Yellow Fluorescent Protein
        'red': '#FF0000',       # RFP - Red Fluorescent Protein
        'blue': '#0000FF'       # BFP - Blue Fluorescent Protein
    }
    
    def __init__(self, color_name: Literal['cyan', 'green', 'yellow', 'red', 'blue']):
        super().__init__('color')
        if color_name not in self.VALID_COLORS:
            raise ValueError(f"Invalid color: {color_name}")
        self.color_name = color_name
        self.color_hex = self.VALID_COLORS[color_name]
    
    def apply_effect(self, bacteria: 'Bacteria', expression_level: float) -> None:
        bacteria.update_color(self.color_hex, expression_level)
    
    def get_info(self) -> str:
        return f"Color CDS (Color: {self.color_name} - {self.color_hex})"


# ============================================================================
# CIRCUIT CLASS
# ============================================================================

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
        elif self.circuit_type == 'color' and isinstance(self.cds, ColorCDS):
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
            cds = ColorCDS(data['color_name'])
        else:
            raise ValueError(f"Unknown circuit type: {circuit_type}")
        
        return Circuit(promoter, cds, circuit_type)


# ============================================================================
# BACTERIA CLASS
# ============================================================================

class Bacteria:
    """Represents a bacteria with shape, surface, and color properties"""
    
    def __init__(self):
        # Default state: medium rod, medium smooth surface, strong green color
        self.shape = 'rod'
        self.shape_expression = 0.7  # medium expression
        
        self.surface = 'smooth'
        self.surface_expression = 0.7  # medium expression
        
        self.color = '#00FF00'  # green (GFP)
        self.color_expression = 1.0  # strong expression
    
    def update_shape(self, shape: str, expression_level: float) -> None:
        """Update shape and its expression level"""
        self.shape = shape
        self.shape_expression = expression_level
    
    def update_surface(self, surface: str, expression_level: float) -> None:
        """Update surface and its expression level"""
        self.surface = surface
        self.surface_expression = expression_level
    
    def update_color(self, color_hex: str, expression_level: float) -> None:
        """Update color and its expression level"""
        self.color = color_hex
        self.color_expression = expression_level
    
    def get_phenotype(self) -> Dict[str, Any]:
        """Get current phenotype (observable characteristics)"""
        return {
            'shape': self.shape,
            'shape_expression': self.shape_expression,
            'surface': self.surface,
            'surface_expression': self.surface_expression,
            'color': self.color,
            'color_expression': self.color_expression
        }
    
    def get_visual_properties(self) -> Dict[str, Any]:
        """
        Get properties formatted for rendering with pygame sprites.
        Expression levels modulate visual intensity/opacity.
        """
        return {
            'shape': {
                'type': self.shape,
                'intensity': self.shape_expression  # 0.3-1.0 for visual modulation
            },
            'surface': {
                'type': self.surface,
                'intensity': self.surface_expression
            },
            'color': {
                'hex': self.color,
                'intensity': self.color_expression  # Affects brightness/opacity
            }
        }
    
    def reset(self) -> None:
        """Reset bacteria to default state"""
        self.__init__()


# ============================================================================
# USAGE EXAMPLE (for testing/reference)
# ============================================================================

if __name__ == "__main__":
    # Create bacteria
    bacteria = Bacteria()
    print("Initial bacteria:", bacteria.get_phenotype())
    
    # Create shape circuit (weak promoter + spherical shape)
    shape_circuit = Circuit(
        promoter=Promoter('weak'),
        cds=ShapeCDS('spherical'),
        circuit_type='shape'
    )
    print(shape_circuit.get_info())
    
    # Create surface circuit (strong promoter + spiky surface)
    surface_circuit = Circuit(
        promoter=Promoter('strong'),
        cds=SurfaceCDS('spiky'),
        circuit_type='surface'
    )
    print(surface_circuit.get_info())
    
    # Create color circuit (medium promoter + red color)
    color_circuit = Circuit(
        promoter=Promoter('medium'),
        cds=ColorCDS('red'),
        circuit_type='color'
    )
    print(color_circuit.get_info())
    
    # Express all circuits
    shape_circuit.express(bacteria)
    surface_circuit.express(bacteria)
    color_circuit.express(bacteria)
    
    print("\nFinal bacteria phenotype:", bacteria.get_phenotype())
    print("Visual properties:", bacteria.get_visual_properties())
    
    # Test serialization
    import json
    data = {
        'shape_circuit': shape_circuit.to_dict(),
        'surface_circuit': surface_circuit.to_dict(),
        'color_circuit': color_circuit.to_dict()
    }
    print("\nSerialized circuits:")
    print(json.dumps(data, indent=2))
    
    # Test deserialization
    reconstructed_shape = Circuit.from_dict(data['shape_circuit'])
    print("\nReconstructed circuit:", reconstructed_shape.get_info())
