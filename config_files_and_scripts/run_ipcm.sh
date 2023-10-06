#!/bin/sh

if [ "$(id -u)" -ne 0 ]; then
        echo 'This script must be run by root' >&2
        exit 1
fi

/usr/local/irati/bin/ipcm -a "console, scripting, mad" -c /usr/local/irati/etc/ipcm.conf

