#!/bin/bash

sudo modprobe ifb
sudo ip link set dev ifb0 up
sudo tc qdisc add dev eth0 ingress
sudo tc filter add dev eth0 parent ffff: \ 
protocol ip u32 match u32 0 0 flowid 1:1 action mirred egress redirect dev ifb0