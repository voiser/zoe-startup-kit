#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Zoe Assistant - https://github.com/guluc3m/gul-zoe
#
# Copyright (c) 2015 David Muñoz Díaz <david@gul.es> 
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

import zoe
import base64
import threading
import time
import subprocess
import os
import os.path
import json
import time
import tempfile
import configparser
import signal
import sys

from zoe.deco import *

@Agent("tg")
class TelegramAgent:

    def __init__(self, conffile = os.environ['ZOE_HOME'] + "/etc/tg.conf"):
        config = configparser.ConfigParser()
        config.read(conffile, encoding = "utf8")
        self._starttime = time.time()
        pwd = os.getcwd()
        tgroot = config["tg"]["installation_folder"]
        if tgroot == "...":
            raise Exception("You haven't configured this agent, have you?")
        print("Looking for telegram-cli in %s..." % (tgroot))
        tgbinary = "%s/bin/telegram-cli" % (tgroot)
        tgkey = "%s/tg-server.pub" % (tgroot)
        if not os.path.isfile(tgbinary):
            raise Exception("Can't find telegram-cli binary in path %s (tried %s)" % (tgroot, tgbinary))
        if not os.path.isfile(tgkey):
            raise Exception("Can't find tg-server.pub server key in path %s (tried %s)" % (tgroot, tgkey))
        print("Launching tg-cli...")
        cmd = "%s -k %s -s %s/lua/stdout.lua -C -R -l 0" % (tgbinary, tgkey, pwd)
        self._tgcli = subprocess.Popen(cmd.split(" "), stdout = subprocess.PIPE, universal_newlines = True, bufsize = 1, stdin = subprocess.PIPE)
        print("Subprocess started with PID %d" % (self._tgcli.pid))
        signal.signal(signal.SIGTERM, self.killtg)
        self._tgthread = threading.Thread (target = self.tgread)
        self._tgthread.start()

    def killtg(self, signal, frame):
        print("Killing child process")
        self._tgcli.kill()
        print("Done")
        os._exit(0)

    def tgread(self):
        while True:
            line = self._tgcli.stdout.readline()
            if line:
                #print("tg line", line)
                if line[0] != "{":
                    continue
                j = json.loads(line)
                #print("Received: ", j)
                self.messagefromtg(j)

    def messagefromtg(self, json):
        msgtime  = json["date"]
        if msgtime < self._starttime:
            #print("Skipping (old message)")
            return
        if not 'text' in json:
            #print("Skipping (no text)")
            return
        fromuser = json["from"]["id"]
        fromtype = json["from"]["type"]
        fromfull = "%s#%s" % (fromtype, fromuser)
        totype   = json["to"]["type"]
        text     = json["text"]
        #print("Message from: ", fromfull)
        user = self.finduser(fromfull)
        if not user:
            #print("Ignored")
            return
        if totype == "chat":
            #print ("In-chat not yet implemented")
            return
        if text[0:3].lower() != "zoe":
            return
        text = text[3:]
        text64 = base64.standard_b64encode(text.encode('utf-8')).decode('utf-8')
        aMap = {"dst":"relay",
                "relayto":"natural", 
                "src":"tg", 
                "tag":["command", "relay"],
                "sender":user["id"],
                "tguser":"%s#%d" % (fromtype, fromuser),
                "cmd":text64}
        self.sendbus(zoe.MessageBuilder(aMap).msg())
    
    def finduser(self, user):
        model = zoe.Users()
        subjects = model.subjects()
        for s in subjects:
            if "tg" in subjects[s] and str(user) in subjects[s]["tg"].split(","):
                uid = subjects[s]["uniqueid"]
                return subjects[uid]
 
    def guess(self, dest):
        if "#" in dest:
            return dest
        subjects = zoe.Users().subjects()
        if dest in subjects:
            address = subjects[dest]["tg"]
            return address
    
    def telegram(self, tguser, txt):
        #print ("I have to send text '", txt, "', to", tguser)
        f = tempfile.NamedTemporaryFile(delete = False)
        f.write(txt.encode('utf-8'))
        f.close()
        self._tgcli.stdin.write("send_text %s %s\n" % (tguser, f.name))
        os.unlink(f.name)
        
    @Message(tags = [])
    def sendtg(self, parser):
        to = self.guess(parser.get("to"))
        msg = parser.get("msg")
        self.logger.debug("Sending " + msg + " to " + to)
        self.telegram(to, msg)

    @Message(tags = ["command-feedback"])
    def feedback(self, parser):
        tguser = parser.get("tguser")
        txt = parser.get("feedback-string")
        self.telegram(tguser, txt)

