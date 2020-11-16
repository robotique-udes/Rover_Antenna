To enable GPSD driver (must be sudoer or prefix command with 'sudo'):
    systemctl enable gpsd.service
    gpsd /dev/ttyUSB0

Test your configuration (reads device messages routed through the gpsd driver):
    gpsmon

Troubleshoot gps device with (reads device messages directly):
    gpsmon /dev/ttyUSB0

Debugging:
- kill everything:
    killall gpsd
    rm /run/gpsd.sock
