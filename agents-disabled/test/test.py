#!/usr/bin/env python3

import zoe
from zoe.deco import *

@Agent(name = "test", topic = "messing_around")
class RelayAgent:

    # 
    # Take a look at the "test" agent log:
    #   tail -f logs/test.log
    # and in other terminal try the commands shown in each method:
    #
    
    #
    # echo -n "dst=test&tag=test&key_a=value_a1&key_a=value_a2&key_b=value_b" | nc localhost 30000 
    #
    @Message(tags = ["test"])
    def receive(self, parser):
        print("Hi, I'm a test agent and I have received the following message:", parser)

    #
    # echo -n "dst=test&tag=hello&name=John Doe" | nc localhost 30000 
    #
    @Message(tags = ["hello"])
    def receive_hello(self, name):
        print("Hi,", name, ", how are you?")
    
    #
    # echo -n "dst=test&tag=indirect&name=John Doe" | nc localhost 30000 
    #
    @Message(tags=["indirect"])
    def receive_and_answer(self, name):
        print("I will send back a message to Zoe (that will also be sent to this agent)")
        return zoe.MessageBuilder({'dst': 'test', 'tag': 'hello', 'name': name})
