#!/usr/bin/python3
""" DIYHA Switch Controller
    Receives MQTT messages from MQTT broker or motion sensor to turn on/off switch.
"""

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

import logging.config
import time
import paho.mqtt.client as mqtt

from pkg_classes.motioncontroller import MotionController
from pkg_classes.switchcontroller import SwitchController
from pkg_classes.testmodel import TestModel
from pkg_classes.topicmodel import TopicModel
from pkg_classes.whocontroller import WhoController
from pkg_classes.configmodel import ConfigModel
from pkg_classes.statusmodel import StatusModel
from pkg_classes.alarmcontroller import AlarmController

# Constants for GPIO pins

SWITCH_GPIO = 17
MOTION_GPIO = 27
ALARM_GPIO = 4

# Start logging and enable imported classes to log appropriately.

logging.config.fileConfig(fname="/usr/local/switch/logging.ini",
                          disable_existing_loggers=False)
LOGGER = logging.getLogger("switch")
LOGGER.info('Application started')

# get the command line arguements

CONFIG = ConfigModel()

# Location is used to create the switch topics

TOPIC = TopicModel()  # Location MQTT topic
TOPIC.set(CONFIG.get_location())

# Set up who message handler from MQTT broker and wait for client.

WHO = WhoController()

# set up switch GPIO controller to power on/off and with interval timer

SWITCH = SwitchController(SWITCH_GPIO)  # Alarm or light controller

# set up the motion controller using a PIR sensor

MOTION = MotionController(MOTION_GPIO)

# set up the alarm controller 

ALARM = AlarmController(ALARM_GPIO)
ALARM.start()

# process diy/system/test development messages

TEST = TestModel(SWITCH)

# Process MQTT messages using a dispatch table algorithm.

def system_message(client, msg):
    """ Log and process system messages. """
    # pylint: disable=unused-argument
    LOGGER.info(msg.topic + " " + msg.payload.decode('utf-8'))
    if msg.topic == 'diy/system/fire':
        if msg.payload == b'ON':
            SWITCH.turn_on_switch()
            ALARM.sound_alarm(True)
        else:
            SWITCH.turn_off_switch()
            ALARM.sound_alarm(False)
    elif msg.topic == 'diy/system/panic':
        if msg.payload == b'ON':
            SWITCH.turn_on_switch()
            ALARM.sound_pulsing_alarm(True)
        else:
            SWITCH.turn_off_switch()
            ALARM.sound_pulsing_alarm(False)
    elif msg.topic == 'diy/system/test':
        TEST.on_message(msg.payload)
    elif msg.topic == 'diy/system/who':
        if msg.payload == b'ON':
            WHO.turn_on()
        else:
            WHO.turn_off()


#  A dictionary dispatch table is used to parse and execute MQTT messages.

TOPIC_DISPATCH_DICTIONARY = {
    "diy/system/fire":
        {"method": system_message},
    "diy/system/panic":
        {"method": system_message},
    "diy/system/test":
        {"method": system_message},
    "diy/system/who":
        {"method": system_message}
}


def on_message(client, userdata, msg):
    """ dispatch to the appropriate MQTT topic handler """
    # pylint: disable=unused-argument
    if msg.topic == TOPIC.get_switch():
        if msg.payload == b'ON':
            SWITCH.turn_on_switch()
        else:
            SWITCH.turn_off_switch()
    else:
        TOPIC_DISPATCH_DICTIONARY[msg.topic]["method"](client, msg)


def on_connect(client, userdata, flags, rc_msg):
    """ Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed.
    """
    # pylint: disable=unused-argument
    client.subscribe("diy/system/fire", 1)
    client.subscribe("diy/system/panic", 1)
    client.subscribe("diy/system/test", 1)
    client.subscribe("diy/system/who", 1)


def on_disconnect(client, userdata, rc_msg):
    """ Subscribing on_disconnect() tilt """
    # pylint: disable=unused-argument
    client.connected_flag = False
    client.disconnect_flag = True


if __name__ == '__main__':

    # Setup MQTT handlers then wait for timed events or messages

    CLIENT = mqtt.Client()
    CLIENT.on_connect = on_connect
    CLIENT.on_disconnect = on_disconnect
    CLIENT.on_message = on_message

    # initilze the Who client for publishing.

    WHO.set_client(CLIENT)

    # command line argument contains Mosquitto MQTT broker IP address.

    SWITCH.set_mqtt_topic(CLIENT, TOPIC.get_switch())

    # command line argument for the switch mode - motion activated is the default

    CLIENT.connect(CONFIG.get_broker(), 1883, 60)
    CLIENT.loop_start()

    time.sleep(2) # let MQTT stuff initialize

    # initialize status monitoring

    STATUS = StatusModel(CLIENT)
    STATUS.start()

    # start the switch automatic management

    SWITCH.start()

    # Loop forever waiting for motion

    while True:
        time.sleep(2.0)
        if MOTION.detected():
            movement = MOTION.get_motion()
            CLIENT.publish(TOPIC.get_motion(), movement, 0, True)
            if movement == "1":
                if CONFIG.mode() == "motion":
                    SWITCH.turn_on_switch()
                else:
                    if SWITCH.state == "ON":
                        SWITCH.turn_on_switch()
