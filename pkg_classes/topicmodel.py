#!/usr/bin/python3
""" DIYHA MQTT location initializer """

# The MIT License (MIT)
#
# Copyright (c) 2019 parttimehacker@gmail.com
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

import socket

class TopicModel:
    """ Location_topic initializer waits for MQTT broker logic to pass location and
        avoids global PEP8 issue.
    """

    def __init__(self):
        """ Create two topics for this application. """
        host_name = socket.gethostname()
        self.status_topic = 'diy/'+host_name+'/status'
        self.switch_status_topic = ''
        self.switch_topic = ''
        self.location_topic = ''
        self.motion_topic = ''

    def set(self, location):
        """ The location topic is typically returned by MQTT message methods at startup. """
        self.location_topic = location
        self.switch_topic = location + '/switch'
        self.switch_status_topic = self.switch_topic + '/status'
        self.motion_topic = location + '/motion'

    def get_status(self,):
        """ Typically used in response to MQTT diy/system/who message. """
        return self.status_topic

    def get_switch(self,):
        """ Typically used in response to MQTT diy/system/who message. """
        return self.switch_topic

    def get_switch_status(self,):
        """ Typically used in response to MQTT diy/system/who message. """
        return self.switch_status_topic

    def get_motion(self,):
        """ Typically used in response to MQTT diy/system/who message. """
        return self.motion_topic

    def get_location(self,):
        """ The location topic is used to manage multiple devices. """
        return self.location_topic