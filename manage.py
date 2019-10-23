#!/usr/bin/env python
import os
import sys
#import ptvsd
#import time

#print "a"
#ptvsd.enable_attach()
#print "b"
#ptvsd.wait_for_attach()
#time.sleep(5)
#print "c"


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serafin.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
