#!/bin/sh
set -e

aerich upgrade
python main.py