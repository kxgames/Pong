import settings

from utilities.vector import *
from utilities.sprites import Sprite

class World:

    def __init__(self):
        self.me = my = Paddle()
        self.you = your = Paddle()

        self.ball = ball = Ball()
        self.field = field = settings.field_shape

        self.winner = None

        # Place the paddles in the right spots.
        my.shape.align_left(field)
        my.shape.align_vertical(field)

        your.shape.align_right(field)
        your.shape.align_vertical(field)

        # Place the ball in the middle of the screen.
        ball.shape.align_horizontal(field)
        ball.shape.align_vertical(field)

class Paddle(Sprite):

    def __init__(self):
        Sprite.__init__(self)
        self.shape = settings.paddle_shape.copy()
        self.velocity = 0
        self.score = 0
        self.target = Vector(0, 0)


    def update(self, time):
        direction = Vector(0, 1)
        displacement = self.velocity * direction * time
        self.shape.displace(displacement)

class Ball(Sprite):

    def __init__(self):
        Sprite.__init__(self)

        speed = settings.ball_speed
        direction = Vector.random()

        x, y = abs(direction)
        if y > x: direction = direction.orthogonal

        self.shape = settings.ball_shape
        self.velocity = speed * direction

    def update(self, time):
        displacement = self.velocity * time
        self.shape.displace(displacement)

