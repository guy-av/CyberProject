import game

from game_objects import GameObject
from power_ups import PowerUp


class Obstacle(GameObject):
    def __init__(self, t: int, c: tuple, x: float, y: float, w: int, h: int) -> None:
        super().__init__(t, c, x, y, w, h)


class Spikes(Obstacle):
    def __init__(self, x: float, y: float, w: int, h: int, d: int) -> None:
        super().__init__(game.Game.TYPE_SPIKES, game.Game.COLOR_SPIKES, x, y, w, h)

        self.dir: int = d

    def on_rotation_stop(self) -> None:
        if self.rotation_dir == game.Game.LEFT:
            if self.times_rotated % 2 == 0:
                self.dir *= -1
        elif self.rotation_dir == game.Game.RIGHT:
            if self.times_rotated % 2 != 0:
                self.dir *= -1

    def draw_shape(self, surface, pyg) -> None:
        if self.width > self.height:
            self.x = int(self.x)
            for x in range(self.x, self.x + self.width, 10):
                if self.dir == 1:
                    points: tuple = ((x, self.y), (x + 5, self.y + self.height), (x + 10, self.y))
                else:
                    y = self.y + self.height
                    points: tuple = ((x, y), (x + 5, y - self.height), (x + 10, y))

                pyg.draw.polygon(surface, self.color, points)
                pyg.draw.polygon(surface, game.Game.COLOR_BLACK, points, 1)
        else:
            self.y = int(self.y)
            for y in range(self.y, self.y + self.height, 10):
                if self.dir == 1:
                    points: tuple = ((self.x, y), (self.x + self.width, y + 5), (self.x, y + 10))
                else:
                    x = self.x + self.width
                    points: tuple = ((x, y), (x - self.width, y + 5), (x, y + 10))

                pyg.draw.polygon(surface, self.color, points)
                pyg.draw.polygon(surface, game.Game.COLOR_BLACK, points, 1)


class Crossbow(GameObject):
    count = 0

    class Arrow(GameObject):
        def __init__(self, x: float, y: float, dx: int, dy: int) -> None:
            super().__init__(game.Game.TYPE_ARROW, game.Game.COLOR_ARROW, x, y, 30, 9)

            self.ox: float = x
            self.oy: float = y

            self.vx: float = 10 * dx
            self.vy: float = 10 * dy

            if self.vy != 0:
                self.width, self.height = self.height, self.width

            self.is_launched: bool = False

        def get_rect(self) -> tuple:
            return self.x, self.y + 3, self.width, self.height - 6

        def render(self, surface, pyg) -> None:
            image: pyg.Surface = game.Game.sprite_arrow
            image_surf: pyg.Surface = image.convert()
            image_surf = pyg.transform.rotate(
                image_surf,
                0 if self.vx > 0 else
                180 if self.vx < 0 else
                90 if self.vy < 0 else
                270 if self.vy > 0 else 0
            )
            image_surf.set_colorkey((255, 255, 255))
            surface.blit(image_surf, (self.x, self.y))

        def update(self) -> None:
            self.x += self.vx
            self.y += self.vy

            for b in game.Game.levels[game.Game.current_level]:
                if b.type == game.Game.TYPE_CROSSBOW or b.__class__.__bases__[0] == PowerUp:
                    continue

                if self.is_colliding(b.get_rect()):
                    self.x, self.y = self.ox, self.oy
                    self.is_launched = False
                    break

    def __init__(self, x: float, y: float, dx: int, dy: int) -> None:
        super().__init__(game.Game.TYPE_CROSSBOW, game.Game.COLOR_CROSSBOW, x, y, 40, 30)

        if dy != 0:
            self.width, self.height = self.height, self.width

        x = x + (self.width - 30) / 2 if dx != 0 else x + (self.width - 29) / 2 + 10
        y = y + (self.height - 29) / 2 + 10 if dx != 0 else y + (self.height - 30) / 2

        self.arrow: Crossbow.Arrow = Crossbow.Arrow(x, y, dx, dy)
        self.count: int = 0

        self.dx: int = dx
        self.dy: int = dy

        self.timing = 40 + (Crossbow.count * 5 if Crossbow.count % 3 == 0 else Crossbow.count * -5)
        Crossbow.count += 1

    def draw_shape(self, surface, pyg) -> None:
        if self.dx != 0:
            pyg.draw.rect(surface, self.color, (self.x, self.y, self.width, 10))
            pyg.draw.rect(surface, game.Game.COLOR_BLACK, (self.x, self.y, self.width, 10), 2)

            pyg.draw.rect(surface, self.color, (self.x, self.y + 20, self.width, 10))
            pyg.draw.rect(surface, game.Game.COLOR_BLACK, (self.x, self.y + 20, self.width, 10), 2)
        else:
            pyg.draw.rect(surface, self.color, (self.x, self.y, 10, self.height))
            pyg.draw.rect(surface, game.Game.COLOR_BLACK, (self.x, self.y, 10, self.height), 2)

            pyg.draw.rect(surface, self.color, (self.x + 20, self.y, 10, self.height))
            pyg.draw.rect(surface, game.Game.COLOR_BLACK, (self.x + 20, self.y, 10, self.height), 2)

        x: float = self.x + self.width - 10 if self.dx < 0 else \
            self.x if self.dx > 0 else \
                self.x + 10 if self.dy != 0 else 0

        y: float = self.y + 10 if self.dx != 0 else \
            self.y + self.height - 10 if self.dy < 0 else \
                self.y if self.dy > 0 else 0

        w = 10 if self.dx != 0 else self.width - 20 if self.dy != 0 else 0
        h = self.height - 20 if self.dx != 0 else 10 if self.dy != 0 else 0

        pyg.draw.rect(surface, self.color, (x, y, w, h))
        pyg.draw.rect(surface, game.Game.COLOR_BLACK, (x, y, w, h), 2)

    def update(self) -> None:
        super().update()

        if not self.arrow.is_launched:
            self.count += 1
        if self.count >= self.timing:
            self.arrow.is_launched = True
            self.count = 0

        if self.arrow.is_launched:
            self.arrow.update()

    def render(self, surface, pyg) -> None:
        super().render(surface, pyg)

        if self.arrow.is_launched:
            self.arrow.render(surface, pyg)
