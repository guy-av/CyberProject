import math
import game


class GameObject:
    def __init__(self, t: int, c: tuple, x: float, y: float, w: int, h: int) -> None:
        self.x: float = x
        self.y: float = y

        self.width: int = w
        self.height: int = h

        self.type: int = t
        self.color: tuple = c

        self.angle: int = 0
        self.rotation_dir: int = 1
        self.is_rotating: bool = False
        self.times_rotated: int = 0

    def get_rect(self) -> tuple:
        return self.x, self.y, self.width, self.height

    def is_colliding(self, rect: tuple) -> bool:
        return self.x < rect[0] + rect[2] and \
               self.x + self.width > rect[0] and \
               self.y < rect[1] + rect[3] and \
               self.y + self.height > rect[1]

    def on_rotation_stop(self) -> None:
        pass

    def rotate_gravity(self, rd: int) -> None:
        self.is_rotating = True
        self.rotation_dir = rd

        if rd > 0:
            self.times_rotated += 1
        else:
            self.times_rotated -= 1

        if self.times_rotated == 4:
            self.times_rotated = 0
        elif self.times_rotated == -1:
            self.times_rotated = 3

    def rotate_position(self) -> None:
        self.angle += 1.5 * self.rotation_dir

        if self.angle in (-90, 90):
            hw: float = game.Game.WIDTH / 2
            hh: float = game.Game.HEIGHT / 2
            shw: float = self.width / 2
            shh: float = self.height / 2

            x: float = self.x + shw - hw
            y: float = self.y + shh - hh
            a: float = self.angle * math.pi / 180

            tx: float = x * math.cos(a) + y * math.sin(a)
            ty: float = (-x) * math.sin(a) - y * math.cos(a)

            self.width, self.height = self.height, self.width

            shw, shh = self.width / 2, self.height / 2

            self.x = tx + hw - shw
            self.y = ty + hh - shh

            self.is_rotating = False

            self.angle = 0

            if game.Game.is_rotating:
                game.Game.is_rotating = False

            self.on_rotation_stop()

    def clear(self, surface, pyg) -> None:
        pyg.draw.rect(surface, game.Game.COLOR_BACKGROUND, self.get_rect())
        pyg.draw.rect(surface, game.Game.COLOR_BACKGROUND, self.get_rect(), 2)

    def draw_shape(self, surface, pyg) -> None:
        pyg.draw.rect(surface, self.color, self.get_rect())
        pyg.draw.rect(surface, game.Game.COLOR_BLACK, self.get_rect(), 2)

    def update(self) -> None:
        if self.is_rotating:
            self.rotate_position()

    def render(self, surface, pyg) -> None:
        if self.is_rotating:
            sur: pyg.Surface = pyg.Surface((game.Game.WIDTH, game.Game.HEIGHT))
            sur.fill(game.Game.COLOR_BACKGROUND)
            sur.set_colorkey(game.Game.COLOR_BACKGROUND)

            self.draw_shape(sur, pyg)

            rotated: pyg.Surface = pyg.transform.rotate(sur, self.angle)
            rotated_rect: pyg.Surface = rotated.get_rect()
            rotated_rect.center = (game.Game.WIDTH / 2, game.Game.HEIGHT / 2)
            surface.blit(rotated, rotated_rect)
        else:
            self.draw_shape(surface, pyg)


class Block(GameObject):
    def __init__(self, x: float, y: float, w: int, h: int) -> None:
        super().__init__(game.Game.TYPE_BLOCK, game.Game.COLOR_BLOCK, x, y, w, h)


class Door(GameObject):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(game.Game.TYPE_DOOR, game.Game.COLOR_DOOR, x, y, 10, 100)

        self.is_open: bool = False
        self.is_animating_closure: bool = False
        self.open_towards_up: bool = True

    def open(self) -> None:
        self.is_animating_closure = True
        self.open_towards_up = True if self.height > self.width else False

    def rotate_gravity(self, rd: int) -> None:
        super().rotate_gravity(rd)

        if self.is_animating_closure:
            self.open_towards_up = not self.open_towards_up

    def update(self) -> None:
        super().update()

        if self.is_animating_closure and self.height > 0 and self.width > 0:
            if not self.is_rotating:
                if self.open_towards_up:
                    if self.times_rotated == 2:
                        self.y += 1
                        self.height -= 1
                    else:
                        self.height -= 1
                else:
                    if self.times_rotated == 3:
                        self.x += 1
                        self.width -= 1
                    else:
                        self.width -= 1
        elif (self.height == 0 or self.width == 0) and not self.is_open:
            self.is_open = True

    def render(self, surface, pyg) -> None:
        super().render(surface, pyg)


class SpringBoard(GameObject):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(game.Game.TYPE_SPRINGBOARD, game.Game.COLOR_SPRINGBOARD, x, y, 80, 10)

    def draw_shape(self, surface, pyg) -> None:
        pyg.draw.rect(surface, self.color[0], (self.x, self.y, self.width, 10))
        pyg.draw.rect(surface, game.Game.COLOR_BLACK, (self.x, self.y, self.width, 10), 2)

        pyg.draw.rect(surface, self.color[1], (self.x + 30, self.y + 10, 20, 10))
        pyg.draw.rect(surface, game.Game.COLOR_BLACK, (self.x + 30, self.y + 10, 20, 10), 2)
