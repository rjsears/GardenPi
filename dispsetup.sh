#!/bin/sh
if ! grep -q 'Raspberry Pi' /proc/device-tree/model || (grep -q okay /proc/device-tree/soc/v3d@7ec00000/status 2> /dev/null || grep -q okay /proc/device-tree/soc/firmwarekms@7e600000/status 2> /dev/null) ; then
if xrandr --output HDMI-1 --primary --mode 800x480 --rate 65.68 --pos 0x0 --rotate left --dryrun ; then 
xrandr --output HDMI-1 --primary --mode 800x480 --rate 65.68 --pos 0x0 --rotate left
fi
fi
if [ -e /usr/share/tssetup.sh ] ; then
. /usr/share/tssetup.sh
fi
exit 0