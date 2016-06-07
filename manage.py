#!/usr/bin/env python
import os
import sys

import dotenv

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == "__main__":
    dotenv.read_dotenv()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vincent.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)