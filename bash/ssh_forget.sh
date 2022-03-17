#
# remove the remembered key for a host that is expected to change
#
USB_IP=192.168.7.2

# figure out what host we should forget
if [ -n "$1" ]
then
    host="$1"
else
    host="$USB_IP"
fi

# delete the known key for that host
ssh-keygen -f $HOME/.ssh/known_hosts -R "$host"
