#!/bin/sh
set -e

sleep 20
aerich upgrade
python main.py