import game
import game_objects
import obstacles
import power_ups


class Player(game_objects.GameObject):
    """
    Player class, sets the actual player, and the "shadows" (other players on the game)
    """

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

        self.before: tuple = ()
        self.s_modifier: float = -10
        self.s_direction: int = 1
        self.level = 0

    def reset(self) -> None:
        """
        On contact with obstacle, reset the level
        """
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
        """
        Checks if player exits the "boundaries" (the screen size)
        """
        return self.x + self.width <= 0 or self.x >= game.Game.WIDTH or \
               self.y + self.height <= 0 or self.y >= game.Game.HEIGHT

    def die(self) -> None:
        """
        Kills player, unless is in God Testing Mode
        """
        if not game.Game.god_mode:
            tvx: float = self.vx
            self.reset()
            self.vx = tvx

            self.is_alive = False

    def fall(self) -> None:
        """
        Attract player towards ground
        """
        if self.is_floating:
            if self.vy > -1:
                self.vy += -0.02
        else:
            self.vy += game.Game.GRAVITY

    def jump(self) -> None:
        """
        Apply vertical velocity upwards to simulate player jumping
        """
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
        """
        On interaction with "Jet", levitate and float of the ground, ignoring gravity
        """
        self.before = (game.Game.frame_cycles, game.Game.frame_count)
        self.is_floating = True

        if self.vy < 0:
            self.vy *= 0.2
        else:
            self.vy = 0

    def start_left(self) -> None:
        """
        Start movement to the left
        """
        self.vx = -3

    def start_right(self) -> None:
        """
        Start movement to the right
        """
        self.vx = 3

    def stop_left(self) -> None:
        """
        Stop movement to the left
        """
        if self.vx == -3:
            self.vx = 0

    def stop_right(self) -> None:
        """
        Stop movement to the right
        """
        if self.vx == 3:
            self.vx = 0

    def check_miscellaneous(self, b) -> bool:
        """
        Check for intersection with miscellaneous obstacles
        """
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
        """
        Update position according to velocity
        """
        self.x += self.vx
        self.y += self.vy

    def update(self) -> None:
        """
        Update the player state in this frame
        """
        if game.Game.is_rotating:
            self.vy -= game.Game.GRAVITY
            return

        if self.is_floating:
            if (game.Game.frame_cycles * 60 + game.Game.frame_count) - (self.before[0] * 60 + self.before[1]) >= 240:
                self.is_floating = False

        self.update_pos()

        prev_x: float = self.x - self.vx
        prev_y: float = self.y - self.vy

        self.is_standing = False

        # check intersections on vertical axis
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

        # check intersections on horizontal axis
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

        if self.vx == 0 and self.vy == 0:
            self.s_modifier += 0.2 * self.s_direction
            if self.s_modifier > 10 or self.s_modifier < -10:
                self.s_direction *= -1
        else:
            self.s_modifier = -10

    def render(self, surface, pyg) -> None:
        """
        Render the player to the screen
        """
        pyg.draw.rect(surface, self.color, self.get_rect())
        pyg.draw.rect(surface, game.Game.COLOR_BLACK, self.get_rect(), 2)
