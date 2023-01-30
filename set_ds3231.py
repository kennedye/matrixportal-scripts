# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# pylint: disable=import-error,unused-import

import time
import board
import busio
from digitalio import DigitalInOut
import neopixel
import rtc
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_ds3231

try:
    from _secrets import af_secrets as secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

def main():  # pylint: disable=too-many-locals
    """
    they call it main.
    """

    print("ESP32 local time")

    TIME_API = "http://worldtimeapi.org/api/ip"

    esp32_cs = DigitalInOut(board.ESP_CS)
    esp32_ready = DigitalInOut(board.ESP_BUSY)
    esp32_reset = DigitalInOut(board.ESP_RESET)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    status_light = neopixel.NeoPixel(
        board.NEOPIXEL, 1, brightness=0.2
    )  # Uncomment for Most Boards
    wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

    i2c = board.I2C()
    ds3231 = adafruit_ds3231.DS3231(i2c)
    # the_rtc = rtc.RTC()

    response = None
    while True:
        try:
            print("Fetching json from", TIME_API)
            response = wifi.get(TIME_API)
            break
        except OSError as e:  #pylint: disable=invalid-name
            print("Failed to get data, retrying\n", e)
            continue

    json = response.json()
    current_time = json["datetime"]
    the_date, the_time = current_time.split("T")
    year, month, mday = [int(x) for x in the_date.split("-")]
    the_time = the_time.split(".")[0]
    hours, minutes, seconds = [int(x) for x in the_time.split(":")]

    # We can also fill in these extra nice things
    year_day = json["day_of_year"]
    week_day = json["day_of_week"]
    is_dst = json["dst"]

    now = time.struct_time(
        (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst)
    )
    print(now)
    ds3231.datetime = now
    #the_rtc.datetime = now

    print(time.localtime())

if __name__ == "__main__":
    main()
