import math
import settings

import pygame
from pygame.locals import *

from utilities.core import Task
from utilities.vector import Vector

# Commands {{{
class BounceBall(object):

    def __init__(self, top, left, bottom, right):
        self.top = top; self.bottom = bottom
        self.left = left; self.right = right

class ScorePoint(object):

    def __init__(self, player):
        self.player = player

class MovePaddle(object):

    def __init__(self, player, up=False, down=False):
        self.player = player
        self.up = up; self.down = down

class StopPaddle(object):

    def __init__(self, player, up=False, down=False):
        self.player = player
        self.up = up; self.down = down

# }}}1

class Game:

    # Constructor {{{1
    def __init__(self, world, forum):
        self.world = world
        self.forum = forum

    # Game Loop {{{1
    def setup(self):
        forum = self.forum
        world = self.world

        me = world.me.shape; you = world.you.shape
        field = world.field

        # Keep the paddles inside the playing field.
        me.keep_inside(field)
        you.keep_inside(field)

        # Assume responsibility for managing the world.
        forum.subscribe(BounceBall, self.bounce_ball)
        forum.subscribe(ScorePoint, self.score_point)

        forum.subscribe(MovePaddle, self.move_paddle)
        forum.subscribe(StopPaddle, self.stop_paddle)

    def update(self, time):
        self.world.me.update(time)
        self.world.you.update(time)
        self.world.ball.update(time)

    def teardown(self):
        pass

    # Event Handlers {{{1
    def bounce_ball(self, command):
        ball = self.world.ball
        field = self.world.field

        vx, vy = ball.velocity

        if command.top:
            vy = 1 * abs(vy)
            ball.shape.align_top(field)

        if command.bottom: 
            vy = -1 * abs(vy)
            ball.shape.align_bottom(field)

        if command.left:
            vx = 1 * abs(vx)
            ball.shape.align_left(field)

        if command.right:
            vx = -1 * abs(vx)
            ball.shape.align_right(field)

        velocity = Vector(vx, vy)
        self.world.ball.velocity = velocity

    def score_point(self, command):
        player = command.player
        player.score += 1

        if player.score == settings.winning_score:
            if not self.world.winner:
                self.world.winner = player

    def move_paddle(self, command):
        player = command.player
        velocity = settings.paddle_speed

        if command.up: player.velocity -= velocity
        if command.down: player.velocity += velocity

    def stop_paddle(self, command):
        player = command.player
        velocity = player.velocity

        if command.up and velocity < 0: player.velocity = 0
        if command.down and velocity > 0: player.velocity = 0

    # }}}1

class Triggers(Task):

    # Constructor {{{1
    def __init__(self, world, forum):
        self.world = world
        self.forum = forum
    
    # Game Loop {{{1
    def setup(self):
        pass

    def update(self, time):
        forum = self.forum
        world = self.world

        ball = self.world.ball.shape
        field = self.world.field

        top, left, bottom, right = ball.inside(field)

        # Bounce the ball if it hits any of the walls.
        if top or bottom or left or right:
            bounce = BounceBall(top, left, bottom, right)
            forum.publish(bounce)

        me = self.world.me
        you = self.world.you

        past_me = ball.bottom < me.shape.top or ball.top > me.shape.bottom 
        past_you = ball.bottom < you.shape.top or ball.top > you.shape.bottom 

        # Change the score if the ball wasn't blocked.
        if left and past_me:
            score = ScorePoint(you)
            forum.publish(score)

        if right and past_you:
            score = ScorePoint(me)
            forum.publish(score)

    def teardown(self):
        pass

    # }}}1

class Player(Task):

    # Constructor {{{1
    def __init__(self, world, forum):
        self.world = world
        self.forum = forum

    # Game Loop {{{1
    def setup(self):
        pygame.init()

        # Save references to other game systems.
        self.world = self.world

        # Create a window to run the game in.
        self.size = [ int(value) for value in self.world.field.size ]
        self.screen = pygame.display.set_mode(self.size)

        self.font = pygame.font.Font(None, settings.text_size)

    def update(self, time):
        self.draw(time)
        if not self.world.winner:
            self.react(time)

    def teardown(self):
        pass

    # }}}1

    # Drawing Methods {{{1
    def draw(self, time):
        world = self.world
        screen = self.screen

        screen.fill(settings.background_color)

        self.draw_player(world.me)
        self.draw_player(world.you)

        self.draw_ball()

        pygame.display.flip()

    def draw_player(self, player):
        world = self.world
        field = world.field

        # Draw the player's score.
        score = str(player.score)
        color = settings.text_color

        width, height = self.font.size(score)

        if player is world.me:
            position = (field.width / 4) - (width / 2), 10
        else:
            position = (3 * field.width / 4) - (width / 2), 10

        text = self.font.render(score, True, color)
        self.screen.blit(text, position)

        # Draw the player's paddle.
        color = settings.foreground_color
        dimensions = player.shape.pygame

        pygame.draw.rect(self.screen, color, dimensions)

    def draw_ball(self):
        ball = self.world.ball

        color = settings.foreground_color
        position, radius = ball.shape.pygame

        pygame.draw.circle(self.screen, color, position, radius)

    # User Input Methods {{{1
    def react(self, time):
        me = self.world.me
        forum = self.forum

        if pygame.event.get(QUIT):
            pass

        for event in pygame.event.get(KEYDOWN):
            if event.key == settings.up_control:
                move = MovePaddle(me, up=True)
                forum.publish(move)

            if event.key == settings.down_control:
                move = MovePaddle(me, down=True)
                forum.publish(move)

        for event in pygame.event.get(KEYUP):
            if event.key == settings.up_control:
                move = StopPaddle(me, up=True)
                forum.publish(move)

            if event.key == settings.down_control:
                move = StopPaddle(me, down=True)
                forum.publish(move)

        pygame.event.clear()

    # }}}1

class Opponent(Task):

    # Constructor {{{1
    def __init__(self, world, forum):
        self.world = world
        self.forum = forum
    
    # Game Loop {{{1
    def setup(self):
        pass

    def update(self, time):
        pass

    def teardown(self):
        pass

    # }}}1
