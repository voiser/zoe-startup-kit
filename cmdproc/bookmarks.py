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

import re
import sys
import argparse

INDEX_FILE = "/var/www/zoe-bookmarks/index.txt"
HTML_FILE = "/var/www/zoe-bookmarks/index.html"

HEADER="""
<html>
<head>
<link href="http://fonts.googleapis.com/css?family=Lato:300" rel="stylesheet" type="text/css">
<script>
function setDisplay(elems, disp) {
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        var style = elem.style;
        style.display = disp;
    }
}

function update() {
    var all = document.getElementsByClassName("_item");
    var text = document.getElementById("search").value;
    var SHOW = "list-item";
    var HIDE = "none";
    if (text == "") {
        setDisplay(all, SHOW);
    } else {
        setDisplay(all, HIDE);
        try {
            var selected = document.querySelectorAll('[class*=' + text + ']');
            if (selected) {
                setDisplay(selected, SHOW);
            }
        } catch (err) {
            // intentionally empty block
        }
    }
}
</script>
<style>
body {
    font-family: 'Lato';
    font-size: 30px;
    color:#444;
    margin:0;
    padding:0;
}
input {
    margin:10px;
    padding:10px;
    background:#ffee88;
    border:1px solid #ccc;
    font-family: 'Lato';
    font-size: 30px;
    color:#444;
}
li {
    list-style:circle;
}
emph {
    color: #888;
    font-size: 80%;
}
h1 {
    font-weight:normal;
}
#header {
    text-align:center;
    background:#eee;
}
#results {
    
}
</style>
</head>
<body>
<div id="header">
<h1>Zoe's bookmarks</h1>
<input id="search" type="text" value="" placeholder="Search..." onkeyup="update()"/>
</div>
<div id="results">
<ul>"""

FOOTER = """
</ul>
</div>
</body>
</html>"""

def get():
    print("bookmark/bm/fav <url> <symbol>")

def run(args):
    urls = args["url"]
    tags = args["symbol"]
    with open(INDEX_FILE, "a") as f:
        for url in urls:
            f.write(url + "\t" + ",".join(tags) + "\n")
    regen()
    print("feedback bookmark saved")

def regen():
    urls = {}
    alltags = []
    allintersections = []
    # taken from http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
    ex = re.compile("(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\t([\w,]*)")
    with open(INDEX_FILE, "r") as f:
        for line in f:
            line = line.strip()
            matches = ex.match(line)
            url = matches.group(1)
            tags = matches.group(2).split(",")
            allintersections.append(tags)
            for t in tags:
                if not t in alltags:
                    alltags.append(t)
            if not url in urls:
                urls[url] = []
            urls[url].extend(tags)
            urls[url] = list(set(urls[url]))
    alltags = sorted(alltags)
    with open(HTML_FILE, "w") as f:
        f.write(HEADER)
        for u in urls:
            tags = urls[u]
            cl = "_item " + " ".join(tags)
            f.write('<li class="' + cl + '"><a href="' + u + '">' + u + '</a> <emph> (in ' + ", ".join(tags) + ')</emph></li>')
        f.write(FOOTER)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--get", action = "store_true")
    parser.add_argument("--run", action = "store_true")
    parser.add_argument("--url", action = "append")
    parser.add_argument("--symbol", action = "append")
    args, unknown = parser.parse_known_args()
    args = vars(args)
    if args["get"]:
        get()
    elif args["run"]:
        run(args)

if __name__ == "__main__":
    main()

