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
        panel_base_width = os.getenv("panel_base_width", 32)  # width of a single panel
        panel_base_height = os.getenv("panel_base_height", 32)  # height of a single panel
        panel_bit_depth = os.getenv("panel_bit_depth", 3)  # valid values: 1-6
        panel_chain_across = os.getenv("panel_chain_across", 1)  # number of panels across
        panel_tile_down = os.getenv("panel_tile_down", 1)  # number of panels high
        panel_serpentine = (os.getenv("panel_serpentine") == "True", "True")  # whether alternate panels are rotated to shorten cabling
        # fmt: on

        panel_width = panel_base_width * panel_chain_across
        panel_height = panel_base_height * panel_tile_down

        # what kind of board are we
        board_type = os.uname().machine
        if "Matrix Portal M4" in board_type:
            # matrixportal M4 pins
            panel_rgb_pins = [
                board.MTX_R1,
                board.MTX_G1,
                board.MTX_B1,
                board.MTX_R2,
                board.MTX_G2,
                board.MTX_B2,
            ]
            # fmt: off
            panel_addr_pins_32 = [board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD]
            panel_addr_pins_64 = [board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD, board.MTX_ADDRE]
            # fmt: on
            panel_clock_pin = board.MTX_CLK
            panel_latch_pin = board.MTX_LAT
            panel_output_enable_pin = board.MTX_OE

        elif "Pimoroni Interstate 75" in board_type:
            # interstate75 pins
            panel_rgb_pins = [
                board.R0,
                board.G0,
                board.B0,
                board.R1,
                board.G1,
                board.B1
            ]
            # fmt: off
            panel_addr_pins_32 = [board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D]
            panel_addr_pins_64 = [board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D, board.ROW_E]
            # fmt: on
            panel_clock_pin = board.CLK
            panel_latch_pin = board.LAT
            panel_output_enable_pin = board.OE

        # create the matrix
        self.matrix = rgbmatrix.RGBMatrix(
            width=panel_width,
            height=panel_height,
            bit_depth=panel_bit_depth,
            tile=panel_tile_down,
            serpentine=panel_serpentine,
            rgb_pins=panel_rgb_pins,
            addr_pins=panel_addr_pins_64 if panel_base_height == 64 else panel_addr_pins_32,
            clock_pin=panel_clock_pin,
            latch_pin=panel_latch_pin,
            output_enable_pin=panel_output_enable_pin,
        )
