# pylint: disable=line-too-long,import-error,unused-import,too-many-locals,invalid-name,unused-variable
"""
sample.py
very basic matrixportal code
not for individual resale
"""
import time
import os
import sys
import board
import busio
import displayio
import framebufferio
import rgbmatrix
import terminalio
from rainbowio import colorwheel
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests
import adafruit_lis3dh  # accelerometer
import adafruit_ds3231  # RTC

try:
    from _secrets import af_secrets as secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

def main():
    """
    they call it main.
    """

    board_type = os.uname().machine
    if "Matrix Portal M4" not in board_type:
        print(f"unsupported board type: {board_type}")
        print("this code is designed to run on MatrixPortal M4")
        sys.exit(1)

    # get rid of any pre-existing display
    displayio.release_displays()

    # see https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython/advanced-multiple-panels
    # for details on the tile/serpentine/chain values

    mx_base_width = 64  # width of a single panel
    mx_base_height = 32  # height of a single panel
    mx_bit_depth = 6  # valid values: 1-6
    mx_chain_across = 1  # number of panels across
    mx_tile_down = 1  # number of panels high
    mx_serpentine = True  # whether alternate panels are rotated to shorten cabling

    mx_width = mx_base_width * mx_chain_across
    mx_height = mx_base_height * mx_tile_down

    # matrixportal M4 pins
    mx_rgb_pins = [
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2,
    ]
    mx_addr_pins = [board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD]
    mx_addr_pins_64 = [
        board.MTX_ADDRA,
        board.MTX_ADDRB,
        board.MTX_ADDRC,
        board.MTX_ADDRD,
        board.MTX_ADDRE,
    ]
    mx_clock_pin = board.MTX_CLK
    mx_latch_pin = board.MTX_LAT
    mx_output_enable_pin = board.MTX_OE

    # create the matrix
    matrix = rgbmatrix.RGBMatrix(
        width=mx_width,
        height=mx_height,
        bit_depth=mx_bit_depth,
        tile=mx_tile_down,
        serpentine=mx_serpentine,
        rgb_pins=mx_rgb_pins,
        addr_pins=mx_addr_pins_64 if mx_base_height==64 else mx_addr_pins,
        clock_pin=mx_clock_pin,
        latch_pin=mx_latch_pin,
        output_enable_pin=mx_output_enable_pin,
    )

    mx_auto_refresh = True  # or False if refreshing the display manually
    display = framebufferio.FramebufferDisplay(matrix, auto_refresh=mx_auto_refresh)

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

if __name__ == "__main__":
    main()
