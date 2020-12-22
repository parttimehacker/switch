#!/usr/bin/python3

""" DIYHA Motion Controller:
    Manage a simple PIR motion sensor returning a 1 or 0 from a queue of interrupts.
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

import queue
import RPi.GPIO as GPIO

class MotionController:
    """ Abstract and manage a PIR motion snesor. """

    def __init__(self, pin=27):
        """ Initialize the PIR GPIO pin. """
        self.pir_pin = pin
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setup(self.pir_pin, GPIO.IN)
        self.queue = queue.Queue()
        self.enable()

    def pir_interrupt_handler(self, ):
        """ Motion interrupt handler adds 1 or 0 to queue. """
        state = self.GPIO.input(self.pir_pin)
        if state == 1:
            message = "1"
        else:
            message = "0"
        if state != self.last_reading:
            self.queue.put(message)
        self.last_reading = state

    def enable(self, ):
        """ Enable interrupts and prepare the callback. """
        self.GPIO.add_event_detect(self.pir_pin, GPIO.BOTH, callback=self.pir_interrupt_handler)

    def detected(self, ):
        """ Has motion been detected? True or false based on queue contents. """
        return not self.queue.empty()

    def get_motion(self, ):
        """ Return the last value either 1 or 0. """
        return self.queue.get(False)

    def wait_for_motion(self, ):
        """ Blocking wait for the next interrupt 1 or 0. """
        return self.queue.get(True)