from __future__ import division

import math
import random
import settings

import pygame
from pygame.locals import *

from utilities.core import Task
from utilities.vector import Vector
from utilities.messaging import Timer

# Commands {{{
class BounceBall(object):

    def __init__(self, top, left, bottom, right):
        self.top = top; self.bottom = bottom
        self.left = left; self.right = right

class BlockBall(object):

    def __init__(self, paddle):
        self.paddle = paddle

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

class Game(Task):

    # Setup {{{1
    def setup(self):
        world = self.world = self.engine.get_world()
        forum = self.forum = self.engine.get_subscriber()

        me = world.me.shape; you = world.you.shape
        field = world.field

        # Keep the paddles inside the playing field.
        me.keep_inside(field)
        you.keep_inside(field)

        # Assume responsibility for managing the world.
        forum.subscribe(BounceBall, self.bounce_ball)
        forum.subscribe(BlockBall, self.block_ball)
        forum.subscribe(ScorePoint, self.score_point)

        forum.subscribe(MovePaddle, self.move_paddle)
        forum.subscribe(StopPaddle, self.stop_paddle)

    # Update {{{1
    def update(self, time):
        self.world.me.update(time)
        self.world.you.update(time)
        self.world.ball.update(time)

    # Teardown {{{1
    def teardown(self):
        pass

    # }}}1

    # Bounce Ball {{{
    def bounce_ball(self, command):
        ball = self.world.ball
        field = self.world.field

        horizontal, vertical = ball.velocity

        if command.top:
            vertical = 1 * abs(vertical)
            ball.shape.align_top(field)

        if command.bottom: 
            vertical = -1 * abs(vertical)
            ball.shape.align_bottom(field)

        if command.left:
            horizontal = 1 * abs(horizontal)
            ball.shape.align_left(field)

        if command.right:
            horizontal = -1 * abs(horizontal)
            ball.shape.align_right(field)

        self.world.ball.velocity = Vector(horizontal, vertical)

    # Block Ball {{{1
    def block_ball(self, command):
        ball = self.world.ball
        paddle = command.paddle

        spin = paddle.velocity * settings.paddle_spin
        ball.velocity += Vector(0, -spin)

    # Score Point {{{1
    def score_point(self, command):
        player = command.player
        player.score += 1

        if player.score == settings.winning_score:
            if not self.world.winner:
                self.world.winner = player
                self.engine.exit_engine()

    # }}}1
    
    # Move Paddle {{{1
    def move_paddle(self, command):
        player = command.player
        velocity = settings.paddle_speed

        if command.up: player.velocity = -velocity
        if command.down: player.velocity = velocity

    # Stop Paddle {{{1
    def stop_paddle(self, command):
        player = command.player
        velocity = player.velocity

        if command.up and velocity < 0: player.velocity = 0
        if command.down and velocity > 0: player.velocity = 0

    # }}}1

class Triggers(Task):

    # Setup {{{1
    def setup(self):
        self.world = self.engine.get_world()
        self.forum = self.engine.get_publisher()

    # Update {{{1
    def update(self, time):
        forum = self.forum
        world = self.world

        ball = self.world.ball.shape
        field = self.world.field

        bounce = shot = None
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
        if left: shot = ScorePoint(you) if past_me else BlockBall(me)
        if right: shot = ScorePoint(me) if past_you else BlockBall(you)

        if left or right:
            forum.publish(shot)

    # Teardown {{{1
    def teardown(self):
        pass

    # }}}1

class Player(Task):

    # Setup {{{1
    def reset(self, engine):
        self.engine = engine
        return self

    def setup_pregame(self):
        pygame.init()

        self.world = self.engine.world
        self.font = pygame.font.Font(None, settings.text_size)

        self.size = [ int(value) for value in self.world.field.size ]
        self.screen = pygame.display.set_mode(self.size)

    def setup_game(self):
        self.world = self.engine.get_world()
        self.forum = self.engine.get_publisher()

    def setup_postgame(self):
        pass

    setup = setup_game

    # Update {{{1
    def update_pregame(self, time):
        self.handle_quit()

        self.draw_background()

        self.draw_paddle(self.world.me)
        self.draw_paddle(self.world.you)

        countdown = math.ceil(self.engine.countdown)
        message = "%d" % countdown

        self.draw_message(message)

        pygame.display.flip()

    def update_game(self, time):
        self.handle_quit()
        self.handle_input()

        self.draw_background()
        self.draw_ball()

        me = self.world.me
        you = self.world.you

        self.draw_paddle(me);   self.draw_score(me)
        self.draw_paddle(you);  self.draw_score(you)

        pygame.display.flip()

    def update_postgame(self, time):
        self.handle_quit()

        world = self.engine.world
        message = "You Win!" if world.winner is world.me else "You Lose!"

        self.draw_background()
        self.draw_ball()

        self.draw_paddle(world.me);     self.draw_score(world.me)
        self.draw_paddle(world.you);    self.draw_score(world.you)

        self.draw_message(message)

        pygame.display.flip()

    update = update_game

    # Teardown {{{1
    def teardown_pregame(self): pass
    def teardown_game(self): pass
    def teardown_postgame(self): pass

    teardown = teardown_game

    # }}}1

    # Input Methods {{{1
    def handle_quit(self):
        if pygame.event.get(QUIT):
            self.engine.exit_loop()

    def handle_input(self):
        me = self.world.me
        forum = self.forum

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

    # Drawing Methods {{{1
    def draw_background(self):
        self.screen.fill(settings.background_color)

    def draw_message(self, message):
        world = self.world
        field = world.field

        width, height = self.font.size(message)
        position = field.horizontal - width / 2, field.vertical - height / 2

        color = settings.text_color
        surface = self.font.render(message, True, color)

        self.screen.blit(surface, position)

    def draw_ball(self):
        ball = self.world.ball

        color = settings.foreground_color
        position, radius = ball.shape.pygame

        pygame.draw.circle(self.screen, color, position, radius)

    def draw_paddle(self, player):
        color = settings.foreground_color
        dimensions = player.shape.pygame

        pygame.draw.rect(self.screen, color, dimensions)

    def draw_score(self, player):
        world = self.world
        field = world.field

        score = str(player.score)
        color = settings.text_color

        width, height = self.font.size(score)

        if player is world.me:
            position = (field.width / 4) - (width / 2), 10
        else:
            position = (3 * field.width / 4) - (width / 2), 10

        text = self.font.render(score, True, color)
        self.screen.blit(text, position)

    # }}}1

class Opponent(Task):

    # Constructor {{{1
    def __init__(self, engine):
        Task.__init__(self, engine)
        self.timer = Timer()

    # }}}1

    # Setup {{{1
    def setup(self):
        self.world = self.engine.get_world()
        self.forum = self.engine.get_member()

        UpdateDefense = Opponent.UpdateDefense
        update_defense = UpdateDefense()

        self.forum.subscribe(BounceBall, self.bounce_ball)
        self.timer.subscribe(UpdateDefense, self.update_defense)
        self.timer.lock()

        self.timer.publish(update_defense, 0)
        self.timer.publish(update_defense, settings.reaction_time)

    # Update {{{1
    def update(self, time):
        forum = self.forum
        timer = self.timer

        timer.deliver(time)

        destination = self.destination
        paddle = self.world.you

        target_above = destination < paddle.shape.vertical
        target_below = destination > paddle.shape.vertical
        
        tolerance = paddle.shape.height / 3

        target_close =                                              \
                destination > paddle.shape.top + tolerance and      \
                destination < paddle.shape.bottom - tolerance

        moving = paddle.velocity != 0
        moving_up = paddle.velocity < 0
        moving_down = paddle.velocity > 0

        if target_close:
            stop_paddle = StopPaddle(paddle, up=True, down=True)
            if moving: forum.publish(stop_paddle)

        elif target_above and not moving_up:
            move_paddle = MovePaddle(paddle, up=True)
            forum.publish(move_paddle)

        elif target_below and not moving_down:
            move_paddle = MovePaddle(paddle, down=True)
            forum.publish(move_paddle)

        else:
            pass

    # Teardown {{{1
    def teardown(self):
        pass

    # }}}1

    # Bounce Ball {{{1
    def bounce_ball(self, command):
        position, bounces, time = self.prepare_defense()
        update_defense = Opponent.UpdateDefense()

        if command.left or command.right:
            delay = time * settings.reaction_time
            self.timer.publish(update_defense, delay)

        if command.left:
            delay = time * settings.adjustment_time
            self.timer.publish(update_defense, delay)

    # Update Defense {{{1
    def update_defense(self, command):
        position, bounces, time = self.prepare_defense()

        confusion = pow(bounces + 1, settings.bounce_penalty)
        sloppiness = time * confusion * settings.foresight_penalty

        self.destination = random.gauss(position, sloppiness)

    # Prepare Defense {{{1
    def prepare_defense(self):
        ball = self.world.ball
        field = self.world.field

        direction = cmp(ball.velocity.x, 0)

        dx = field.width - direction * ball.shape.horizontal
        dy = dx * ball.velocity.y / abs(ball.velocity.x)

        position = dy + ball.shape.vertical
        bounces = position // field.height
        time = abs(dx / ball.velocity.x)

        position = position - bounces * field.height
        if bounces % 2: position = field.height - position

        return position, abs(bounces), time

    # }}}1

    # Update Message {{{1
    class UpdateDefense(object):
        pass

    #}}}1

