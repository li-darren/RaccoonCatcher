from abc import ABC, abstractmethod


class BaseState(ABC):
    def __init__(self, game):
        self.game = game

    def on_enter(self, data: dict):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, screen):
        pass
