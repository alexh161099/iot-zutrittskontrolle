from machine import Pin, SPI
import time

class MFRC522:

    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    def __init__(self, spi, cs, rst):
        self.spi = spi
        self.cs = cs
        self.rst = rst
        self.cs.init(self.cs.OUT, value=1)
        self.rst.init(self.rst.OUT, value=1)
        self.init()

    def _wreg(self, reg, val):
        self.cs(0)
        self.spi.write(bytearray([(reg << 1) & 0x7E]))
        self.spi.write(bytearray([val]))
        self.cs(1)

    def _rreg(self, reg):
        self.cs(0)
        self.spi.write(bytearray([((reg << 1) & 0x7E) | 0x80]))
        val = self.spi.read(1)[0]
        self.cs(1)
        return val

    def _setbitmask(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    def _clearbitmask(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def init(self):
        self.rst(1)
        self._wreg(0x01, 0x0F)
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        self._antenna_on()

    def _antenna_on(self, on=True):
        if on:
            self._setbitmask(0x14, 0x03)
        else:
            self._clearbitmask(0x14, 0x03)

    def request(self, mode):
        self._wreg(0x0D, 0x07)
        (status, back_data, back_bits) = self._tocard(0x0C, [mode])
        if status != self.OK or back_bits != 0x10:
            return (self.ERR, None)
        return (self.OK, back_data)

    def anticoll(self):
        ser_chk = 0
        ser = []
        self._wreg(0x0D, 0x00)
        (status, back_data, back_bits) = self._tocard(0x0C, [0x93, 0x20])
        if status != self.OK:
            return (self.ERR, None)
        if len(back_data) != 5:
            return (self.ERR, None)
        for i in range(4):
            ser_chk ^= back_data[i]
            ser.append(back_data[i])
        if ser_chk != back_data[4]:
            return (self.ERR, None)
        return (self.OK, ser)

    def _tocard(self, command, send):
        recv = []
        bits = irq_en = wait_irq = n = 0
        if command == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        if command == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)
        self._clearbitmask(0x04, 0x80)
        self._setbitmask(0x0A, 0x80)
        self._wreg(0x01, 0x00)

        for c in send:
            self._wreg(0x09, c)

        self._wreg(0x01, command)

        if command == 0x0C:
            self._setbitmask(0x0D, 0x80)

        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if not (i != 0 and not (n & 0x01) and not (n & wait_irq)):
                break

        self._clearbitmask(0x0D, 0x80)

        if i != 0:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                status = self.OK
                if n & irq_en & 0x01:
                    status = self.NOTAGERR
                if command == 0x0C:
                    n = self._rreg(0x0A)
                    last_bits = self._rreg(0x0C) & 0x07
                    if last_bits != 0:
                        bits = (n - 1) * 8 + last_bits
                    else:
                        bits = n * 8
                    if n == 0:
                        n = 1
                    if n > 16:
                        n = 16
                    for _ in range(n):
                        recv.append(self._rreg(0x09))
            else:
                status = self.ERR
        else:
            status = self.ERR
        return (status, recv, bits)
