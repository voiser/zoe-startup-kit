#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Zoe Assistant - https://github.com/guluc3m/gul-zoe
#
# Copyright (c) 2013 David Muñoz Díaz <david@gul.es> 
#
# This file is distributed under the MIT LICENSE
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

import os
import zoe
import configparser
from zoe.deco import *
from twitter import *

@Agent(name = "twitter")
class TwitterAgent:
    
    def __init__(self, conffile = os.environ['ZOE_HOME'] + "/etc/twitter.conf"):
        config = configparser.ConfigParser()
        config.read(conffile, encoding = "utf8")
        api_key = config["twitter"]["api_key"]
        api_key_secret = config["twitter"]["api_key_secret"]
        access_token = config["twitter"]["access_token"]
        access_token_secret = config["twitter"]["access_token_secret"]
        self._twitter = Twitter(auth=OAuth(access_token, access_token_secret, api_key, api_key_secret))

    @Message(tags=[])
    def send(self, to, msg):
        if to:
            if to[0] == "@":
                msg = to + " " + msg
            else:
                try:
                    guessed = zoe.Users().subject(to)["twitter"]
                    msg = guessed + " " + msg
                except Exception as e:
                    msg = "@" + to + " " + msg
        self._twitter.statuses.update(status=msg)
