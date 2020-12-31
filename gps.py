#!/usr/bin/env python3
"""
Reads information from SIM7080G Pi Hat Module for IOT
"""

from classes import simcom
import argparse
import logging
import sys
import time
import uuid
import yaml


def parse_args():
    global args
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--verbose',
        '-v',
        action='count',
        default=0,
        help=""" DEBUG 
            LINEA 2
        """)
    ap.add_argument(
        '--error',
        '-e', 
        action='count',
        default=0,
        help=""" ERROR 
            LINEA 2
        """ )
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
    elif (args['error'] > 0):
        set_logging('ERROR')
    else:
        set_logging(cfg['logging'])

    global session_uuid
    session_uuid = str(uuid.uuid1())


""" Read GPS data """


def main():
    sim = simcom(None)
    try:
        while True:
            sim.getGpsPosition()
            time.sleep(10)
    except KeyboardInterrupt:
        # Not an error, so no need for a stack trace.
        print("\nUser canceled - Shutting down module SIMCOM")
    except Exception as e:
        print (e)
        print("\nShutting down module SIMCOM")
    finally:
        del sim  # Delete object and Power Down SIMCOM
        sys.exit(1)

if __name__ == "__main__":
    # TODO
    #  - GUI inter
    dateformat = "%d/%m/%Y-%H:%M:%S"
    setup()
    main()
