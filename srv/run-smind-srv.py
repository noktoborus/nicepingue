#!/bin/sh
# vim: ft=sh ff=unix fenc=utf-8
# file: run.sh

(
	while true;
	do
		rm -f /home/shadowmind/socket
		sudo -u root -g shadowmind nohup smind-srv.py >/dev/null 2>&1
		sleep 1
	done
)

