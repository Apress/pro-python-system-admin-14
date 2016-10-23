#!/usr/bin/env python

import subprocess
import os

print "I am running with the following user id: ", os.getuid()
subprocess.Popen(('/bin/sh', '-c', 'echo "I am an external shell process with effective user id:"; id'), 
                 preexec_fn=os.setuid(501))
