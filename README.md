# zoe-startup-kit

This is a clean distribution of Zoe, the GUL UC3M assistant. It contains the 
basic agents on which you can build your own assistant.

See the [gul-zoe repository at Github](https://github.com/guluc3m/gul-zoe) for more information.


# What do I need

- OS X or Linux (BSD should be fine too, but I haven't tested it)
- Bash
- Java 1.7
- Python 3
- Perl 5


# Agents included

- Core components (server, natural, broadcast, log, relay, users)
- Jabber (read and write)
- Mail (read and write)
- Twitter (write only)
- An example agent (agests/test)



# How do I start

- Check the configuration files at etc/ folder.
- Load the Zoe configuration:

  $ . etc/environment.sh

- Launch Zoe:

  $ ./zoe.sh start

- Check the Zoe status:

  $ ./zoe.sh status

If there are dead agents, check their log files (at the log/ directory) to figure out the error. It is probably a misconfiguration. 



# How do I add my own features

There are two basic parts in Zoe: agents and commands. 

## Agents

An agent is a process responsible of a single feature. To communicate, agents use messages, that are simple key-value pairs. 
[This document](https://github.com/guluc3m/gul-zoe/blob/master/doc/messages.html) describes the message format and the set of messages
already defined. Please note that this document contains messages for agents that are not available in this repository, like the banking
agent or the activities one.

In order to write an agent, take a look at agents/test and [this article](http://voiser.org/post/69721172250/introducing-zoe-deco).

Add your agent to the agents/ directory and Zoe will automatically run and configure it.

## Commands

You can easily send a message to an agent from the shell:

  $ echo -n "message" | nc localhost 30000
  
But sometimes you would like to send these messages using a more simple interface. Take a look at the cmdproc/ folder 
and [this article](http://voiser.org/post/71342980952/zoe-commands) to learn how to write your own commands.


# I don't want mail or twitter or whatever. How can I disable that agent?

Just remove it from the agents/ folder.


# Where can I find more information?

- In English:
 - [Some articles about Zoe](http://voiser.org/)
- In Spanish:
 - [GUL UC3M mailing list](https://gul.uc3m.es/mailman/listinfo/gul)
 - [GUL UC3M twitter account](https://twitter.com/guluc3m)
 - [An introductory video about programming Zoe](https://www.youtube.com/watch?v=3ApdZpXHGns)
