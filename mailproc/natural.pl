#!/usr/bin/env perl

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

use Encode;
use MIME::QuotedPrint::Perl;
use Email::MIME;
use Email::Simple;
use Mail::Address;
use MIME::Base64;
use Config::IniFiles;
use Env qw(ZOE_HOME);
use strict; 

# read the email from the file given as first argument
my $file = $ARGV[0];
local $/;
open(FILE, "<", $file);
my $document = <FILE>; 
close (FILE);

# header parser
my $headers = Email::Simple->new($document);

# extract sender
my $sender_line = $headers->header("From");
my @addrs = Mail::Address->parse($sender_line);
my $sender = $addrs[0]->address();

# search for that sender in zoe-users.conf
$sender = findSender($sender) or exit();

# extract message ID
my $message_id = $headers->header("Message-ID");

# extract the plain text and images from the email file
my @texts = ();
my @images = ();
process($document, \@texts, \@images);

# I'll concentrate only in the first text part
my $text = $texts[0];
$text =~ s/\r\n/\n/g;

# Right now, images are ignored

# Split text into command and extended text
my @lines = split /\n+/, $text;
my $cmd = $lines[0];
my $longcmd = join("\n", @lines[1 .. $#lines]);

# Finally, encode the commands and send the final message.
$cmd     = encode_base64($cmd, "");
$longcmd = encode_base64($longcmd, "");
print "message src=mail&dst=relay&relayto=natural&tag=command&tag=relay&cmd=$cmd&cmdext=$longcmd&sender=$sender&inreplyto=$message_id\n";




#
# Takes a raw email and extracts texts and images
# USAGE:
# 
#   process ($email, \@texts, \@images)
#
sub process {
  my $email = shift;
  my $texts_ref = shift;
  my $images_ref = shift;

  my $parsed = Email::MIME->new($email);
  my @flat = ();
  extract($parsed, \@flat);
 
  my @text_parts  = grep { $_->content_type =~ /text\/plain/ } @flat;
  my @image_parts = grep { $_->content_type =~ /image/ } @flat;
  
  for my $text_part (@text_parts) {
    my $t = $text_part->body_str;
    $t = encode("UTF-8", $t);
    push(@$texts_ref, $t);
  }
  
  for my $image_part (@image_parts) {
    push(@$images_ref, $image_part->body);
  }
}

#
# Extracts all parts from a multipart email into a single, flat array
# USAGE:
#
#   extract ($email, \@result)
#
sub extract {
  my $part = shift;
  my $flatref = shift;
  my $ct = $part->content_type;
  if ($ct =~ /multipart/) {
    my @subparts = $part->subparts;
    foreach my $p (@subparts) {
      my $mime = $p->content_type;
      my $len = $p->subparts;
      if ($len > 0) {
        extract($p, $flatref);
      } else {
        push(@$flatref, $p);
      }
    }
  } else {
    push(@$flatref, $part)
  }
}

#
# Given an email address, find the corresponding Zoe user
#
sub findSender {
  my $sender = shift;
  my $cfg = Config::IniFiles->new (-file => "$ZOE_HOME/etc/zoe-users.conf");
  foreach my $section ($cfg->Sections) {
    my $mail = $cfg->val($section, "mail");
    if (defined $mail and $mail eq $sender) {
      my $sec = $section;
      $sec =~ s/^subject //;
      return $sec;
    }
  }
}

