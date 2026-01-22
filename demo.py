from multiprocessing import Process
from customisation import create_customisation
from scoreboard import create_scoreboard


# initialise two displays
if __name__ == '__main__':
    p1 = Process(target=create_customisation)
    p2 = Process(target=create_scoreboard)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
