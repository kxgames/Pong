import pygame
from pygame.locals import *
from utilities.shapes import *

# Gameplay Parameters
winning_score = 5

field_shape = Rectangle.from_width(700)
paddle_shape = Rectangle.from_size(4, 40)
ball_shape = Circle.from_radius(5)

paddle_spin = 0.5
paddle_speed = 150
ball_speed = 400

# Computer Opponent Parameters
reaction_time = 0.3
adjustment_time = 0.7

bounce_penalty = 1.9
foresight_penalty = 20

# User Interface Parameters
up_control = K_k
down_control = K_j

text_size = 50
text_color = 255, 255, 255

background_color = 0, 0, 0
foreground_color = 255, 255, 255

