# SPDX-FileCopyrightText: 2019 Dave Astels for Adafruit Industries
# SPDX-License-Identifier: MIT

# pylint: disable=invalid-name

import time
import os
import sys
import board
import busio
from digitalio import DigitalInOut,Direction,Pull
from adafruit_debouncer import Debouncer
import neopixel
import rtc
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_ds3231


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

def create_wifi(wifi_secrets: dict) -> adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager:
    """
    set up a WifiManager structure
    """
    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
    return adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, wifi_secrets, status_light)


def set_time(wifi: adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager) -> None:
    TIME_API = "https://worldtimeapi.org/api/ip"
    i2c = board.I2C()
    ds3231 = adafruit_ds3231.DS3231(i2c)
    while True:
        try:
            print("Fetching json from", TIME_API)
            response = wifi.get(TIME_API)
            break
        except OSError as e:
            print("Failed to get data, retrying\n", e)
            continue

    json = response.json()
    current_time = json["datetime"]
    the_date, the_time = current_time.split("T")
    year, month, mday = [int(x) for x in the_date.split("-")]
    the_time = the_time.split(".")[0]
    hours, minutes, seconds = [int(x) for x in the_time.split(":")]

    year_day = json["day_of_year"]
    week_day = json["day_of_week"]
    is_dst = json["dst"]

    now = time.struct_time(
        (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
    )
    print(now)
    ds3231.datetime = now
    print(time.localtime())


def main() -> None:
    """
    ...main.
    """

    # is it safe
    compatibility_check()

    # get wifi secrets
    secrets = get_secrets()
    
    wifi = create_wifi(secrets)

    button_up = DigitalInOut(board.BUTTON_UP)
    button_down = DigitalInOut(board.BUTTON_DOWN)
    button_up.direction = button_down.direction = Direction.INPUT
    button_up.pull = button_down.pull = Pull.UP
    switch_up = Debouncer(button_up)
    # button_down.direction = digitalio.Direction.INPUT
    # button_down.pull = digitalio.Pull.UP
    switch_down = Debouncer(button_down)
#     status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

    while True:
        switch_up.update()
        switch_down.update()
        if switch_up.fell:
            print("Just pressed up")
        if switch_up.rose:
            print("Just released up")
        if switch_down.fell:
            print("Just pressed down")
            set_time(wifi)
        if switch_down.rose:
            print("Just released down")
        if switch_up.value:
#             print("up not pressed")
            pass
        else:
            print("up pressed")

if __name__ == "__main__":
    main()

