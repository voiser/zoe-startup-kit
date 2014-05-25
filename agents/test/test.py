#!/usr/bin/env PYTHONUNBUFFERED=1 python3

import zoe
from zoe.deco import *

@Agent(name = "test", topic = "messing_around")
class RelayAgent:

    @Message(tags = ["test"])
    def receive(self, parser):
        print("Hi, I'm a test agent and I have received the following message:", parser)
