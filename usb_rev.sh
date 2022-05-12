mv /lib/modules/`uname -r`/kernel/drivers/usb/storage/usb-storage.ko.blacklist /lib/modules/`uname -r`/kernel/drivers/usb/storage/usb-storage.ko
chmod 777 /media/
chmod 755 /usr/lib/gvfs/gvfsd-mtp
chmod 755 /usr/lib/gvfs/gvfsd-gphoto2
chmod 755 /usr/lib/gvfs/gvfs-gphoto2-volume-monitor
chmod 755 /usr/lib/gvfs/gvfs-mtp-volume-monitor
chmod 755 /usr/lib/gvfs/gvfsd-afp
chmod 755 /usr/lib/gvfs/gvfs-afc-volume-monitor
