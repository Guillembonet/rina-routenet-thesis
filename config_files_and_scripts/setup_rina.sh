#!/bin/sh

if [ "$(id -u)" -ne 0 ]; then
        echo 'This script must be run by root' >&2
        exit 1
fi

ip link add link enp0s3 name enp0s3.100 type vlan id 100
ip link add link enp0s8 name enp0s8.101 type vlan id 101
ip link add link enp0s9 name enp0s9.102 type vlan id 102
ip link set dev enp0s3 up
ip link set dev enp0s3.100 up
ip link set dev enp0s8 up
ip link set dev enp0s8.101 up
ip link set dev enp0s9 up
ip link set dev enp0s9.102 up

/home/irati/Documents/stack/load-irati-modules

