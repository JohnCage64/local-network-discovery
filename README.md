# local-network-discovery

very simple python script for discovery host in local network. It use ping but can be changed to fping for very very fast output in such case fping binary is needed. 

Features:



Usage:
---
./ld.py | Chack all local subnets (take ip from ifconfig without localhost)  
./ld.py -i eth0  | Chack all live machines on eth0 ip subnet  
./ld.py -d |  Output id pyton list format (for all subnets avialiable without localhost)  
./ld.py -i eth0 -d |  Output id pyton list format all live machines on eth0 ip subnets  
./ld.py -l | list all avialiable ifce  
./ld.py -o file_name | save all live ip (for all subnets avialiable without localhost) to file (one line one ip)
./ld.py -i eth0 -o file_name | save all live ip on eth0 ip subnet to file (one line one ip)
