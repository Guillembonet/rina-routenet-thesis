[ -f /usr/bin/routenet.client ] && (mv /usr/bin/routenet /usr/bin/routenet.dummy; mv /usr/bin/routenet.client /usr/bin/routenet) || echo "client is already used"  
