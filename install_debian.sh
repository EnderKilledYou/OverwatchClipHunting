#!/usr/bin/env bash
apt update -y
apt upgrade -y
apt install python3 python3-pip -y
apt-get install ffmpeg libsm6 libxext6 -y
apt-get install -y cron
apt-get install -y ca-certificates
sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
update-ca-certificates
apt-get update
apt-get -y upgrade

apt-get update
apt-get -y upgrade

node -v
npm -v
