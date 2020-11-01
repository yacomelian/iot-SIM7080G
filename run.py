#!/usr/bin/env python3
"""
Reads information from SIM7080G Pi Hat Module for IOT
"""

from classes import simcom
import argparse
import logging
import sys
import uuid
import yaml


def parse_args():
    global args
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-e", "--exec", action="store",
        required=False,
        choices=['batch', 'simulate', 'demo'],
        help="""Select a different execution type, NOT USE IN REAL MODE:
         batch: read from csv files in folder
         simulate: read from created /dev/* device created
         demo: read from csv to create realtime data
         """)
    ap.add_argument('--verbose', '-v', action='count', default=0)
    args = vars(ap.parse_args())


""" Loads configuration, stored in global config """


def load_config():
    global cfg
    cfg = yaml.safe_load(open(str(sys.path[0]) + "/config.yml"))


""" Enables and configures logging """


def set_logging(level='INFO'):
    strlevel = 'logging.' + level
    logging.basicConfig(stream=sys.stderr, level=eval(strlevel))


"""
    Setup global environment.
    This works like arduino model, setup and loop
"""


def setup():
    parse_args()
    load_config()
    if (args['verbose'] > 0):
        set_logging('DEBUG')
    else:
        set_logging(cfg['logging'])

    global session_uuid
    session_uuid = str(uuid.uuid1())


""" Read GPS data """


def main():
    sim = simcom(None)
    sim.test_gps()
 

if __name__ == "__main__":
    # TODO
    #  - GUI inter
    dateformat = "%d/%m/%Y-%H:%M:%S"
    setup()
    try:
        main()
    except KeyboardInterrupt:
        # Not an error, so no need for a stack trace.
        print("\nOperation cancelled by user")
        sys.exit(1)
