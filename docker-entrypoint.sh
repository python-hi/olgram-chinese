#!/bin/sh
set -e

if [[ -z "${CUSTOM_CERT}" ]]; then
  if [ ! -f /cert/private.key ]; then
    openssl req -newkey rsa:2048 -sha256 -nodes -keyout /cert/private.key -x509 -days 1000 -out /cert/public.pem -subj "/C=US/ST=Berlin/L=Berlin/O=my_org/CN=my_cn"
  fi
fi

sleep 10
aerich upgrade
python main.py
