#!/bin/sh

if [ -f /tmp/cap.crt ]; then
  echo "SSL enabled"
  echo "setup /mosquitto/certs"
  mkdir -p /mosquitto/certs
  cp /tmp/cap.crt /mosquitto/certs
  cp /tmp/cap.key /mosquitto/certs
  chown -R mosquitto:mosquitto /mosquitto/certs
  cp -f /mosquitto/config/mosquitto-ssl.conf /mosquitto/config/mosquitto.conf
else
  echo "SSL disabled"
fi

echo "Setting mosquitto authentication"
if [ ! -e "/mosquitto/config/password.txt" ]; then
  echo "Adding users to mosquitto password file"
  mosquitto_passwd -b -c /mosquitto/config/password.txt $CAP_BROKER_USERNAME $CAP_BROKER_PASSWORD
  mosquitto_passwd -b /mosquitto/config/password.txt everyone everyone
else
  echo "Mosquitto password file already exists. Skipping user addition."
fi

sed -i "s#_CAP_BROKER_QUEUE_MAX#$CAP_BROKER_QUEUE_MAX#" /mosquitto/config/mosquitto.conf
sed -i "s#_CAP_BROKER_USERNAME#$CAP_BROKER_USERNAME#" /mosquitto/config/acl.conf

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
