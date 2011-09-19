#!/usr/bin/env python

from game import *
from world import *

from utilities.core import *
from utilities.messaging import Forum

class GameEngine(SerialEngine):

    def __init__(self, loop):
        SerialEngine.__init__(self, loop)

        self.forum = Forum()

        self.publisher = self.forum.get_publisher()
        self.subscriber = self.forum.get_subscriber()
        self.member = self.forum.get_member()

        self.world = World()
        self.game = Game(self)

        self.tasks = {}

    def get_world(self):
        return self.world

    def get_game(self):
        return self.game

    def get_publisher(self):
        return self.publisher

    def get_subscriber(self):
        return self.subscriber

    def get_member(self):
        return self.member

    def setup(self):
        self.game.setup()
        SerialEngine.setup(self)

        self.forum.lock()

    def update(self, time):
        SerialEngine.update(self, time)

        self.forum.deliver()
        self.game.update(time)

    def teardown(self):
        SerialEngine.teardown(self)
        self.game.teardown()

class PongLoop(Loop):

    def __init__(self):
        self.engine = PongEngine(self)

class PongEngine(GameEngine):

    def __init__(self, loop):
        GameEngine.__init__(self, loop)

        self.tasks = {
                "triggers" : Triggers(self),
                "player" : Player(self),
                "opponent" : Opponent(self) }

    def successor(self):
        player = self.tasks["player"]
        return PostgameEngine(self.loop, self.world, player)

class PostgameEngine(Engine):

    def __init__(self, loop, world, player):
        Engine.__init__(self, loop)

        self.world = world
        self.player = player

    def setup(self): pass
    def teardown(self): pass

    def update(self, time):
        self.player.update(time)

if __name__ == "__main__":
    loop = PongLoop()
    loop.play()


