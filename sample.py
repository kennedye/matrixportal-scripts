"""
sample.py
very basic interstate75/matrixportal code
not for individual resale
"""
# pylint: disable=import-error,unused-import
import time
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
from rainbowio import colorwheel

# get rid of any pre-existing display
displayio.release_displays()

# see https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython/advanced-multiple-panels
# for details on the tile/serpentine/chain values

MX_BASE_WIDTH = 64  # width of a single panel
MX_BASE_HEIGHT = 32  # height of a single panel
MX_BIT_DEPTH = 6  # valid values: 1-6
MX_CHAIN_ACROSS = 1  # number of panels across
MX_TILE_DOWN = 1  # number of panels high
MX_SERPENTINE = True  # whether alternate panels are rotated to shorten cabling

MX_WIDTH = MX_BASE_WIDTH * MX_CHAIN_ACROSS
MX_HEIGHT = MX_BASE_HEIGHT * MX_TILE_DOWN

# don't forget to comment out whichever one you're not using below!

# interstate_75 pins
mx_rgb_pins = [board.R0, board.G0, board.B0, board.R1, board.G1, board.B1]
mx_addr_pins = [board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D]
mx_addr_pins_64 = [board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D, board.ROW_E]
mx_clock_pin = board.CLK
mx_latck_pin = board.LAT
mx_output_enable_pin = board.OE

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
    width=MX_WIDTH,
    height=MX_HEIGHT,
    bit_depth=MX_BIT_DEPTH,
    tile=MX_TILE_DOWN,
    serpentine=MX_SERPENTINE,
    rgb_pins=mx_rgb_pins,
    addr_pins=mx_addr_pins,  # use mx_addr_pins_64 when using 64x64 panels
    clock_pin=mx_clock_pin,
    latch_pin=mx_latch_pin,
    output_enable_pin=mx_output_enable_pin,
)

MX_AUTO_REFRESH = True  # or False if refreshing the display manually
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=MX_AUTO_REFRESH)

master_group = displayio.Group()

display.show(master_group)
