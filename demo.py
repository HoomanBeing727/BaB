import json
from multiprocessing import Process
from customisation import create_customisation
from platedisplay import create_platedisplay


# initialise two displays
if __name__ == '__main__':
    p1 = Process(target=create_customisation)
    p2 = Process(target=create_platedisplay)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
