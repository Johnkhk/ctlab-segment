#!/bin/bash

docker run --platform linux/amd64 -it --rm \
	-p 9000:8800 \
	-v /Users/john/Desktop/code/CTLAB:/workspace \
	-e DISPLAY=$DISPLAY \
	-e QT_X11_NO_MITSHM=1 \
	-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
	ct_vis:latest \
	bash
