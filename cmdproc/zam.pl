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
my $lang;
my @strings;

GetOptions("get"                   => \$get,
           "run"                   => \$run,
           "msg-sender-uniqueid=s" => \$sender,
           "a"                     => \$add,
           "c"                     => \$clean,
           "f"                     => \$forget,
           "i"                     => \$install,
           "is"                    => \$installsrc,
           "l"                     => \$launch,
           "p"                     => \$purge,
           "r"                     => \$remove,
           "rs"                    => \$restart,
           "s"                     => \$stop,
           "u"                     => \$update,
           "lang=s"                => \$lang,
           "string=s"              => \@strings);

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
  print("--a --lang=en add /the agent <string> from <string>\n");
  print("--c --lang=en clean the temp/temporary directory\n");
  print("--f --lang=en forget /the agent <string>\n");
  print("--i --lang=en install /the agent <string>\n");
  print("--is --lang=en install /the agent <string> from <string>\n");
  print("--l --lang=en launch /the agent <string>\n");
  print("--p --lang=en purge /the agent <string>\n");
  print("--r --lang=en remove/uninstall /the agent <string>\n");
  print("--rs --lang=en restart /the agent <string>\n");
  print("--s --lang=en stop /the agent <string>\n");
  print("--u --lang=en update /the agent <string>\n");

  print("--a --lang=es añade /el agente <string> desde <string>\n");
  print("--c --lang=es limpia el directorio temp/temporal\n");
  print("--f --lang=es olvida /el agente <string>\n");
  print("--i --lang=es instala /el agente <string>\n");
  print("--is --lang=es instala /el agente <string> desde <string>\n");
  print("--l --lang=es lanza /el agente <string>\n");
  print("--p --lang=es purga /el agente <string>\n");
  print("--r --lang=es borra/desinstala /el agente <string>\n");
  print("--rs --lang=es reinicia /el agente <string>\n");
  print("--s --lang=es para/detén /el agente <string>\n");
  print("--u --lang=es actualiza /el agente <string>\n");
}

#
# Add an agent to the list
#
sub add {
  print("message dst=zam&tag=add&name=$strings[0]&source=$strings[1]&sender=$sender&locale=$lang\n");
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
  print("message dst=zam&tag=forget&name=$strings[0]&sender=$sender&locale=$lang\n");
}

#
# Install an agent
#
sub install {
  print("message dst=zam&tag=install&name=$strings[0]&sender=$sender&locale=$lang\n");
}

#
# Install an agent from source
#
sub install_source {
  print("message dst=zam&tag=install&name=$strings[0]&source=$strings[1]&sender=$sender&locale=$lang\n");
}

#
# Launch an agent
#
sub launch {
  print("message dst=zam&tag=launch&name=$strings[0]&sender=$sender&locale=$lang\n");
}

#
# Purge an agent
#
sub purge {
  print("message dst=zam&tag=purge&name=$strings[0]&sender=$sender&locale=$lang\n");
}

#
# Remove/Uninstall an agent
#
sub remove {
  print("message dst=zam&tag=remove&name=$strings[0]&sender=$sender&locale=$lang\n");
}

#
# Restart an agent
#
sub restart {
  print("message dst=zam&tag=restart&name=$strings[0]&sender=$sender&locale=$lang\n");
}


#
# Stop an agent
#
sub stop {
  print("message dst=zam&tag=stop&name=$strings[0]&sender=$sender&locale=$lang\n");
}

#
# Update an agent
#
sub update {
  print("message dst=zam&tag=update&name=$strings[0]&sender=$sender&locale=$lang\n");
}
