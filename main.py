#!/usr/bin/env python

from game import *
from world import *

from utilities.core import *
from utilities.messaging import Forum

class PongLoop(Loop):

    # Constructor {{{1
    def __init__(self):
        self.engine = PregameEngine(self)

    # }}}1

class PregameEngine(GameEngine):

    # Constructor {{{1
    def __init__(self, loop):
        Engine.__init__(self, loop)

        self.world = World()
        self.player = Player(self)

    # Game Loop {{{1
    def setup(self):
        self.player.setup_pregame()
        self.countdown = settings.countdown

    def update(self, time):
        self.player.update_pregame(time)

        if self.countdown < 0:
            self.exit_engine()
        else:
            self.countdown -= time

    def teardown(self):
        self.player.teardown_pregame()

    def successor(self):
        return PongEngine(self.loop, self.world, self.player)

    # }}}1

class PongEngine(GameEngine):

    # Constructor {{{1
    def __init__(self, loop, world, player):
        GameEngine.__init__(self, loop)

        self.world = world
        self.game = Game(self)

        self.tasks = {
                "triggers" : Triggers(self),
                "player" : player.reset(self), 
                "opponent" : Opponent(self) }

    # Game Loop {{{1
    def successor(self):
        player = self.tasks["player"]
        return PostgameEngine(self.loop, self.world, player)

    # }}}1

class PostgameEngine(Engine):

    # Constructor {{{1
    def __init__(self, loop, world, player):
        Engine.__init__(self, loop)

        self.world = world
        self.player = player

    # Game Loop {{{1
    def setup(self): 
        self.player.setup_postgame()

    def update(self, time):
        self.player.update_postgame(time)

    def teardown(self): 
        self.player.teardown_postgame()

    # }}}1

if __name__ == "__main__":
    loop = PongLoop()
    loop.play()


