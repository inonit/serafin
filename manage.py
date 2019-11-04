#!/usr/bin/env python
import os
import sys
import ptvsd
import time


if "0.0.0.0:8000" in sys.argv:
    print "a"
    ptvsd.enable_attach()
    print "b"
    #ptvsd.wait_for_attach()
    #time.sleep(5)
    print "c"
    #add --noreload flag to enable debuging with ptvsd


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serafin.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
