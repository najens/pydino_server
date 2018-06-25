#!/usr/bin/env python
import os
import sys
from app import app as application
import logging
from logging.handlers import RotatingFileHandler

# Set environment variables for dev only
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

sys.path.insert(0, 'var/www/catalog')


if __name__ == '__main__':
    # Setup logging handler
    formatter = logging.Formatter(
        ('[%(asctime)s] {%(pathname)s:%(lineno)d} '
         '- %(name)s - %(levelname)s - %(message)s'))
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    # application.logger.addHandler(handler)
    # Run app on default localhost port 5000
    application.run()
