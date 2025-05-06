
from machine import Pin, SPI
import time, struct

def color565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

class ILI9341:
    def __init__(self, spi, cs, dc, rst, w=320, h=240, rot=1):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.w = w
        self.h = h
        self.rot = rot

        for pin in (cs, dc, rst):
            pin.init(pin.OUT, value=1)

        self.reset()
        self.init_display()

    def reset(self):
        self.rst(1)
        time.sleep_ms(50)
        self.rst(0)
        time.sleep_ms(50)
        self.rst(1)
        time.sleep_ms(150)

    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, data):
        self.dc(1)
        self.cs(0)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs(1)

    def init_display(self):
        self.write_cmd(0x01)
        time.sleep_ms(150)
        self.write_cmd(0x11)
        time.sleep_ms(500)
        self.write_cmd(0x3A)
        self.write_data(0x55)
        self.set_rotation(self.rot)
        self.write_cmd(0x29)
        time.sleep_ms(100)

    def set_rotation(self, rot):
        settings = [(0x48, 240, 320), (0x28, 320, 240), (0x88, 240, 320), (0xE8, 320, 240)]
        val, w, h = settings[rot % 4]
        self.write_cmd(0x36)
        self.write_data(val)
        self.w = w
        self.h = h

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data(struct.pack(">HH", x0, x1))
        self.write_cmd(0x2B)
        self.write_data(struct.pack(">HH", y0, y1))
        self.write_cmd(0x2C)

    def draw_pixel(self, x, y, color):
        self.set_window(x, y, x, y)
        self.write_data(struct.pack(">H", color))

    def fill(self, color):
        self.set_window(0, 0, self.w - 1, self.h - 1)
        self.dc(1)
        self.cs(0)
        data = struct.pack('>H', color) * 64
        for _ in range((self.w * self.h) // 64):
            self.spi.write(data)
        self.cs(1)

    def text_scaled(self, text, x, y, color, scale=2):
        for i, char in enumerate(text):
            self._draw_char(x + i * 6 * scale, y, char, color, scale)

    def _draw_char(self, x, y, char, color, scale):
        font = FONT.get(char, FONT.get('?'))
        for col, line in enumerate(font):
            for row in range(8):
                if line & (1 << row):
                    for dx in range(scale):
                        for dy in range(scale):
                            self.draw_pixel(x + col * scale + dx, y + row * scale + dy, color)

FONT = {
    'A': [126, 17, 17, 126],
    'B': [127, 73, 73, 54],
    'C': [62, 65, 65, 34],
    'D': [127, 65, 65, 62],
    'E': [127, 73, 73, 65],
    'F': [127, 9, 9, 1],
    'G': [62, 65, 81, 50],
    'H': [127, 8, 8, 127],
    'I': [65, 127, 65, 0],
    'J': [32, 64, 65, 63],
    'K': [127, 8, 20, 99],
    'L': [127, 64, 64, 64],
    'M': [127, 2, 4, 2, 127],
    'N': [127, 4, 8, 127],
    'O': [62, 65, 65, 62],
    'P': [127, 9, 9, 6],
    'Q': [62, 65, 81, 62, 64],
    'R': [127, 9, 25, 102],
    'S': [38, 73, 73, 50],
    'T': [1, 1, 127, 1, 1],
    'U': [63, 64, 64, 63],
    'V': [31, 32, 64, 32, 31],
    'W': [63, 64, 56, 64, 63],
    'X': [99, 20, 8, 20, 99],
    'Y': [7, 8, 112, 8, 7],
    'Z': [97, 81, 73, 69, 67],
    'a': [32, 84, 84, 120],
    'b': [127, 68, 68, 56],
    'c': [56, 68, 68, 40],
    'd': [56, 68, 68, 127],
    'e': [56, 84, 84, 24],
    'f': [8, 126, 9, 2],
    'g': [72, 84, 84, 60],
    'h': [127, 4, 4, 120],
    'i': [0, 68, 125, 64],
    'j': [32, 64, 68, 61],
    'k': [127, 16, 40, 68],
    'l': [0, 65, 127, 64],
    'm': [124, 4, 56, 4, 120],
    'n': [124, 4, 4, 120],
    'o': [56, 68, 68, 56],
    'p': [124, 20, 20, 8],
    'q': [8, 20, 20, 124],
    'r': [124, 8, 4, 4],
    's': [72, 84, 84, 36],
    't': [4, 63, 68, 64],
    'u': [60, 64, 64, 124],
    'v': [28, 32, 64, 32, 28],
    'w': [60, 64, 48, 64, 60],
    'x': [68, 40, 16, 40, 68],
    'y': [12, 80, 80, 60],
    'z': [68, 100, 84, 76],
    '0': [62, 69, 73, 62],
    '1': [0, 66, 127, 64],
    '2': [98, 81, 73, 70],
    '3': [34, 73, 73, 54],
    '4': [24, 20, 18, 127],
    '5': [47, 73, 73, 49],
    '6': [62, 73, 73, 50],
    '7': [1, 113, 9, 7],
    '8': [54, 73, 73, 54],
    '9': [38, 73, 73, 62],
    ':': [0, 54, 54, 0],
    '.': [0, 96, 96, 0],
    '?': [2, 89, 9, 6],
    '°': [6, 9, 9, 6],
    'C': [60, 66, 66, 36],
    ' ': [0, 0, 0, 0]
}


