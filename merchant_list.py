"""Fading text"""
import time
import pygame
import pytweening

class FadingName(object):
    """Text which slowly fades"""

    _text_color = (0x55, 0x55, 0x55)

    def __init__(self, x_loc, y_loc, text, font):
        self.created_time = time.time()
        self.life_time = 3
        self._text = text
        self._position = list((x_loc, y_loc))
        self._text_surface = font.render(self._text, True, self._text_color)
        rect = self._text_surface.get_rect()
        self._text_surface.convert_alpha()
        self._text_surface2 = pygame.surface.Surface(rect.size, pygame.SRCALPHA, 32)
        self._text_width = rect.width
        self._text_height = rect.height

    def is_alive(self):
        """Returns true if we are within lifetime, false otherwise"""
        return (time.time() - self.created_time) < self.life_time

    def life_factor(self):
        """Gets a scaling factor based on life remaining"""
        return (time.time() - self.created_time) / self.life_time

    def get_y(self):
        """Returns y position"""
        return self._position[1]

    def get_x(self):
        """Returns x position"""
        return self._position[0]

    def get_height(self):
        """Returns text height"""
        return self._text_height

    def get_width(self):
        return self._text_width

    def set_position(self, x_loc, y_loc):
        """Returns current position"""
        self._position = list((x_loc, y_loc))

    def draw(self, win):
        """Renders faded text to a display window"""
        fade = int(255 * (1 - self.life_factor()))
        self._text_surface2.fill((255, 255, 255, fade))
        self._text_surface2.blit(self._text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        text_pos = (self.get_x() - self._text_width/2, self.get_y() + 25)
        win.blit(self._text_surface2, text_pos)

class InterpolatingFadingName(FadingName):
    """Text which interpolates it's own position"""

    def __init__(self, x_loc, y_loc, text, font, animation_rate=50):
        super().__init__(x_loc, y_loc, text, font)
        self._animation_rate = animation_rate
        self._ticks_ago = 0
        self._target_position = list((x_loc, y_loc))

    def interpolate(self, value, target):
        """Interpolate a value based on animation_rate and ticks"""
        percent = 1.0 - (float((self._animation_rate - self._ticks_ago) / self._animation_rate))
        percent = pytweening.easeOutQuad(percent)
        if percent >= 1.0:
            return target
        interp = value + ((target - value) * percent)
        return interp

    def get_y(self):
        """Return y"""
        value = self.interpolate(self._position[1], self._target_position[1])
        if value == self._target_position[1]:
            self._position[1] = self._target_position[1]
        return value

    def get_x(self):
        """Return x"""
        value = self.interpolate(self._position[0], self._target_position[0])
        if value == self._target_position[0]:
            self._position[0] = self._target_position[0]
        return value

    def set_position(self, x_loc, y_loc):
        """Set the target position"""
        self._position = list((x_loc, y_loc))
        self._target_position = list((x_loc, y_loc))

    def move(self, x_dist, y_dist):
        self._position[0] = self.get_x()
        self._position[1] = self.get_y()
        self._target_position[0] += x_dist
        self._target_position[1] += y_dist
        self._ticks_ago = 0

    def tick(self):
        """Tick once"""
        self._ticks_ago = min(self._animation_rate, self._ticks_ago + 1)

class MerchantList(object):
    """Displays a list of merchant names

    Should smoothly animate adding new names and moving the list down."""
    _ROW_SPACING = 20

    def __init__(self, x_loc, y_loc, font, limit=15):
        self._limit = limit
        self._values = []
        self._position = (x_loc, y_loc)
        self._font = font

    def add(self, text):
        """Add a new value; drop old values"""
        for value in self._values:
            value.move(
                0,
                self._ROW_SPACING
            )
        new_value = InterpolatingFadingName(
            self._position[0],
            self._position[1] - self._ROW_SPACING,
            text,
            self._font
        )
        new_value.move(0, self._ROW_SPACING)
        self._values.append(new_value)

        if len(self._values) > self._limit:
            del self._values[-1]

    def draw(self, win):
        """Render names to a window"""
        for value in self._values:
            value.tick()
            if value.is_alive():
                value.draw(win)
            else:
                self._values.remove(value)
