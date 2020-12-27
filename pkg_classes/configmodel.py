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

import argparse
import logging
import logging.config

class ConfigModel:
    """ Who controller handles  MQTT broker messsages for diy/system/who ON or OFF.
    """

    def __init__(self,):
        """ Create two topics for this application. """
        logging.config.fileConfig(fname='/usr/local/diyha_switch/logging.ini',
                                  disable_existing_loggers=False)
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        PARSER = argparse.ArgumentParser('sensor.py parser')
        PARSER.add_argument('--mqtt', help='MQTT server IP address')
        PARSER.add_argument('--location', help='Location topic required')
        PARSER.add_argument('--mode', help='Mode: motion or message required')
        ARGS = PARSER.parse_args()
        # command line arguement for the MQTT broker hostname or IP
        if ARGS.mqtt == None:
            self.logger.error("Terminating> --mqtt not provided")
            exit()
        self.broker_ip = ARGS.mqtt
        # command line arguement for the location topic
        if ARGS.location == None:
            self.logger.error("Terminating> --location not provided")
            exit()
        self.location = ARGS.location
        # command line argument for the mode - manual or motion - motion is the default
        if ARGS.mode == None:
            self.mode = "motion"
        else:
            self.mode = ARGS.mode
        self.logger.info( "Mode> ", str( self.mode ) )

    def get_broker(self, ):
        """ The location topic is typically returned by MQTT message methods at startup."""
        return self.broker_ip

    def get_location(self, ):
        """ Typically used by MQTT subscribe methods. """
        return self.location

    def get_mode(self,):
        """  Response to MQTT diy/system/who message. """
        return self.mode