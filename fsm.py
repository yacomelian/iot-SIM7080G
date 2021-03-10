#!/usr/bin/env python3
"""
Reads information from SIM7080G Pi Hat Module for IOT
"""

from classes import *
import argparse
import logging
import sys
import time
import uuid
import yaml


if __name__ == "__main__":
    # The client code.
    context = Context(powerOff())
    context.request1()
    context.request2()