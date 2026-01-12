from nbiology import Circuit, Bacteria, Promoter, ShapeCDS, SurfaceCDS
from settings import *

class UI: 
    def __init__(self): 
        self.screen = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = WINDOW_WIDTH / 2
        self.top = WINDOW_HEIGHT / 2
    
    def general(self): 
        rect = pygame.FRect(self.left, self.top, 400, 400)
        self.draw.rect(self.screen, 'red')
        
    def draw(self): 
        self.general() 
            
def create_customisation():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Window 1")
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 255))  # Blue background
        pygame.display.update()
        clock.tick(60)
    
    pygame.quit()
    
    