#!/bin/bash
set -e

if [ ! -z "${CUSTOM_CERT}" ]; then
  echo "使用自定义证书"
  if [ ! -f /cert/private.key ]; then
    echo "生成新证书"
    openssl req -newkey rsa:2048 -sha256 -nodes -keyout /cert/private.key -x509 -days 10000 -out /cert/public.pem -subj "/C=US/ST=Berlin/L=Berlin/O=my_org/CN=${WEBHOOK_HOST}"
  fi
fi

sleep 10
aerich upgrade
python migrate.py
python main.py $@
