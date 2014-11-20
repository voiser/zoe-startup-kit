#!/usr/bin/env perl
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

use Getopt::Long qw(:config pass_through);

my $get;
my $run;
my $add;
my $clean;
my $forget;
my $install;
my $installsrc;
my $launch;
my $purge;
my $remove;
my $restart;
my $stop;
my $update;

my $sender;
my @strings;

GetOptions("get" => \$get,
           "run" => \$run,
           "msg-sender=s" => \$sender,
           "a" => \$add,
           "c" => \$clean,
           "f" => \$forget,
           "i" => \$install,
           "is" => \$installsrc,
           "l" => \$launch,
           "p" => \$purge,
           "r" => \$remove,
           "rs" => \$restart,
           "s" => \$stop,
           "u" => \$update,
           "string=s" => \@strings);

if ($get) {
  &get;
} elsif ($run and $add) {
  &add;
} elsif ($run and $clean) {
  &clean;
} elsif ($run and $forget) {
  &forget;
} elsif ($run and $install) {
  &install;
} elsif ($run and $installsrc) {
  &install_source;
} elsif ($run and $launch) {
  &launch;
} elsif ($run and $purge) {
  &purge;
} elsif ($run and $remove) {
  &remove;
} elsif ($run and $restart) {
  &restart;
} elsif ($run and $stop) {
  &stop;
} elsif ($run and $update) {
  &update;
}

#
# Commands in the script
#
sub get {
  print("--a  add /the agent <string> from <string>\n");
  print("--c  clean the temp/temporary directory\n");
  print("--f forget /the agent <string>\n");
  print("--i install /the agent <string>\n");
  print("--is install /the agent <string> from <string>\n");
  print("--l launch /the agent <string>\n");
  print("--p purge /the agent <string>\n");
  print("--r remove/uninstall /the agent <string>\n");
  print("--rs restart /the agent <string>\n");
  print("--s stop /the agent <string>\n");
  print("--u update /the agent <string>\n");
  
  print("--a añade /el agente <string> desde <string>\n");
  print("--c limpia el directorio temp/temporal\n");
  print("--f olvida /el agente <string>\n");
  print("--i instala /el agente <string>\n");
  print("--is instala /el agente <string> desde <string>\n");
  print("--l lanza /el agente <string>\n");
  print("--p purga /el agente <string>\n");
  print("--r borra/desinstala /el agente <string>\n");
  print("--rs reinicia /el agente <string>\n");
  print("--s para/detén /el agente <string>\n");
  print("--u actualiza /el agente <string>\n");
}

#
# Add an agent to the list
#
sub add {
  print("message dst=zam&tag=add&name=$strings[0]&source=$strings[1]&sender=$sender\n");
}

#
# Clean temp directory
#
sub clean {
  print("message dst=zam&tag=clean\n");
}

#
# Forget an agent
#
sub forget {
  print("message dst=zam&tag=forget&name=$strings[0]&sender=$sender\n");
}

#
# Install an agent
#
sub install {
  print("message dst=zam&tag=install&name=$strings[0]&sender=$sender\n");
}

#
# Install an agent from source
#
sub install_source {
  print("message dst=zam&tag=install&name=$strings[0]&source=$strings[1]&sender=$sender\n");
}

#
# Launch an agent
#
sub launch {
  print("message dst=zam&tag=launch&name=$strings[0]&sender=$sender\n");
}

#
# Purge an agent
#
sub purge {
  print("message dst=zam&tag=purge&name=$strings[0]&sender=$sender\n");
}

#
# Remove/Uninstall an agent
#
sub remove {
  print("message dst=zam&tag=remove&name=$strings[0]&sender=$sender\n");
}

#
# Restart an agent
#
sub restart {
  print("message dst=zam&tag=restart&name=$strings[0]&sender=$sender\n");
}


#
# Stop an agent
#
sub stop {
  print("message dst=zam&tag=stop&name=$strings[0]&sender=$sender\n");
}

#
# Update an agent
#
sub update {
  print("message dst=zam&tag=update&name=$strings[0]&sender=$sender\n");
}
