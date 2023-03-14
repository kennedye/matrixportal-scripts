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

def make_rect(color: int, width: int, height: int) -> displayio.TileGrid:
    """
    create a "rounded" rectangle and return it as a single TileGrid
    """
    h_start = w_start = 0
    h_end = height - 1
    w_end = width - 1

    palette1 = displayio.Palette(3)
    palette1[0] = (color[0], color[1], color[2])  # the passed-in color
    palette1[1] = (
        int(color[0] * 0.1),
        int(color[1] * 0.1),
        int(color[2] * 0.1),
    )  # the passed-in color at 10%
    palette1[2] = (0, 0, 0)  # black

    bitmap1 = displayio.Bitmap(width, height, 3)

    bitmap1[w_start + 1, h_start] = 1
    bitmap1[w_end - 1, h_start] = 1
    bitmap1[w_start, h_start + 1] = 1
    bitmap1[w_end, h_start + 1] = 1
    bitmap1[w_start, h_end - 1] = 1
    bitmap1[w_end, h_end - 1] = 1
    bitmap1[w_start + 1, h_end] = 1
    bitmap1[w_end - 1, h_end] = 1

    bitmap1[w_start, h_start] = 2
    bitmap1[w_start, h_end] = 2
    bitmap1[w_end, h_start] = 2
    bitmap1[w_end, h_end] = 2

    return displayio.TileGrid(bitmap1, pixel_shader=palette1)


def move_down(rect: displayio.Group()) -> None:
    """
    move a rectangle's Group down (todo: add gravity?)
    """
    for i in range(10):
        time.sleep(0.025)
        rect.y = i


def move_up(rect: displayio.Group()) -> None:
    """
    move a rectangle's Group up (todo: add gravity?)
    """
    for i in range(9, -1, -1):
        time.sleep(0.025)
        rect.y = i


def main():
    """
    they call it main.
    """
    # get rid of any pre-existing display
    # get rid of any pre-existing display
    displayio.release_displays()

    # see https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython/advanced-multiple-panels
    # for details on the tile/serpentine/chain values

    MX_BASE_WIDTH = 32  # width of a single panel
    MX_BASE_HEIGHT = 32  # height of a single panel
    MX_BIT_DEPTH = 6  # valid values: 1-6
    MX_CHAIN_ACROSS = 1  # number of panels across
    MX_TILE_DOWN = 1  # number of panels high
    MX_SERPENTINE = True  # whether alternate panels are rotated to shorten cabling

    MX_WIDTH = MX_BASE_WIDTH * MX_CHAIN_ACROSS
    MX_HEIGHT = MX_BASE_HEIGHT * MX_TILE_DOWN

    # don't forget to comment out whichever one you're not using below!

    # interstate_75 pins
    # mx_rgb_pins = [board.R0, board.G0, board.B0, board.R1, board.G1, board.B1]
    # mx_addr_pins = [board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D]
    # mx_addr_pins_64 = [board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D, board.ROW_E]
    # mx_clock_pin = board.CLK
    # mx_latck_pin = board.LAT
    # mx_output_enable_pin = board.OE

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

    group_main = displayio.Group()
    display.show(group_main)

    color1 = (255, 165, 0)  # orange
    color2 = (173, 216, 230)  # light blue
    color3 = (0, 255, 0)  # green
    width = height = 10

    tile_grid1 = make_rect(color1, width, height)
    group1 = displayio.Group()
    group1.append(tile_grid1)

    group1.x = 0
    group1.y = 0

    tile_grid2 = make_rect(color2, width, height)
    group2 = displayio.Group()
    group2.append(tile_grid2)

    group2.x = 11
    group2.y = 0

    tile_grid3 = make_rect(color3, width, height)
    group3 = displayio.Group()
    group3.append(tile_grid3)

    group3.x = 22
    group3.y = 0

    group_main.append(group1)
    group_main.append(group2)
    group_main.append(group3)

    time.sleep(2)

    while True:
        move_down(group1)
        move_down(group2)
        move_down(group3)
        move_up(group1)
        move_up(group2)
        move_up(group3)


if __name__ == "__main__":
    main()
