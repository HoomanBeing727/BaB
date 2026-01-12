import pygame
from os.path import join

WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080 
SIZE = {'bacteria': (100, 100)}
POS = {'bacteria': (WINDOW_WIDTH - 50, WINDOW_HEIGHT / 2), 'opponent': (50, WINDOW_HEIGHT / 2)}
SPEED = {'player': 500, 'opponent': 250, 'ball': 450}
COLORS = {
    'paddle': '#ee322c',
    'paddle shadow': '#b12521',
    'ball': '#ee622c',
    'ball shadow': '#c14f24',
    'bg': '#002633',
    'bg detail': '#004a63'
}