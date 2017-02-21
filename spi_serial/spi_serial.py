import mraa as m
import time

import gpio
import spidev

import logging
logging.basicConfig(level=logging.ERROR)
#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

GPIO_RESET_PIN=14
SPI_BUS=5
SPI_DEVICE=1
DELAY_USEC=1
SPEED_HZ=62500
BITS_PER_WORD=8

class SpiSerial():
    def __init__(self):
        #self.cs0 = m.Gpio(23)
        #self.cs0.dir(m.DIR_OUT)
        #self.cs0.write(1)
        self.dev = spidev.SpiDev()
        self.dev.open(SPI_BUS, SPI_DEVICE)
        #self.dev = m.spiFromDesc("spi-raw-5-1")
        self.dev.max_speed_hz=SPEED_HZ
        #self.dev.frequency(62500)
        self.dev.mode=0b00
        self.dev.bits_per_word=BITS_PER_WORD
        #self.timeout = 0
        self.rx_buf = []

    def spi_xfer(self, b):
        tx = bytearray(1)
        tx[0] = (int('{:08b}'.format(b)[::-1], 2))
        rxbuf = self.dev.xfer(list(tx), SPEED_HZ, DELAY_USEC, BITS_PER_WORD)
        #print "rx=%s" % rxbuf
        return (int('{:08b}'.format(rxbuf[0])[::-1], 2))

    def close(self):
        pass

    def write(self, tx_bytes):
        tx_bytes = bytearray(tx_bytes)
        self.spi_xfer(0x99)
        num_rxd = self.spi_xfer(len(tx_bytes))
        for y in range(0, len(tx_bytes)):
            rx = self.spi_xfer(tx_bytes[y])
            if num_rxd > 0:
                self.rx_buf.append(rx)
                num_rxd -= 1
        for y in range(0, num_rxd):
            rx = self.spi_xfer(0)
            self.rx_buf.append(rx)

    def read(self, num_bytes=0):
        if num_bytes == 0:
            num_bytes = len(self.rx_buf)
        ret_val = self.rx_buf[0:num_bytes]
        del(self.rx_buf[0:num_bytes])
        return ret_val
        
    def peek(self):
        return self.rx_buf[0]
        
    def pop(self):
        return self.read(1)

    def inWaiting(self):
        self.spi_xfer(0x99)
        num_rxd = self.spi_xfer(0)
        for y in range(0, num_rxd):
            rx = self.spi_xfer(0)
            self.rx_buf.append(rx)
        return len(self.rx_buf)

    def reset(self):
        #self.RST = m.Gpio(36)
        #self.RST.dir(m.DIR_OUT)
        #self.RST.write(0)   # reset the device
        gpio.setup(GPIO_RESET_PIN, gpio.OUT)
        gpio.set(GPIO_RESET_PIN, 0)
        time.sleep(0.01)
        gpio.set(GPIO_RESET_PIN, 1)
        #self.RST.write(1)   # let the device out of reset
        time.sleep(2.01)    # wait for the CC1110 to come up
        # TODO: change the CC1110 code to not have a 2s delay
