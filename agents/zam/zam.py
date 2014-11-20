#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe Agent Manager - https://github.com/RMed/zoe_agent_manager
#
# Copyright (c) 2014 Rafael Medina García <rafamedgar@gmail.com>
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

import os
import shutil
import stat
import subprocess
import zoe
from configparser import ConfigParser
from io import StringIO
from os import environ as env
from os.path import join as path
from semantic_version import Version
from zoe.deco import *

ZCONF_PATH = path(env["ZOE_HOME"], "etc", "zoe.conf")
ZAM_TEMP = path(env["ZOE_VAR"], "zam")
ZAM_LIST = path(env["ZOE_HOME"], "etc", "zam", "list")
ZAM_INFO = path(env["ZOE_HOME"], "etc", "zam", "info")


@Agent(name="zam")
class AgentManager:

    @Message(tags=["add"])
    def add(self, name, source, sender=None):
        """ Add an agent to the list. """
        alist = self.read_list()

        self.add_to_list(name, source, alist, False, sender)

    @Message(tags=["clean"])
    def clean(self):
        """ Clean the temp data stored in var/zam. """
        try:
            shutil.rmtree(ZAM_TEMP)
        except:
            # Nothing to remove?
            pass

    @Message(tags=["forget"])
    def forget(self, name, sender=None):
        """ Remove an agent from the agent list.

            The agent must be uninstalled first, and means that in order to
            install it again, the source must be provided.
        """
        alist = self.read_list()

        if self.installed(name, alist):
            msg = "Agent %s is installed, uninstall it first" % name
            print(msg)
            return self.feedback(msg, sender)

        if name in alist.sections():
            alist.remove_section(name)
            self.write_list(alist)
        msg = "Removed agent %s from agent list" % name
        print(msg)
        return self.feedback(msg, sender)

    @Message(tags=["install"])
    def install(self, name, source=None, sender=None):
        """ Install an agent from source. """
        alist = self.read_list()

        if self.installed(name, alist):
            msg = "Agent %s is already installed" % name
            print(msg)
            return self.feedback(msg, sender)

        if name not in alist.sections():
            if not source:
                msg = "Source not found"
                print(msg)
                return self.feedback(msg, sender)

            alist = self.add_to_list(name, source, alist, sender=sender)

        self.clean()

        temp = path(ZAM_TEMP, name)
        git_code = self.fetch(name, source)

        if git_code != 0:
            msg = "Could not fetch source"
            print(msg)
            self.clean()
            return self.feedback(msg, sender)

        a_info = self.parse_info(path(temp, "zam", "info"));

        # Version is mandatory!
        if not a_info["version"]:
            msg = "Missing version in info file for %s" % name
            print(msg)
            return self.feedback(msg, sender)

        # PREINSTALL
        preinst = path(temp, "zam", "preinst")
        if os.path.isfile(preinst):
            st = os.stat(preinst)
            os.chmod(preinst, st.st_mode | stat.S_IEXEC)
            proc = subprocess.call([preinst, ])

            print("Ran preinst script, got code %i" % proc)

        # INSTALL
        # Generate list of source files
        file_list = self.move_files(name)

        # Save agent file list
        with open(path(ZAM_INFO, name + ".list"), "w+") as dfile:
            for f in file_list:
                dfile.write("%s\n" % f)

        # Make script executable
        #
        # There may be cases where an agent is only formed by natural
        # language files, so this key may not be present.
        if a_info["script"]:
            script = path(env["ZOE_HOME"], "agents",
                name, a_info["script"])
            st = os.stat(script)
            os.chmod(script, st.st_mode | stat.S_IEXEC)

        # Make cmdproc scripts executable
        for f in [cf for cf in file_list if cf.startswith("cmdproc")]:
            df = path(env["ZOE_HOME"], f)
            st = os.stat(df)
            os.chmod(df, st.st_mode | stat.S_IEXEC)

        # Add agent to the zoe.conf file
        zconf = self.read_conf()

        ports = []
        for sec in zconf.sections():
            if "port" in zconf[sec]:
                ports.append(int(zconf[sec]["port"]))
        ports = sorted(ports)

        if not ports:
            ports.append(env["ZOE_SERVER_PORT"])
        free_port = ports[0]
        while free_port in ports:
            free_port += 1

        zconf.add_section("agent " + name)
        zconf["agent " + name]["port"] = str(free_port)

        # Topics are optional
        if a_info["topics"]:
            topics = a_info["topics"].split(" ")
            zconf = self.topics_install(name, topics, zconf)

        self.write_conf(zconf)

        # Update agent list
        alist[name]["installed"] = "1"
        alist[name]["version"] = a_info["version"]

        self.write_list(alist)

        print("Agent %s installed correctly" % name)

        # POSTINSTALL
        postinst = path(temp, "zam", "postinst")
        if os.path.isfile(postinst):
            st = os.stat(postinst)
            os.chmod(postinst, st.st_mode | stat.S_IEXEC)
            proc = subprocess.call([postinst, ])
            print("Ran postinst script, got code %i" % proc)

        # Store config files list (if any)
        info_conf = path(temp, "zam", "conf")
        if os.path.isfile(info_conf):
            conflist = []
            with open(info_conf, "r") as conffile:
                for c in conffile.read().splitlines():
                    conflist.append(c)

            with open(path(ZAM_INFO, name + ".conffiles"), "w+") as stored_conf:
                for c in conflist:
                    stored_conf.write("%s\n" % c)

        # Cleanup
        self.clean()

        # Launch the agent (and register it)
        if a_info["script"]:
            return [
                self.feedback("Agent %s installed correctly" % name, sender),
                self.launch(name, sender)
            ]

    @Message(tags=["launch"])
    def launch(self, name, sender=None):
        """ Launch an agent. """
        agent_dir = path(env["ZOE_HOME"], "agents", name)
        if not os.path.isdir(agent_dir):
            msg = "Agent %s does not exist!" % name
            print(msg)
            return self.feedback(msg, sender)

        # Redirect stdout and stderr to zam's log
        log_file = open(path(env["ZOE_LOGS"], "zam.log"), "a")
        proc = subprocess.Popen([path(env["ZOE_HOME"], "zoe.sh"),
            "launch-agent", name], stdout=log_file, stderr=log_file,
            cwd=env["ZOE_HOME"])

        zconf = self.read_conf()

        # Force the agent to register
        port = zconf["agent " + name]["port"]
        launch_msg = {
            "dst": "server",
            "tag": "register",
            "name": name,
            "host": env["ZOE_SERVER_HOST"],
            "port": port
        }


        return [
            self.feedback("Launching agent %s" % name, sender),
            zoe.MessageBuilder(launch_msg)
        ]

    @Message(tags=["purge"])
    def purge(self, name, sender=None):
        """ Remove an agent's configuration files. """
        # Uninstall the agent
        self.remove(name)

        # Remove config files
        confpath = path(ZAM_INFO, name + ".conffiles")
        if not os.path.isfile(confpath):
            msg = "Agent %s has no config files" % name
            print(msg)
            return self.feedback(msg, sender)

        with open(confpath, "r") as conflist:
            for cf in conflist.read().splitlines():
                c = path(env["ZOE_HOME"], cf)
                print("Removing %s" % c)
                try:
                    os.remove(c)
                except:
                    # Nothing to remove?
                    pass

        os.remove(confpath)

        msg = "Agent %s purged" % name
        print(msg)

        return self.feedback(msg, sender)

    @Message(tags=["remove"])
    def remove(self, name, sender=None):
        """ Uninstall an agent.

            Any additional files (such as configuration files) are kept
            in case the agent is installed again.
        """
        alist = self.read_list()

        if not self.installed(name, alist):
            msg = "Agent %s is not installed" % name
            print(msg)
            return self.feedback(msg, sender)

        if self.running(name):
            self.stop(name, sender)

        # Remove from zoe.conf
        zconf = self.read_conf()

        if "agent " + name in zconf.sections():
            zconf.remove_section("agent " + name)

        for topic in [t for t in zconf.sections() if t.startswith("topic")]:
            topic_agents = zconf[topic]["agents"].split(" ")

            try:
                topic_agents.remove(name)
                if not topic_agents:
                    zconf.remove_section(topic)
                else:
                    zconf[topic]["agents"] = " ".join(topic_agents)

            except:
                # Not in the list
                continue

        self.write_conf(zconf)

        # Remove agent files and directories
        flist_path = path(ZAM_INFO, name + ".list")
        with open(flist_path, "r") as flist:
            for f in flist.read().splitlines():
                l = path(env["ZOE_HOME"], f)
                # Remove final file
                os.remove(l)
                # Remove the tree that was generated in the installation
                dirs = os.path.split(l)
                while dirs[0] != "/":
                    if os.listdir(dirs[0]):
                        break
                    shutil.rmtree(dirs[0])
                    dirs = os.path.split(dirs[0])

        os.remove(flist_path)

        # Update agent list
        alist[name]["installed"] = "0"
        alist[name]["version"] = ""
        self.write_list(alist)

        msg = "Agent %s uninstalled" % name
        print(msg)

        return self.feedback(msg, sender)

    @Message(tags=["restart"])
    def restart(self, name, sender=None):
        """ Restart an agent. """
        if not self.running(name):
            msg = "Agent %s is not running" % name
            print(msg)
            return self.feedback(msg, sender)

        # Redirect stdout and stderr to zam's log
        log_file = open(path(env["ZOE_LOGS"], "zam.log"), "a")
        proc = subprocess.Popen([path(env["ZOE_HOME"], "zoe.sh"),
            "restart-agent", name], stdout=log_file, stderr=log_file,
            cwd=env["ZOE_HOME"])

        return self.feedback("Restarting agent %s" % name, sender)

    @Message(tags=["stop"])
    def stop(self, name, sender=None):
        """ Stop an agent's execution. """
        if not self.running(name):
            msg = "Agent %s is not running" % name
            print(msg)
            return self.feedback(msg, sender)

        # Redirect stdout and stderr to zam's log
        log_file = open(path(env["ZOE_LOGS"], "zam.log"), "a")
        proc = subprocess.Popen([path(env["ZOE_HOME"], "zoe.sh"),
            "stop-agent", name], stdout=log_file, stderr=log_file,
            cwd=env["ZOE_HOME"])

        return self.feedback("Stopping agent %s" % name, sender)

    @Message(tags=["update"])
    def update(self, name, sender=None):
        """ Update an installed agent. """
        alist = self.read_list()

        if not self.installed(name, alist):
            msg = "Agent %s is not installed" % name
            print(msg)
            return self.feedback(msg, sender)

        self.clean()

        # Get source
        temp = path(ZAM_TEMP, name)
        git_code = self.fetch(name, alist[name]["source"])

        if git_code != 0:
            msg = "Could not fetch source"
            print(msg)
            self.clean()
            return self.feedback(msg, sender)

        # Parse information
        a_info = self.parse_info(path(temp, "zam", "info"));

        # Version is mandatory!
        if not a_info["version"]:
            msg = "Missing version in info file for %s" % name
            print(msg)
            return self.feedback(msg, sender)

        remote_ver = Version(a_info["version"])
        local_ver = Version(alist[name]["version"])

        if remote_ver <= local_ver:
            msg = "Agent %s is already up-to-date" % name
            print(msg)
            return self.feedback(msg, sender)

        # PREUPDATE
        preupd = path(temp, "zam", "preupd")
        if os.path.isfile(preupd):
            st = os.stat(preupd)
            os.chmod(preupd, st.st_mode | stat.S_IEXEC)
            proc = subprocess.call([preupd, ])
            print("Ran preupd script, got code %i" % proc)

        # UPDATE
        # Move files
        file_list = self.move_files(name, True)

        # Save agent file list
        with open(path(ZAM_INFO, name + ".list"), "w+") as dfile:
            for f in file_list:
                dfile.write("%s\n" % f)

        # Make script executable
        #
        # There may be cases where an agent is only formed by natural
        # language files, so this key may not be present.
        if a_info["script"]:
            script = path(env["ZOE_HOME"], "agents",
                name, a_info["script"])
            st = os.stat(script)
            os.chmod(script, st.st_mode | stat.S_IEXEC)

        # Make cmdproc scripts executable
        for f in [cf for cf in file_list if cf.startswith("cmdproc")]:
            df = path(env["ZOE_HOME"], f)
            st = os.stat(df)
            os.chmod(df, st.st_mode | stat.S_IEXEC)

        # Update version
        alist[name]["version"] = str(remote_ver)
        self.write_list(alist)

        # Update topics (if any)
        if a_info["topics"]:
            topics = a_info["topics"].split(" ")
            zconf = self.topics_update(name, topics)

            self.write_conf(zconf)

        # POSTUPDATE
        postupd = path(temp, "zam", "postupd")
        if os.path.isfile(postupd):
            st = os.stat(postupd)
            os.chmod(postupd, st.st_mode | stat.S_IEXEC)
            proc = subprocess.call([postupd, ])
            print("Ran postupd script, got code %i" % proc)

        # Cleanup
        self.clean()


        if a_info["script"]:
            # Restart the agent
            return [
                self.feedback("Updated agent %s" % name, sender),
                self.restart(name, sender)
            ]

    def add_to_list(self, name, source, alist, ret=True, sender=None):
        """ Add an agent to the list.

            name -- name of the anget to install. Will be checked against
                the agent list
            source -- git repository URL to the source
            alist -- agent list file
            ret -- whether or not this function should return the new list
        """
        new_alist = alist

        if name in new_alist.sections():
            msg = "Agent %s is already in the list" % name
            print(msg)
            return self.feedback(msg, sender)

        new_alist.add_section(name)
        new_alist[name]["source"] = str(source)
        new_alist[name]["installed"] = "0"
        new_alist[name]["version"] = ""

        self.write_list(new_alist)

        print("Added new agent %s to the list" % name)

        if ret:
            return new_alist

    def feedback(self, message, user):
        """ If there is a sender, send feedback message with status
            through Jabber.

            message -- message to send
            user -- user to send the message to
        """
        if not user:
            return

        to_send = {
            "dst": "relay",
            "tag": "relay",
            "relayto": "jabber",
            "to": user,
            "msg": message
        }

        return zoe.MessageBuilder(to_send)

    def fetch(self, name, source):
        """ Download the source of the agent to var/zam/name. """
        temp = path(ZAM_TEMP, name)
        alist = self.read_list()

        try:
            if not source:
                src = alist[name]["source"]
            else:
                src = source
        except:
            return -1

        return subprocess.call(["git", "clone", src, temp])

    def installed(self, name, alist):
        """ Check if an agent is installed or not. """
        if name in alist.sections():
            if alist[name]["installed"] == "1":
                return True

        return False

    def move_files(self, name, updating=False):
        """ Move the files and directories to their corresponding ZOE_HOME
            counterpart.

            To be used only by install() and update()

            Returns the destination file list
        """
        source_dir = path(ZAM_TEMP, name)

        # Generate list of source files
        src_list = []
        for d in os.listdir(source_dir):
            if os.path.isdir(path(source_dir, d)) and d not in [".git", "zam"]:
                subdir = path(source_dir, d)
                for root, dirs, files in os.walk(subdir):
                    for f in files:
                        src_list.append(path(root, f))

        if updating:
            # Diff list
            diff_list = []
            for src in src_list:
                stripped = src.replace(source_dir, "")
                stripped = self.remove_slash(stripped)
                diff_list.append(stripped)

            # Compare file lists and remove those not present in the update
            alist_path = path(ZAM_INFO, name + ".list")
            with open(alist_path, "r") as alist:
                for f in [p for p in alist.read().splitlines() if p not in diff_list]:
                    l = path(env["ZOE_HOME"], f)
                    # Remove final file
                    os.remove(l)
                    # Remove the generated tree
                    dirs = os.path.split(l)
                    while dirs[0] != "/":
                        if os.listdir(dirs[0]):
                            break
                        shutil.rmtree(dirs[0])
                        dirs = os.path.split(dirs[0])

        # Move files
        file_list = []
        for src in src_list:
            stripped = src.replace(source_dir, "")
            stripped = self.remove_slash(stripped)
            dst = os.path.dirname(path(env["ZOE_HOME"], stripped))

            try:
                os.makedirs(dst)
            except:
                # Tree already exists?
                pass

            shutil.copy(src, dst)
            # new_path = shutil.copy(src, dst)
            # new_path = new_path.replace(env["ZOE_HOME"], "")
            # new_path = self.remove_slash(new_path)

            file_list.append(stripped)

        return file_list

    def parse_info(self, info_path):
        """ When installing an agent, parse the information file and return
            a dictionary with the information.

            In the case the specific field is not present, give value None
            and continue.
        """
        info = ConfigParser()
        # Add a dummy section
        info.read_string(StringIO(
            "[info]\n%s" % open(info_path).read()).read())

        data = {
            "agent": None,
            "version": None,
            "license": None,
            "maintainer": None,
            "script": None,
            "topics": None,
            "description": None
        }

        for key in info["info"].keys():
            data[key] = info["info"][key]

        return data

    def read_conf(self):
        """ Read the Zoe configuration file located in etc/zoe.conf. """
        conf = ConfigParser()
        conf.read(ZCONF_PATH)

        return conf

    def read_list(self):
        """ Read the agent list.

            Returns ConfigParser object.
        """
        alist = ConfigParser()
        alist.read(ZAM_LIST)

        return alist

    def remove_slash(self, path):
        """ Remove initial slash (/) from path (if any). """
        new_path = path

        if path.startswith("/"):
            new_path = path[0].replace("/", "") + path[1:]

        return new_path

    def running(self, name):
        """ Check if an agent is running. """
        # We depend on the .pid files here
        pid_path = path(env["ZOE_VAR"], name + ".pid")

        if os.path.isfile(pid_path):
            return True

        return False

    def topics_install(self, agent, topics, conf=None):
        """ Set the topics an agent listens to DURING INSTALLATION.

            If the zoe conf file is not passed, will read it.
        """
        zconf = conf
        if not zconf:
            zconf = self.read_conf()

        for topic in topics:
            topic_section = "topic " + topic

            if topic_section not in zconf.sections():
                zconf.add_section(topic_section)
                zconf[topic_section]["agents"] = ""

            topic_agents = zconf[topic_section]["agents"].split(" ")

            if agent not in topic_agents:
                topic_agents.append(agent)
                zconf[topic_section]["agents"] = " ".join(topic_agents)

        return zconf

    def topics_update(self, agent, topics, conf=None):
        """ Set the topics an agent listens to DURING UPDATE.

            If the zoe conf file is not passed, will read it.
        """
        zconf = conf
        if not zconf:
            zconf = self.read_conf()

        # Insert missing topics
        for topic in topics:
            topic_section = "topic " + topic

            if topic_section not in zconf.sections():
                zconf.add_section(topic_section)
                zconf[topic_section]["agents"] = ""

        for topic_section in [
                t for t in zconf.sections() if t.startswith("topic")]:
            topic_agents = zconf[topic_section]["agents"].split(" ")

            if agent in topic_agents and topic_section.replace(
                    "topic ", "") not in topics:
                # Currently present and should not be
                topic_agents.remove(agent)

            elif agent not in topic_agents and topic_section.replace(
                    "topic ", "") in topics:
                # Not present and should be
                topic_agents.append(agent)

            zconf[topic_section]["agents"] = " ".join(topic_agents)

        return zconf

    def write_conf(self, zconf):
        """ Write Zoe configuration into etc/zoe.conf. """
        with open(ZCONF_PATH, 'w') as configfile:
            zconf.write(configfile)

    def write_list(self, lparser):
        """ Write data into agent list. """
        with open(ZAM_LIST, 'w') as listfile:
            lparser.write(listfile)
