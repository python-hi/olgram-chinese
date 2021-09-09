#!/bin/sh
set -e

sleep 10
aerich upgrade
python main.py