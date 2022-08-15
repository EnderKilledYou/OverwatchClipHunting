#!/usr/bin/env bash
  apt update -y
  apt upgrade -y
  apt install python3 python3-pip -y
  apt-get install ffmpeg libsm6 libxext6  -y
  apt-get install -y cron