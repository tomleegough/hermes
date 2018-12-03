#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/hermes/")

from hermes import app as application
application.secret_key = 'dev'
