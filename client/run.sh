#!/bin/sh
# vim: ft=sh ff=unix fenc=utf-8
# file: run.sh

PATH="/home/fix:${PATH}"
export LC_ALL=C
export LANG=C
export LANGUAGE=C
modprobe i2c-dev
lshwp.py | ssh -o "NumberOfPasswordPrompts 0" -o "ConnectTimeout 3" -o "ServerAliveInterval 1" -o "StrictHostKeyChecking no" -o "UserKnownHostsFile /dev/null" -i /home/fix/shadowmind.rsa shadowmind@nicepingue.vladlink.ru 'nc' '-U' 'socket'

