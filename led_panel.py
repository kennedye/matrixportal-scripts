# pylint: disable=import-error,unused-import
import os
import board
import rgbmatrix


class LedPanel:
    """simple class to define a panel instance"""

    def __init__(self):
        # see https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython/advanced-multiple-panels
        # for details on the tile/serpentine/chain values

        # note: these values are read from settings.toml, only available in CircuitPython 8.0 and later
        # fmt: off
        panel_base_width = os.getenv("mx_base_width", "32")  # width of a single panel
        panel_base_height = os.getenv("mx_base_height", "32")  # height of a single panel
        panel_bit_depth = os.getenv("mx_bit_depth", "3")  # valid values: 1-6
        panel_chain_across = os.getenv("mx_chain_across", "1")  # number of panels across
        panel_tile_down = os.getenv("mx_tile_down", "1")  # number of panels high
        panel_serpentine = (os.getenv("mx_serpentine") == "True", "True")  # whether alternate panels are rotated to shorten cabling
        # fmt: on

        panel_width = panel_base_width * panel_chain_across
        panel_height = panel_base_height * panel_tile_down

        # what kind of board are we
        if (
            "MatrixPortal S3" in os.uname().machine
            or "Matrix Portal M4" in os.uname().machine
        ):  # Adafruit Matrix Portal M4/S3
            panel_rgb_pins = [
                board.MTX_R1,
                board.MTX_G1,
                board.MTX_B1,
                board.MTX_R2,
                board.MTX_G2,
                board.MTX_B2,
            ]
            panel_addr_pins = [
                board.MTX_ADDRA,
                board.MTX_ADDRB,
                board.MTX_ADDRC,
                board.MTX_ADDRD,
            ]
            if panel_base_height > 32:
                panel_addr_pins.append(board.MTX_ADDRE)
            panel_clock_pin = board.MTX_CLK
            panel_latch_pin = board.MTX_LAT
            panel_output_enable_pin = board.MTX_OE

        elif "Pimoroni Interstate 75" in os.uname().machine:  # regular Interstate 75
            panel_rgb_pins = [
                board.R0,
                board.G0,
                board.B0,
                board.R1,
                board.G1,
                board.B1,
            ]
            panel_addr_pins = [board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D]
            if panel_base_height > 32:
                panel_addr_pins.append(board.ROW_E)
            panel_clock_pin = board.CLK
            panel_latch_pin = board.LAT
            panel_output_enable_pin = board.OE

        elif "Raspberry Pi Pico W with rp2040" in os.uname().machine:  # Interstate 75 W
            panel_rgb_pins = [
                board.GP0,
                board.GP1,
                board.GP2,
                board.GP3,
                board.GP4,
                board.GP5,
            ]
            panel_addr_pins = [board.GP6, board.GP7, board.GP8, board.GP9]
            if panel_base_height > 32:
                panel_addr_pins.append(board.GP10)
            panel_clock_pin = board.GP11
            panel_latch_pin = board.GP12
            panel_output_enable_pin = board.GP13

        # create the matrix
        self.matrix = rgbmatrix.RGBMatrix(
            width=panel_width,
            height=panel_height,
            bit_depth=panel_bit_depth,
            tile=panel_tile_down,
            serpentine=panel_serpentine,
            rgb_pins=panel_rgb_pins,
            addr_pins=panel_addr_pins,
            clock_pin=panel_clock_pin,
            latch_pin=panel_latch_pin,
            output_enable_pin=panel_output_enable_pin,
        )
