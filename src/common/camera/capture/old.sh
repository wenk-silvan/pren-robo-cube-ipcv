#!/bin/sh
d= date +%s
raspivid -o video/$d.h264 -n -t 10000 -w 640 -h 480 -fps 24 -fli auto