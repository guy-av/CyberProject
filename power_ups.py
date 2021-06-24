import game

from game_objects import GameObject


class PowerUp(GameObject):
    """
    Power up class representing the effects and keys which are distributed across all levels
    """
    def __init__(self, t: int, c: tuple, x: float, y: float) -> None:
        super().__init__(t, c, x, y, 20, 20)

        self.degree: int = 0
        self.collected: bool = False

    def collect(self) -> None:
        """
        Mark power up as collected
        """
        self.collected = True

        self.on_collect()

    def on_collect(self) -> None:
        """
        Placeholder for effects
        """
        pass

    def update(self) -> None:
        """
        Update rotation
        """
        super().update()

        self.degree += 1
        if self.degree == 360:
            self.degree = 0

    def render(self, surface, pyg) -> None:
        """
        Render the power up to the screen
        """
        if self.collected:
            return

        if self.is_rotating:
            sur: pyg.Surface = pyg.Surface((game.Game.WIDTH, game.Game.HEIGHT))
            sur.fill(game.Game.COLOR_BACKGROUND)
            sur.set_colorkey(game.Game.COLOR_BACKGROUND)

            ssur: pyg.Surface = pyg.Surface((self.width, self.height))
            ssur.fill(game.Game.COLOR_BACKGROUND)
            ssur.set_colorkey((0, 255, 0))

            pyg.draw.rect(ssur, self.color, (0, 0, self.width, self.height))
            pyg.draw.rect(ssur, game.Game.COLOR_BLACK, (0, 0, self.width, self.height), 1)

            sblitted: pyg.Surface = sur.blit(ssur, (self.x, self.y))
            srotated: pyg.Surface = pyg.transform.rotate(ssur, self.degree)
            srotated_rect: pyg.Surface = srotated.get_rect()
            srotated_rect.center = sblitted.center
            sur.blit(srotated, srotated_rect)

            rotated: pyg.Surface = pyg.transform.rotate(sur, self.angle)
            rotated_rect: pyg.Surface = rotated.get_rect()
            rotated_rect.center = (game.Game.WIDTH / 2, game.Game.HEIGHT / 2)
            surface.blit(rotated, rotated_rect)
        else:
            sur: pyg.Surface = pyg.Surface((self.width, self.height))
            sur.fill(game.Game.COLOR_BACKGROUND)
            sur.set_colorkey((0, 255, 0))

            pyg.draw.rect(sur, self.color, (0, 0, self.width, self.height))
            pyg.draw.rect(sur, game.Game.COLOR_BLACK, (0, 0, self.width, self.height), 1)

            blitted: pyg.Surface = surface.blit(sur, (self.x, self.y))
            rotated: pyg.Surface = pyg.transform.rotate(sur, self.degree)
            rotated_rect: pyg.Surface = rotated.get_rect()
            rotated_rect.center = blitted.center
            surface.blit(rotated, rotated_rect)


class Key(PowerUp):
    """
    A power up used to unlock doors and progress levels
    """
    def __init__(self, x: float, y: float) -> None:
        super().__init__(game.Game.TYPE_KEY, game.Game.COLOR_KEY, x, y)


class GravityRotator(PowerUp):
    """
    A power up used to rotate the level by 90 degrees
    """
    def __init__(self, x: float, y: float, rd: int) -> None:
        super().__init__(game.Game.TYPE_GRAVITY_ROTATOR, game.Game.COLOR_GRAVITY_ROTATOR, x, y)
        self.rotation_dir: int = rd

    def on_collect(self) -> None:
        game.Game.rotate(self.rotation_dir)


class Jet(PowerUp):
    """
    A power up used to levitate and float off the ground
    """
    def __init__(self, x: float, y: float) -> None:
        super().__init__(game.Game.TYPE_JET, game.Game.COLOR_JET, x, y)
