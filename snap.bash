#!/bin/bash

cd /home/le127/Arbalet/arbapps
python -m arbalet.tools.snap -w &
cd /home/le127/Arbalet/Snap--Build-Your-Own-Blocks
gksudo "python -m SimpleHTTPServer 80" &
firefox localhost:33450/admin
sleep 10
notify "Arbalet 127" "Snap est prêt sur l'adresse 172.17.9.199"
echo ""
echo "Snap est prêt sur l'adresse 172.17.9.199"

