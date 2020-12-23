#!/usr/bin/python3

""" DIYHA Alarm Controller:
    Manage a simple digital high or low GPIO pin.
"""

# The MIT License (MIT)
#
# Copyright (c) 2020 parttimehacker@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import threading
import time
import RPi.GPIO as GPIO

# constants for on/off topics and light interval before turning off

ON_STATE = "ON"
OFF_STATE = "OFF"

SWITCH_INTERVAL = 5 * 60 # 5 minute interval timer

LOCK = threading.Lock()

class SwitchController:
    """ Abstract and manage an switch GPIO pin. """

    def __init__(self, pin=17, interval=SWITCH_INTERVAL):
        """ Initialize the alarm GPIO pin.  """
        self.switch_pin = pin
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(self.switch_pin, GPIO.OUT,)
        GPIO.output(self.switch_pin, GPIO.LOW)
        self.state = OFF_STATE
        self.last_motion = 0.0
        self.interval = interval
        self.switch_topic = ""

    def set_mqtt_topic(self, client, topic):
        """ set the switch status topic and prepare for publish """
        self.client = client
        self.switch_topic = topic

    def start(self,):
        """ Start the switch interval timer thread """
        self.active = True
        led_thread = threading.Thread(target=self.manage_switch, args=())
        led_thread.daemon = True
        led_thread.start()

    def manage_switch(self):
        """ sleep and then test for expired timer """
        while self.active:
            LOCK.acquire()
            if self.state == ON_STATE:
                elapsed_time = time.time() - self.last_motion
                if elapsed_time > self.interval:
                    GPIO.output(self.switch_pin, GPIO.LOW)
                    self.state = OFF_STATE
                    if len(self.switch_topic) > 0:
                        self.client.publish(self.switch_topic, self.state, 0, True)
            LOCK.release()
            time.sleep(5)

    def turn_on_switch(self,):
        """ step to turn on the switch and message status """
        LOCK.acquire()
        if self.state == OFF_STATE:
            GPIO.output(self.switch_pin, GPIO.HIGH)
            self.state = ON_STATE
            if len(self.switch_topic) > 0:
                self.client.publish(self.switch_topic, self.state, 0, True)
        self.last_motion = time.time()
        LOCK.release()

    def turn_off_switch(self,):
        """ step to turn off the switch and message status """
        LOCK.acquire()
        if self.state == ON_STATE:
            self.state = OFF_STATE
            GPIO.output(self.switch_pin, GPIO.LOW)
            if len(self.switch_topic) > 0:
                self.client.publish(self.switch_topic, self.state, 0, True)
        LOCK.release()
