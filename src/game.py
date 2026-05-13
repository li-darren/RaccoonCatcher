import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COL_BG


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Shared game state (mutated by states via self.game)
        self.score = 0
        self.level = 1
        self.timer_remaining = 0.0
        self.target_zone = 0
        self.camera_room_elapsed = 0.0
        self.raccoons_paused = False

        # Import systems here to avoid circular imports at module level
        from src.systems.level_config import LEVELS
        from src.systems.zone_manager import ZoneManager
        from src.systems.raccoon_manager import RaccoonManager

        self.level_config = LEVELS[0]
        self.zone_manager = ZoneManager()
        self.raccoon_manager = RaccoonManager(self)

        # Build all states after systems are ready
        from src.states.menu_state import MenuState
        from src.states.camera_state import CameraState
        from src.states.transition_state import TransitionState
        from src.states.yard_state import YardState
        from src.states.result_state import ResultState
        from src.states.level_complete_state import LevelCompleteState
        from src.states.game_over_state import GameOverState

        self.states = {
            "menu": MenuState(self),
            "camera": CameraState(self),
            "transition": TransitionState(self),
            "yard": YardState(self),
            "result": ResultState(self),
            "level_complete": LevelCompleteState(self),
            "game_over": GameOverState(self),
        }
        self.current_state = self.states["menu"]
        self.current_state.on_enter({})

    def change_state(self, name: str, **kwargs):
        self.current_state.on_exit()
        self.current_state = self.states[name]
        self.current_state.on_enter(kwargs)

    def reset_level(self, level_num: int):
        from src.systems.level_config import LEVELS
        idx = min(level_num - 1, len(LEVELS) - 1)
        self.level = level_num
        self.level_config = LEVELS[idx]
        self.score = 0
        self.timer_remaining = self.level_config.time_limit_sec
        self.camera_room_elapsed = 0.0
        self.raccoons_paused = False
        self.raccoon_manager.populate(self.level_config)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.current_state.handle_event(event)

            self.current_state.update(dt)
            self.screen.fill(COL_BG)
            self.current_state.draw(self.screen)
            pygame.display.flip()
