# pylint: disable=line-too-long,import-error,unused-import,too-many-locals,invalid-name,unused-variable,too-many-statements,invalid-envvar-default,consider-using-f-string
"""
mp_simpleclock.py
just the text ma'am
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
import terminalio
from rainbowio import colorwheel
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests
import adafruit_lis3dh  # accelerometer
import adafruit_ds3231  # RTC
from led_panel import LedPanel
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_fancyled.adafruit_fancyled as fancy

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
    lis3dh.set_tap(2, 60)

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

    font = bitmap_font.load_font("/fonts/4x6.pcf")
    font2 = bitmap_font.load_font("/fonts/5x7.pcf")

    ip_label = label.Label(font2)
    ip_label.x = 0
    ip_label.y = 4
    ip_label.color = (255, 0, 0)
    ip_label_anchored_position = (0, 0)
    ip_label.text = "IP"
    master_group.append(ip_label)
    url_getip="https://api.ipgeolocation.io/getip"
    getip=wifi.get(url_getip).json()
    ip=getip["ip"]
    print(ip)

    loc_label = label.Label(font2)
    loc_label.x = 0
    loc_label.y = 11
    loc_label.color = (0, 255, 0)
    loc_label_anchored_position = (0, 0)
    loc_label.text = "loc"
    master_group.append(loc_label)
    url_getloc="https://api.ipgeolocation.io/ipgeo?apiKey=" + secrets["gl_apikey"] + "&ip=" + ip
    getloc=wifi.get(url_getloc).json()
    print(getloc)

    w_label = label.Label(font2)
    w_label.x = 0
    w_label.y = 18
    w_label.color = (0, 0, 255)
    w_label_anchored_position = (0, 0)
    w_label.text = "weather"
    master_group.append(w_label)
    url_w = "https://api.openweathermap.org/data/2.5/weather?lat=" + getloc["latitude"] + "&lon=" + getloc["longitude"] + "&appid=" + secrets["ow_apikey"] + "&units=imperial"
    w=wifi.get(url_w).json()
    print(w)

    master_group.pop()
    master_group.pop()
    master_group.pop()

    text_label = label.Label(font)
    text_label.x = 0
    text_label.y = 3
    text_label.color=(255,0,255)
    text_label.anchored_position = (0, 0)
    text_label.text="{hours:02d}{minutes:02d}{seconds:02d}".format(hours=current_time[3], minutes=current_time[4], seconds=current_time[5])
    master_group.append(text_label)
    label2 = label.Label(font)
    label2.x = 0
    label2.y = 9
    gc = fancy.CRGB(255, 0, 0)
    gc = fancy.gamma_adjust(gc, gamma_value=1.8)
    label2.color=gc.pack()
    label2.text = "abcdefgh"
    master_group.append(label2)
    label3 = label.Label(font)
    label3.x = 0
    label3.y = 15
    gc = fancy.CRGB(255, 255, 0)
    gc = fancy.gamma_adjust(gc, gamma_value=1.8)
    label3.color=gc.pack()
    label3.text = "ijklmnop"
    master_group.append(label3)
    label4 = label.Label(font)
    label4.x = 0
    label4.y = 21
    label4.color = (255, 255, 0)
    label4.text = "qrstuvwx"
    master_group.append(label4)
    label5 = label.Label(font)
    label5.x = 0
    label5.y = 27
    label5.color = (255, 255, 0)
    label5.text = "yz123456"
    master_group.append(label5)
    print(text_label.bounding_box)
    while True:
        current_time = ds3231.datetime
        text_label.text="{hours:02d}{minutes:02d}{seconds:02d}".format(hours=current_time[3], minutes=current_time[4], seconds=current_time[5])
        r,g,b = (random.randint(32,255),random.randint(32,255),random.randint(32,255))
        gc = fancy.CRGB(r, g, b)
        gc = fancy.gamma_adjust(gc, gamma_value=1.8)
        text_label.color=gc.pack()
        r,g,b = (random.randint(1,255),random.randint(1,255),random.randint(1,255))
        gc = fancy.CRGB(r, g, b)
        gc = fancy.gamma_adjust(gc, gamma_value=1.8)
        label2.color=gc.pack()
        r,g,b = (random.randint(32,255),random.randint(32,255),random.randint(32,255))
        label3.color=(r, g, b)
        r,g,b = (random.randint(128,255),random.randint(128,255),random.randint(128,255))
        label4.color=(r, g, b)
        r,g,b = (random.randint(32,128),random.randint(32,128),random.randint(32,128))
        label5.color=(r, g, b)
        if lis3dh.tapped:
            print("Tapped!")

        time.sleep(1)

if __name__ == "__main__":
    main()
