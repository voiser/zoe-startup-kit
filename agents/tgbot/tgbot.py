#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# zoe-tgbot - https://github.com/rmed/zoe-tgbot
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
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

import sys
sys.path.append('./lib')

import base64
import threading
import telebot
import time
import zoe
from os import environ as env
from os.path import join as path
from telebot import util
from zoe.deco import Agent, Message

with open(path(env['ZOE_HOME'], 'etc', 'tgbot.conf'), 'r') as f:
    TG_TOKEN = f.readline().strip()


@Agent(name='tg')
class Tgbot:

    def __init__(self):
        self._starttime = time.time()

        # Non-threaded (better fro skipping exceptions)
        self.bot = telebot.TeleBot(TG_TOKEN, threaded=False)
        self.bot.set_update_listener(self._tg_msg)
        self._bot_me = self.bot.get_me()

        self._tg_listener = threading.Thread(target=self._tg_bot)
        self._tg_listener.setDaemon(True)
        self._tg_listener.start()

    def _tg_bot(self):
        """ Start the telegram bot that continuously polls for new messages
            and parses them accordingly.
        """
        while True:
            try:
                # Continue polling even after an exception occurs
                self.bot.polling(none_stop=True)
                time.sleep(100)
            except Exception as e:
                print('[EXCEPTION]:', e)
                time.sleep(100)
                pass

    def _tg_msg(self, messages):
        """ Handler for telegram messages. """
        for msg in messages:
            if msg.date < self._starttime:
                # Skip old messages
                continue

            if msg.content_type != 'text':
                # Only work with texts
                continue

            from_user = msg.from_user.id
            from_username = msg.from_user.username
            from_chat = msg.chat.id

            from_full = []
            if from_chat < 0:
                # If chat ID is negative, then it is a group chat
                from_full.append('group#%s' % from_chat)

            from_full.append('user#%s' % from_user)

            if from_username:
                # Check also the unique username
                from_full.append(from_username)

            used_id, user = self.finduser(from_full)
            if not user:
                # Not recognized
                print(
                    'Received message from unknown IDs: ', from_full)
                print(
                    'Chat/User name was: ',
                        msg.chat.title if from_chat < 0 else
                        msg.from_user.first_name)
                continue

            if '#' not in used_id:
                # This is not a unique ID, notify the user so that they can
                # add it to their user configuration
                # API only allows IDs when sending messages
                self.bot.send_message(from_user,
                    'Please add "user#%s" to your zoe-users.conf' % from_user)

            # Remove @BOT_USERNAME from text
            text = msg.text.replace('@%s' % self._bot_me.username, '').strip()
            text64 = base64.standard_b64encode(
                text.encode('utf-8')).decode('utf-8')

            # We need the chat ID for the answer
            natural_msg = {
                'dst'     : 'relay',
                'relayto' : 'natural',
                'src'     : 'tg',
                'tag'     : ['command', 'relay'],
                'sender'  : user['id'],
                'tguser'  : 'user#%s' % from_user,
                'tgchat'  : str(from_chat),
                'cmd'     : text64
            }

            self.sendbus(zoe.MessageBuilder(natural_msg).msg())

    @Message(tags=['command-feedback'])
    def feedback(self, parser):
        """ Send the feedback of a command through Telegram. """
        tgchat = int(parser.get('tgchat'))
        text = parser.get('feedback-string')

        # API supports a maximum of 5000 characters per message
        # This will divide the messages in chunks of 3000 characters
        text_chunks = util.split_string(text, 3000)
        for chunk in text_chunks:
            # self.bot.send_message(tgchat, chunk, parse_mode='Markdown')
            self.bot.send_message(tgchat, chunk)

    @Message(tags=[])
    def sendtg(self, parser):
        """ Send a message to an user through Telegram.

            In order to do this, the agent will `guess` who the recipient
            is based on the `to` tag in the parser.
        """
        to = self.guess(parser.get('to'))
        if not to:
            # Did not find unique ID
            print('Cannot find Telegram ID for %s' % parser.get('to'))
            return

        msg = parser.get('msg')

        # API supports a maximum of 5000 characters per message
        # This will divide the messages in chunks of 3000 characters
        text_chunks = util.split_string(msg, 3000)
        for chunk in text_chunks:
            # self.bot.send_message(to, chunk, parse_mode='Markdown')
            self.bot.send_message(to, chunk)

    def finduser(self, user_ids):
        """ Find a given user or group.

            First checks the group ID to see if anyone in the given group can
            communicate with Zoe. If no occurence is found, the user ID
            is checked, and then the username (if present).
        """
        subjects = zoe.Users().subjects()

        # Store a relation so users are not accessed all the time
        id_rels = {}
        for subj in subjects:
            if 'tg' not in subjects[subj]:
                continue

            for s in subjects[subj]['tg'].split(','):
                id_rels[s.strip()] = subjects[subj]['uniqueid']

        for usr in user_ids:
            if usr in id_rels.keys():
                return usr, subjects[id_rels[usr]]

        return None, None

    def guess(self, dest):
        """ Guess the recipient of the message

            First, it will check if it is a Telegram ID (string with #), then
            if it is a Zoe user and finally Telegram nicknames for each user.
        """
        if '#' in dest:
            # Already a unique ID
            return int(dest.rsplit('#')[1])

        subjects = zoe.Users().subjects()
        if dest in subjects and 'tg' in subjects[dest]:
            subject_ids = [s.strip() for s in subjects[dest]['tg'].split(',')]

            # Find unique ID
            for sid in subject_ids:
                if '#' in sid:
                    return int(sid.rsplit('#')[1])

        # Try to find the username
        for subj in subjects:
            subject_ids = [s.strip() for s in subjects[subj]['tg'].split(',')]

            if dest in subject_ids:
                for sid in subject_ids:
                    if '#' in sid:
                        return int(sid.rsplit('#')[1])
