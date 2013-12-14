#!/usr/bin/env python
import os
import sys

root_path = os.path.abspath(os.path.join(__file__, '..', '..'))
sys.path.insert(0, root_path)
print root_path

if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webserver.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
