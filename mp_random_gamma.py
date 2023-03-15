# pylint: disable=line-too-long,import-error,unused-import,too-many-locals,invalid-name,unused-variable,too-many-statements,invalid-envvar-default
"""
mp_random_gamma.py
draw some random dots over and over
now featuring gamma correction!
"""
import time
import os
import sys
import random
import board
import busio
import displayio
import framebufferio
import rgbmatrix
# import terminalio
from rainbowio import colorwheel
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests
import adafruit_lis3dh  # accelerometer
import adafruit_ds3231  # RTC
import adafruit_fancyled.adafruit_fancyled as fancy
from led_panel import LedPanel

try:
    from _secrets import af_secrets as secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


def compatibility_check():
    """
    basic checks to make sure the board and version are correct
    """
    board_type = os.uname().machine
    if "Matrix Portal M4" not in board_type:
        print(f"unsupported board type: {board_type}")
        print("this code is designed to run on MatrixPortal M4")
        sys.exit(1)
    cp_info = sys.implementation
    if cp_info.version[0] < 8:
        print(f"unsupported CircuitPython major version: {cp_info.version[0]}")
        print("this code is designed to run on CircuitPython 8.0 or later")
        sys.exit(1)


def main():
    """
    they call it main.
    """

    # is it safe
    compatibility_check()

    # get rid of any pre-existing display
    displayio.release_displays()

    panel = LedPanel()
    panel_auto_refresh = (os.getenv("panel_auto_refresh") == "True", "True")  # or False if refreshing the display manually
    display = framebufferio.FramebufferDisplay(panel.matrix, auto_refresh=panel_auto_refresh)

    master_group = displayio.Group()

    display.show(master_group)

    i2c = board.I2C()  # read for accelerometer and RTC

    # accelerometer - https://docs.circuitpython.org/projects/lis3dh/en/latest/
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
    # Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
    lis3dh.range = adafruit_lis3dh.RANGE_2_G
    # then do stuff with lis3dh.acceleration or the shake/tap functions

    # RTC - https://learn.adafruit.com/adafruit-ds3231-precision-rtc-breakout/circuitpython
    ds3231 = adafruit_ds3231.DS3231(i2c)
    current_time = ds3231.datetime  # struct_time

    # wifi
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
    wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
    # now do things like wifi.get() and wifi.post()

    bitmap = displayio.Bitmap(panel.matrix.width, panel.matrix.height, 256)
    palette = displayio.Palette(256)
    palette[0] = (0, 0, 0)
    for i in range(1, 254):
        r = random.randint(32, 96)
        g = random.randint(32, 96)
        b = random.randint(32, 96)
        gc = fancy.CRGB(r, g, b)
        gc = fancy.gamma_adjust(gc, gamma_value=1.8)
        palette[i] = gc.pack()
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    master_group.append(tile_grid)
    initial = time.monotonic()
    while True:
        x = random.randint(0, panel.matrix.width - 1)
        y = random.randint(0, panel.matrix.height - 1)
        color = random.randint(1, 254)
        if bitmap[x, y] == 0:
            bitmap[x, y] = color
        now = time.monotonic()
        if now - initial > 5:
            bitmap.fill(0)
            initial = now
            for i in range(1, 254):
                r = random.randint(1, 255)
                g = random.randint(1, 255)
                b = random.randint(1, 255)
                gc = fancy.CRGB(r, g, b)
                gc = fancy.gamma_adjust(gc)
                palette[i] = gc.pack()


if __name__ == "__main__":
    main()
