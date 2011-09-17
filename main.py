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

        self.world = World()
        self.game = Game(self.world, self.subscriber)

        self.tasks = {}

    def get_world(self):
        return self.world

    def get_game(self):
        return self.game

    def get_publisher(self):
        return self.publisher

    def get_subscriber(self):
        return self.subscriber

    def setup(self):
        SerialEngine.setup(self)

        self.game.setup()
        self.forum.lock()

    def update(self, time):
        SerialEngine.update(self, time)

        self.forum.deliver()
        self.game.update(time)

    def teardown(self):
        SerialEngine.teardown(self)
        self.game.teardown()

    def exit(self):
        return bool(self.world.winner)

class PongLoop(Loop):

    def __init__(self):
        self.engine = PongEngine(self)

class PongEngine(GameEngine):

    def __init__(self, loop):
        GameEngine.__init__(self, loop)

        world = self.world
        publisher = self.publisher

        self.tasks = {
                "triggers" : Triggers(world, publisher),
                "player" : Player(world, publisher),
                "opponent" : Opponent(world, publisher) }

if __name__ == "__main__":
    loop = PongLoop()
    loop.play()


