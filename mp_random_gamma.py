# pylint: disable=line-too-long,import-error,unused-import,too-many-locals,unused-variable,too-many-statements,invalid-envvar-default
"""
mp_random_gamma.py
draw some random dots over and over
now featuring gamma correction!
"""
import time
import random
import os
import sys
import board
import busio
import displayio
import framebufferio
import rgbmatrix
import terminalio
import adafruit_fancyled.adafruit_fancyled as fancy
from rainbowio import colorwheel
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests
import adafruit_lis3dh  # accelerometer
import adafruit_ds3231  # RTC
from led_panel import LedPanel


# LED gamma correction table -
# https://learn.adafruit.com/led-tricks-gamma-correction/the-quick-fix
# fmt: off
# gamma = [
#     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
#     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
#     1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
#     2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
#     5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
#    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
#    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
#    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
#    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
#    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
#    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
#    90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
#   115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
#   144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
#   177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
#   215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255
# ]
# fmt: on


def get_secrets() -> dict:
    """
    retrieve wifi secrets from settings.toml
    (requires CircuitPython >= 8.0)
    """
    secrets = {
        "ssid": os.getenv("CIRCUITPY_WIFI_SSID"),
        "password": os.getenv("CIRCUITPY_WIFI_PASSWORD"),
    }
    if secrets == {"ssid": None, "password": None}:
        print("WiFi secrets are kept in settings.toml, please add them there!")
    return secrets


def compatibility_check() -> None:
    """
    basic checks to make sure the board and version are correct
    """
    if "Matrix" not in os.uname().machine:
        print(f"unsupported board type: {os.uname().machine}")
        print("this code is designed to run on MatrixPortal M4/S3")
        sys.exit(1)
    if sys.implementation.version[0] < 8:
        print(
            f"unsupported CircuitPython major version: {sys.implementation.version[0]}"
        )
        print("this code is designed to run on CircuitPython 8.0 or later")
        sys.exit(1)


def create_wifi_M4(
    wifi_secrets: dict,
) -> adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager:
    """
    set up a WifiManager structure
    """
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
    return adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(
        esp, wifi_secrets, status_light
    )


def main() -> None:
    """
    ...main.
    """

    # is it safe
    compatibility_check()

    # get rid of any pre-existing display
    displayio.release_displays()

    panel = LedPanel()
    panel_auto_refresh = (
        os.getenv("mx_auto_refresh") == "True",
        "True",
    )  # or False if refreshing the display manually
    display = framebufferio.FramebufferDisplay(
        panel.matrix, auto_refresh=panel_auto_refresh
    )

    master_group = displayio.Group()

    display.root_group = master_group

    i2c = board.I2C()  # read for accelerometer and RTC

    # accelerometer - https://docs.circuitpython.org/projects/lis3dh/en/latest/
    try:
        lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
        # Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
        lis3dh.range = adafruit_lis3dh.RANGE_2_G
        # then do stuff with lis3dh.acceleration or the shake/tap functions
    except ValueError as error:
        print(f"unable to initialize LIS3DH: {error}")

    # RTC - https://learn.adafruit.com/adafruit-ds3231-precision-rtc-breakout/circuitpython
    try:
        ds3231 = adafruit_ds3231.DS3231(i2c)
        current_time = ds3231.datetime  # struct_time
    except ValueError as error:
        print(f"unable to initialize DS3231: {error}")

    # if M4, create wifi object with secrets and use wifi.get() / wifi.post()
    if "Matrix Portal M4" in os.uname().machine:
        wifi = create_wifi_M4(get_secrets())

    # set up MatrixPortal buttons
    button_up = DigitalInOut(board.BUTTON_UP)
    button_down = DigitalInOut(board.BUTTON_DOWN)
    button_up.direction = button_down.direction = Direction.INPUT
    button_up.pull = button_down.pull = Pull.UP
    switch_up = Debouncer(button_up)
    switch_down = Debouncer(button_down)

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
    total_pixels = panel.matrix.width * panel.matrix.height
    colored_pixels = 0
    while True:
        # wifi.pixel_status((0, 255, 0))
        while colored_pixels < total_pixels:
            x = random.randint(0, panel.matrix.width - 1)
            y = random.randint(0, panel.matrix.height - 1)
            color = random.randint(32, 254)
            if bitmap[x, y] == 0:
                bitmap[x, y] = color
                colored_pixels += 1
        #                 print(f"colored pixels = {colored_pixels}")
        now = time.monotonic()
        if now - initial > 5:
            # wifi.pixel_status((0, 32, 0))
            color = 0
            while colored_pixels > 0:
                x = random.randint(0, panel.matrix.width - 1)
                y = random.randint(0, panel.matrix.height - 1)
                if bitmap[x, y] != color:
                    bitmap[x, y] = color
                    colored_pixels -= 1
            #                     print(f"colored pixels = {colored_pixels}")
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
