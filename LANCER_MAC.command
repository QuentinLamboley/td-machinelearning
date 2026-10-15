#!/bin/sh
cd "$(dirname "$0")" || exit 1
sh ./LANCER_LINUX_MAC.sh
printf '\nAppuyer sur Entrée pour fermer...'
read -r x
