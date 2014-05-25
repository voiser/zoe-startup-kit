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
- . etc/environment.sh
- ./zoe.sh start
- ./zoe.sh status

  If there are dead agents, check their log files (at the log/ directory) to figure out the error. It is probably a misconfiguration. 



# How do I add my own features

- STEP ONE: Write your own agent. Take a look at agents/test and [this article](http://voiser.org/post/69721172250/introducing-zoe-deco)

Now you can make your agent work by doing in a shell:

  $ echo "message for your agent" | nc localhost 30000

- STEP TWO (optional) If you want to interact directly with your agent, you should specify a natural language command. [Take a look at this article](http://voiser.org/post/71342980952/zoe-commands)


# I don't want mail or twitter or whatever. How can I disable that agent?

Just remove it from the agents/ folder.


# Where can I find more information?

- In English:
 - [Some articles about Zoe](http://voiser.org/)
- In Spanish:
 - [GUL UC3M mailing list](https://gul.uc3m.es/mailman/listinfo/gul)
 - [GUL UC3M twitter account](https://twitter.com/guluc3m)
 - [An introductory video about programming Zoe](https://www.youtube.com/watch?v=3ApdZpXHGns)
