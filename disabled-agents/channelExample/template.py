#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 David Muñoz Díaz <david@gul.es>
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#
# This is a template for adding a communication channel to Zoe, 
# like IRC or Jabber.
#

import base64
import threading
import zoe
from zoe.deco import Agent, Message

#
# The agent name
#
NAME = "(agent name here)"

#
# The configuration key in zoe-users.conf that refer to this channel
# For instance, if this is a Jabber channel, you probably will have something like:
#
# [subject admin]
# ...
# jabber_id = ...
# ...
#
# In this case, CHANNEL_KEY would be 'jabber_id'
#
CHANNEL_KEY = "(your key here)"

@Agent(name = NAME)
class MyChannelAgent:

    #
    # initialize your channel here
    # when a message is received from the channel, self.incoming_message should
    # be invoked.
    # Note that some extra parameters will probably be needed, like the message itself, 
    # the sender, etc.
    #
    def __init__(self):
        self._users = zoe.Users().subjects()
        # Remember that the constructor must not be blocking,
        # that is, the channel event loop must run in its own thread.
        pass

    #
    # This function is invoked when there's an incoming message
    #
    def incoming_message(self, ...):

        # The incoming message, as a str
        text = ...

        # The person who sent the message
        emitter = ...

        # Normally we will not attend anyone's message, only messages from our users.
        # We have to find a user who matches the emitter value. 
        # It will probably look for all users in zoe-users.conf and find one with 
        # the identity of the emitter.
        user = self.finduser(emitter)
        if not user:
            # Not recognized
            print('Received message from unknown user: ', emitter)
            return

        # The natural agent, which attends commands, expects the command in base64
        text64 = base64.standard_b64encode(text.encode('utf-8')).decode('utf-8')

        # This is the resulting message.
        natural_msg = {
            'dst'     : 'relay',
            'relayto' : 'natural',
            'src'     : NAME,
            'tag'     : ['command', 'relay'],
            'sender'  : user['id'],
            'cmd'     : text64,
            # you can add more data you need, like the channel context (say, chat room)
            'room'    : ...
        }    
        self.sendbus(zoe.MessageBuilder(natural_msg).msg())

    #
    # Invoked when Zoe answers a command
    #
    @Message(tags=['command-feedback'])
    def feedback(self, parser):
        text = parser.get('feedback-string')
        room = parser.get('room')
        # send the text to the channel

    #
    # Invoked when a new message has to be sent to a user
    #
    @Message(tags=[])
    def sendtg(self, to, text, parser):
        # Guess the recipient
        rcpt = self.guess(to)
        if not rcpt:
            print('Cannot find ID for %s' % to)
            return
        # Send the text to the user

    #
    # Finds a Zoe user identified by a channel ID
    # For instance, if you have a channel where each user is identified by a unique
    # number, and zoe-users.conf looks like:
    # 
    # [subject admin]
    # channelid = 1,2,3
    # 
    # Then, when the channel tells us that a message from user '2' is received, 
    # we have to find that it corresponds to the Zoe user 'admin'.
    # This function also deals with aliases, meaning that it will return the principal
    # user, not any of its alias.
    #
    def finduser(self, channel_id):
        for s in self._users:
            if CHANNEL_KEY in self._users[s] and channel_id in self._users[s][CHANNEL_KEY].split(","):
                uid = self._users[s]["uniqueid"]
                return self._users[uid]
    
    #
    # Given a recipient, guesses its channel id 
    #
    def guess(self, dest):
        if dest in self._users:
            address = self._users[dest][CHANNEL_KEY]
            if "," in address:
                address = address.split(",")[0]
            return address
