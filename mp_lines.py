# pylint: disable=line-too-long,import-error,unused-import,too-many-locals,invalid-name,unused-variable,too-many-statements,invalid-envvar-default
"""
mp_lines.py
a rainbow of lines
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


def make_palette_rgb():
    """
    build a rainbow palette
    of gamma-corrected values
    this should probably be a class
    so it can go in a separate file
    """
    palette = [None] * 192

    # red to orange
    palette[0] = (255, 0, 0)
    palette[1] = (255, 5, 0)
    palette[2] = (255, 11, 0)
    palette[3] = (255, 16, 0)
    palette[4] = (255, 21, 0)
    palette[5] = (255, 27, 0)
    palette[6] = (255, 32, 0)
    palette[7] = (255, 37, 0)
    palette[8] = (255, 43, 0)
    palette[9] = (255, 48, 0)
    palette[10] = (255, 53, 0)
    palette[11] = (255, 59, 0)
    palette[12] = (255, 64, 0)
    palette[13] = (255, 69, 0)
    palette[14] = (255, 75, 0)
    palette[15] = (255, 80, 0)
    palette[16] = (255, 85, 0)
    palette[17] = (255, 90, 0)
    palette[18] = (255, 96, 0)
    palette[19] = (255, 101, 0)
    palette[20] = (255, 106, 0)
    palette[21] = (255, 112, 0)
    palette[22] = (255, 117, 0)
    palette[23] = (255, 122, 0)
    palette[24] = (255, 128, 0)
    palette[25] = (255, 133, 0)
    palette[26] = (255, 138, 0)
    palette[27] = (255, 144, 0)
    palette[28] = (255, 149, 0)
    palette[29] = (255, 154, 0)
    palette[30] = (255, 160, 0)
    palette[31] = (255, 165, 0)

    # orange to yellow
    palette[32] = (255, 165, 0)
    palette[33] = (255, 168, 0)
    palette[34] = (255, 171, 0)
    palette[35] = (255, 174, 0)
    palette[36] = (255, 177, 0)
    palette[37] = (255, 180, 0)
    palette[38] = (255, 182, 0)
    palette[39] = (255, 185, 0)
    palette[40] = (255, 188, 0)
    palette[41] = (255, 191, 0)
    palette[42] = (255, 194, 0)
    palette[43] = (255, 197, 0)
    palette[44] = (255, 200, 0)
    palette[45] = (255, 203, 0)
    palette[46] = (255, 206, 0)
    palette[47] = (255, 209, 0)
    palette[48] = (255, 211, 0)
    palette[49] = (255, 214, 0)
    palette[50] = (255, 217, 0)
    palette[51] = (255, 220, 0)
    palette[52] = (255, 223, 0)
    palette[53] = (255, 226, 0)
    palette[54] = (255, 229, 0)
    palette[55] = (255, 232, 0)
    palette[56] = (255, 235, 0)
    palette[57] = (255, 238, 0)
    palette[58] = (255, 240, 0)
    palette[59] = (255, 243, 0)
    palette[60] = (255, 246, 0)
    palette[61] = (255, 249, 0)
    palette[62] = (255, 252, 0)
    palette[63] = (255, 255, 0)

    # yellow to green
    palette[64] = (255, 255, 0)
    palette[65] = (247, 255, 0)
    palette[66] = (239, 255, 0)
    palette[67] = (230, 255, 0)
    palette[68] = (222, 255, 0)
    palette[69] = (214, 255, 0)
    palette[70] = (206, 255, 0)
    palette[71] = (197, 255, 0)
    palette[72] = (189, 255, 0)
    palette[73] = (181, 255, 0)
    palette[74] = (173, 255, 0)
    palette[75] = (165, 255, 0)
    palette[76] = (156, 255, 0)
    palette[77] = (148, 255, 0)
    palette[78] = (140, 255, 0)
    palette[79] = (132, 255, 0)
    palette[80] = (123, 255, 0)
    palette[81] = (115, 255, 0)
    palette[82] = (107, 255, 0)
    palette[83] = (99, 255, 0)
    palette[84] = (90, 255, 0)
    palette[85] = (82, 255, 0)
    palette[86] = (74, 255, 0)
    palette[87] = (66, 255, 0)
    palette[88] = (58, 255, 0)
    palette[89] = (49, 255, 0)
    palette[90] = (41, 255, 0)
    palette[91] = (33, 255, 0)
    palette[92] = (25, 255, 0)
    palette[93] = (16, 255, 0)
    palette[94] = (8, 255, 0)
    palette[95] = (0, 255, 0)

    # green to blue
    palette[96] = (0, 255, 0)
    palette[97] = (0, 247, 8)
    palette[98] = (0, 239, 16)
    palette[99] = (0, 230, 25)
    palette[100] = (0, 222, 33)
    palette[101] = (0, 214, 41)
    palette[102] = (0, 206, 49)
    palette[103] = (0, 197, 58)
    palette[104] = (0, 189, 66)
    palette[105] = (0, 181, 74)
    palette[106] = (0, 173, 82)
    palette[107] = (0, 165, 90)
    palette[108] = (0, 156, 99)
    palette[109] = (0, 148, 107)
    palette[110] = (0, 140, 115)
    palette[111] = (0, 132, 123)
    palette[112] = (0, 123, 132)
    palette[113] = (0, 115, 140)
    palette[114] = (0, 107, 148)
    palette[115] = (0, 99, 156)
    palette[116] = (0, 90, 165)
    palette[117] = (0, 82, 173)
    palette[118] = (0, 74, 181)
    palette[119] = (0, 66, 189)
    palette[120] = (0, 58, 197)
    palette[121] = (0, 49, 206)
    palette[122] = (0, 41, 214)
    palette[123] = (0, 33, 222)
    palette[124] = (0, 25, 230)
    palette[125] = (0, 16, 239)
    palette[126] = (0, 8, 247)
    palette[127] = (0, 0, 255)

    # blue to purple
    palette[128] = (0, 0, 255)
    palette[129] = (5, 1, 255)
    palette[130] = (10, 2, 254)
    palette[131] = (15, 3, 254)
    palette[132] = (21, 4, 253)
    palette[133] = (26, 5, 253)
    palette[134] = (31, 6, 252)
    palette[135] = (36, 7, 252)
    palette[136] = (41, 8, 251)
    palette[137] = (46, 9, 251)
    palette[138] = (52, 10, 250)
    palette[139] = (57, 11, 250)
    palette[140] = (62, 12, 249)
    palette[141] = (67, 13, 249)
    palette[142] = (72, 14, 248)
    palette[143] = (77, 15, 248)
    palette[144] = (83, 17, 247)
    palette[145] = (88, 18, 247)
    palette[146] = (93, 19, 246)
    palette[147] = (98, 20, 246)
    palette[148] = (103, 21, 245)
    palette[149] = (108, 22, 245)
    palette[150] = (114, 23, 244)
    palette[151] = (119, 24, 244)
    palette[152] = (124, 25, 243)
    palette[153] = (129, 26, 243)
    palette[154] = (134, 27, 242)
    palette[155] = (139, 28, 242)
    palette[156] = (145, 29, 241)
    palette[157] = (150, 30, 241)
    palette[158] = (155, 31, 240)
    palette[159] = (160, 32, 240)

    # purple to red
    palette[160] = (160, 32, 240)
    palette[161] = (163, 31, 232)
    palette[162] = (166, 30, 225)
    palette[163] = (169, 29, 217)
    palette[164] = (172, 28, 209)
    palette[165] = (175, 27, 201)
    palette[166] = (178, 26, 194)
    palette[167] = (181, 25, 186)
    palette[168] = (185, 24, 178)
    palette[169] = (188, 23, 170)
    palette[170] = (191, 22, 163)
    palette[171] = (194, 21, 155)
    palette[172] = (197, 20, 147)
    palette[173] = (200, 19, 139)
    palette[174] = (203, 18, 132)
    palette[175] = (206, 17, 124)
    palette[176] = (209, 15, 116)
    palette[177] = (212, 14, 108)
    palette[178] = (215, 13, 101)
    palette[179] = (218, 12, 93)
    palette[180] = (221, 11, 85)
    palette[181] = (224, 10, 77)
    palette[182] = (227, 9, 70)
    palette[183] = (230, 8, 62)
    palette[184] = (234, 7, 54)
    palette[185] = (237, 6, 46)
    palette[186] = (240, 5, 39)
    palette[187] = (243, 4, 31)
    palette[188] = (246, 3, 23)
    palette[189] = (249, 2, 15)
    palette[190] = (252, 1, 8)
    palette[191] = (255, 0, 0)

    for i in range(len(palette)):
        r, g, b = palette[i]
        gc = fancy.gamma_adjust(fancy.CRGB(r, g, b), gamma_value=1.8)
        palette[i] = gc.pack()
    
    gamma_palette = displayio.Palette(192)
    for i in range(len(gamma_palette)):
        gamma_palette[i] = palette[i]

    return gamma_palette


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

    bitmap = [None] * panel.matrix.width
    tile_grid = [None] * panel.matrix.width
    palette = make_palette_rgb()
    for i in range(0, panel.matrix.width):
        bitmap[i] = displayio.Bitmap(1, panel.matrix.height, 192)
        for x in range(0, panel.matrix.height):
            bitmap[i][0,x] = i
        tile_grid[i] = displayio.TileGrid(bitmap[i], pixel_shader=palette)
        tile_grid[i].x = i
        master_group.append(tile_grid[i])

    i = 0
    while True:
        i += 1
        if i > 191:
            i = 0
        for x in range(0, panel.matrix.height):
            for y in range(0, panel.matrix.width):
                bitmap[y][x] = i


if __name__ == "__main__":
    main()
