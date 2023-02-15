# pylint: disable=line-too-long,import-error,unused-import,too-many-locals,invalid-name,unused-variable,too-many-statements,invalid-envvar-default,too-few-public-methods
import os
import board
import rgbmatrix

class LedPanel():
    """simple class to define a panel instance
    """

    def __init__(self):
        # see https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython/advanced-multiple-panels
        # for details on the tile/serpentine/chain values

        # note: these values are read from settings.toml, only available in CircuitPython 8.0 and later
        # fmt: off
        mx_base_width = os.getenv("mx_base_width", 32)  # width of a single panel
        mx_base_height = os.getenv("mx_base_height", 32)  # height of a single panel
        mx_bit_depth = os.getenv("mx_bit_depth", 3)  # valid values: 1-6
        mx_chain_across = os.getenv("mx_chain_across", 1)  # number of panels across
        mx_tile_down = os.getenv("mx_tile_down", 1)  # number of panels high
        mx_serpentine = (os.getenv("mx_serpentine") == "True", "True")  # whether alternate panels are rotated to shorten cabling
        # fmt: on

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
        # fmt: off
        mx_addr_pins_32 = [board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD]
        mx_addr_pins_64 = [board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD, board.MTX_ADDRE]
        # fmt: on
        mx_clock_pin = board.MTX_CLK
        mx_latch_pin = board.MTX_LAT
        mx_output_enable_pin = board.MTX_OE

        # create the matrix
        self.matrix = rgbmatrix.RGBMatrix(
            width=mx_width,
            height=mx_height,
            bit_depth=mx_bit_depth,
            tile=mx_tile_down,
            serpentine=mx_serpentine,
            rgb_pins=mx_rgb_pins,
            addr_pins=mx_addr_pins_64 if mx_base_height == 64 else mx_addr_pins_32,
            clock_pin=mx_clock_pin,
            latch_pin=mx_latch_pin,
            output_enable_pin=mx_output_enable_pin,
        )
