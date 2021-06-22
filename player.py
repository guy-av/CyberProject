import game
import game_objects
import obstacles
import power_ups


class Player(game_objects.GameObject):
    def __init__(self, color) -> None:
        super().__init__(
            game.Game.TYPE_PLAYER, color,
            game.Game.start_points[game.Game.current_level][0],
            game.Game.start_points[game.Game.current_level][1], 40, 40
        )

        self.vx: float = 0
        self.vy: float = 0

        self.is_standing: bool = False
        self.is_floating: bool = False
        self.is_jumping: bool = False
        self.is_alive: bool = True
        self.keep_jumping: bool = False

        self.total_keys_collected: int = 0

        self.trail: list = []
        self.before: tuple = ()
        self.s_modifier: float = -10
        self.s_direction: int = 1
        self.level = 0

    def reset(self) -> None:
        self.x = game.Game.start_points[game.Game.current_level][0]
        self.y = game.Game.start_points[game.Game.current_level][1]

        self.vx = 0
        self.vy = 0

        self.is_standing = False
        self.is_floating = False
        self.is_jumping = False
        game.Game.is_floating = False

        self.total_keys_collected = 0

        self.before = ()
        self.s_modifier = -10
        self.s_direction = 1

    def passed(self) -> bool:
        return self.x + self.width <= 0 or self.x >= game.Game.WIDTH or \
               self.y + self.height <= 0 or self.y >= game.Game.HEIGHT

    def die(self) -> None:
        tvx: float = self.vx
        self.reset()
        self.vx = tvx

        self.is_alive = False

    def fall(self) -> None:
        if self.is_floating:
            if self.vy > -1:
                self.vy += -0.02
        else:
            self.vy += game.Game.GRAVITY

    def jump(self) -> None:
        if self.is_standing:
            self.vy = -5
            self.is_jumping = True
            self.keep_jumping = True
        elif self.is_jumping:
            if -8.5 < self.vy < 0 and self.keep_jumping:
                self.vy -= 1
            else:
                self.keep_jumping = False

    def float(self) -> None:
        self.before = (game.Game.frame_cycles, game.Game.frame_count)
        self.is_floating = True

        if self.vy < 0:
            self.vy *= 0.2
        else:
            self.vy = 0

    def start_left(self) -> None:
        self.vx = -3

    def start_right(self) -> None:
        self.vx = 3

    def stop_left(self) -> None:
        if self.vx == -3:
            self.vx = 0

    def stop_right(self) -> None:
        if self.vx == 3:
            self.vx = 0

    def check_miscellaneous(self, b) -> bool:
        if b.type == game.Game.TYPE_CROSSBOW:
            if self.is_colliding(b.arrow.get_rect()):
                self.die()
                return True

        if b.is_colliding(self.get_rect()):
            if b.__class__.__bases__[0] == power_ups.PowerUp:
                if not b.collected:
                    b.collect()

                    if b.type == game.Game.TYPE_KEY:
                        self.total_keys_collected += 1
                    elif b.type == game.Game.TYPE_JET:
                        self.float()
                    return True
                else:
                    return True

            elif b.__class__.__bases__[0] == obstacles.Obstacle:
                self.die()
                return True

            elif b.type == game.Game.TYPE_DOOR:
                if b.is_open:
                    return True

        return False

    def update_pos(self):
        self.x += self.vx
        self.y += self.vy

    def update(self) -> None:
        if game.Game.is_rotating:
            self.vy -= game.Game.GRAVITY
            self.trail = self.trail[1:]
            return

        if self.is_floating:
            if (game.Game.frame_cycles * 60 + game.Game.frame_count) - (self.before[0] * 60 + self.before[1]) >= 240:
                self.is_floating = False

        self.update_pos()

        prev_x: float = self.x - self.vx
        prev_y: float = self.y - self.vy

        self.is_standing = False

        for b in game.Game.get_level_objects():
            if self.check_miscellaneous(b):
                continue

            if b.is_colliding(self.get_rect()):
                if self.vy < 0 and prev_y >= b.y + b.height:
                    if prev_x == b.x + b.width or prev_x + self.width == b.x:
                        continue

                    self.y = b.y + b.height
                    self.vy = 0.5
                elif self.vy > 0 and prev_y + self.height <= b.y:
                    if prev_x == b.x + b.width or prev_x + self.width == b.x:
                        continue

                    self.y = b.y - self.height

                    if b.type == game.Game.TYPE_SPRINGBOARD:
                        if self.vy < 15:
                            self.vy *= -1.1
                        else:
                            self.vy *= -1
                    else:
                        self.vy = 0
                        self.is_standing = True
                        self.is_jumping = False

        for b in game.Game.get_level_objects():
            if self.check_miscellaneous(b):
                continue

            if b.is_colliding(self.get_rect()):
                if self.vx < 0 and prev_x >= b.x + b.width:
                    if self.is_standing and self.y == b.y:
                        continue

                    self.x = b.x + b.width

                    if self.vy > 0 and not self.is_floating:
                        self.vy -= game.Game.GRAVITY / 2
                elif self.vx > 0 and prev_x + self.width <= b.x:
                    if self.is_standing and self.y == b.y:
                        continue

                    self.x = b.x - self.width

                    if self.vy > 0 and not self.is_floating:
                        self.vy -= game.Game.GRAVITY / 2

        self.trail.append((self.x - self.vx, self.y - self.vy))

        if len(self.trail) == 5 or (self.vx == 0 and self.vy == 0):
            self.trail = self.trail[1:]

        if self.vx == 0 and self.vy == 0:
            self.s_modifier += 0.2 * self.s_direction
            if self.s_modifier > 10 or self.s_modifier < -10:
                self.s_direction *= -1
        else:
            self.s_modifier = -10

    def render(self, surface, pyg) -> None:
        # if not self.s_modifier >= 0:
        #     length: int = len(self.trail)
        #     for i in range(length):
        #         t: list = self.trail[i]
        #         w: int = self.width - (length - i) * 5
        #         h: int = self.height - (length - i) * 5
        #         x: float = t[0] + self.width / 2 - w / 2
        #         y: float = t[1] + self.height / 2 - h / 2
        #         c: tuple = (self.color[0] - (length - i) * 20, self.color[1], self.color[2])
        #         surf: pyg.Surface = pyg.Surface((w, h))
        #         pyg.draw.rect(surf, c, (0, 0, w, h))
        #         pyg.draw.rect(surf, game.Game.COLOR_BLACK, (0, 0, w, h), 2)
        #         surf.set_alpha(150 - (length - i) * 10)
        #         surface.blit(surf, (x, y))

        # if self.vx == 0 and self.vy == 0:
        #     s: float = self.s_modifier / 2
        #
        #     if self.s_modifier >= 0:
        #         pyg.draw.rect(surface, self.color, (self.x + s / 2, self.y + s, self.width - s, self.height - s))
        #         pyg.draw.rect(surface, game.Game.COLOR_BLACK,
        #                       (self.x + s / 2, self.y + s, self.width - s, self.height - s), 2)
        #     else:
        #         pyg.draw.rect(surface, self.color, self.get_rect())
        #         pyg.draw.rect(surface, game.Game.COLOR_BLACK, self.get_rect(), 2)
        # else:
        pyg.draw.rect(surface, self.color, self.get_rect())
        pyg.draw.rect(surface, game.Game.COLOR_BLACK, self.get_rect(), 2)
