#!/usr/bin/python3
import argparse, socket, multiprocessing, os, subprocess
import socket, array, struct, fcntl


###VARIAVLES and STUFF

red = lambda text: '\033[0;31m' + text + '\033[0m'
green = lambda text: '\033[0;32m' + text + '\033[0m'
magenta = lambda text: '\033[0;35m' + text + '\033[0m'
cyan = lambda text: '\033[0;36m' + text + '\033[0m'



##########################
##########################
def get_local_interfaces():
    MAX_BYTES = 4096
    FILL_CHAR = b'\0'
    SIOCGIFCONF = 0x8912
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', MAX_BYTES * FILL_CHAR)
    names_address, names_length = names.buffer_info()
    mutable_byte_buffer = struct.pack('iL', MAX_BYTES, names_address)
    mutated_byte_buffer = fcntl.ioctl(sock.fileno(), SIOCGIFCONF, mutable_byte_buffer)
    max_bytes_out, names_address_out = struct.unpack('iL', mutated_byte_buffer)
    namestr = names.tobytes()
    namestr[:max_bytes_out]
    bytes_out = namestr[:max_bytes_out]

    ip_dict = {}
    for i in range(0, max_bytes_out, 40):
        name = namestr[ i: i+16 ].split(FILL_CHAR, 1)[0]
        name = name.decode('utf-8')
        ip_bytes   = namestr[i+20:i+24]
        full_addr = []
        for netaddr in ip_bytes:
            if isinstance(netaddr, int):
                full_addr.append(str(netaddr))
            elif isinstance(netaddr, str):
                full_addr.append(str(ord(netaddr)))
        ip_dict[name] = '.'.join(full_addr)

    return ip_dict
def get_local(switch):
    local = get_local_interfaces()
    return local[switch]
def pinger(job_q, results_q):
    DEVNULL = open(os.devnull, 'w')
    while True:
        ip = job_q.get()
        if ip is None:
            break
        try:
            #subprocess.check_call(['fping', '-c1',"-t200", ip],stdout=DEVNULL,stderr=DEVNULL)
            subprocess.check_call(['ping', '-c1',"-t1", ip],
                                  stdout=DEVNULL,
                                  stderr=DEVNULL)
            results_q.put(ip)
        except:
            pass
def map_network(ip,pool_size=255):
    ip_list = list()
    ip_parts = ip.split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()
    pool = [multiprocessing.Process(target=pinger, args=(jobs, results)) for i in range(pool_size)]
    for p in pool:
        p.start()
    for i in range(1, 255):
        jobs.put(base_ip + '{0}'.format(i))
    for p in pool:
        jobs.put(None)
    for p in pool:
        p.join()
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)
    #HASH BELOW FOR THIS (iface address) COMPUTER IN RESULTS
    ip_list.remove(ip)
    return ip_list

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='local_dicscover',description='Lets find out who beside us is up in here, right?', epilog='Have fun!')
    parser.add_argument("-i",type=str, help='ld.py -i eth0  | That\s will chek what machines answer ping on eth0 subnet')
    parser.add_argument("-l", action='store_true',help='ld.py -l  | Will list all ifce and list it with name:ip')
    parser.add_argument("-o",type=str, help='ld.py -o file_name |  all ips are save in file_name, one line one ip')
    parser.add_argument("-d", action='store_true', help='ld.py -d  | output python dict')

    args = parser.parse_args()
    local = get_local_interfaces()

    ### Without args  [OK]
    if not args.i and not args.l and not args.o and not args.d:
        for sub in local:
            if not (local[sub]=="127.0.0.1"):
                subnet = (local[sub]).split('.')
                subnet = subnet[0]+'.'+subnet[1]+'.'+subnet[2]+'.0'
                print(f'{green(local[sub])} -> {cyan(subnet)}')
                lst = map_network(local[sub])
                for ip in lst:
                    UP = 'UP'
                    print (f'{green(UP)}: {cyan(ip)}')
                    
                    
    ### -o file_name    [OK]
    if args.o and not args.l and not args.i and not args.d:
#        print("-o")
        ip_file = (str(args.o)+'.txt')
        f=open(ip_file, "w")

        for sub in local:
            if not (local[sub]=="127.0.0.1"):
                c=0
                for x in local:
                    if (x !='lo'):
                        zapis = (str(x))+':'+(str(map_network(local[x])))
                        f.write(zapis+'\n')
                        
        f.close()
        print (green('DONE'))

    ### -i etho o file_name  [OK]
    if args.i and args.o and not args.d and not args.l:
 #       print ("-i -o")
        try:
            ip = (local[args.i])
            ip_file = (str(args.o)+'.txt')
            subnet = (ip.split('.'))
            subnet = subnet[0]+'.'+subnet[1]+'.'+subnet[2]+'.0'
            print (f'Saving to {cyan(ip_file)} hosts that replying echo on {green(subnet)} via [{cyan(args.i)} -> {green(ip)}]')                     
            lst = map_network(ip)
            f=open(ip_file, "w")
            for host in lst:
                host=(host+'\r\n')
                f.write(host)        
            f.close()
            print (green('DONE'))
        except KeyError:
            print(red('Wrong interface'))
            for sub in local:
                print(cyan('Avialiable'),':',f'{green(sub)}')
     

    ### -i eth0 -d   [OK]   
    if args.i and args.d and not args.l and not args.o:
  #      print('-i -d')
        try:
            ip = (local[args.i])
            subnet = (ip.split('.'))
            subnet = subnet[0]+'.'+subnet[1]+'.'+subnet[2]+'.0'
            print (f'Checking hosts that replying echo on {green(subnet)} via [{cyan(args.i)} -> {green(ip)}]')      
            lst = map_network(ip)
            print(f'{green(args.i)}: {lst}')
        except KeyError:
            print(red('Wrong interface'))
            for sub in local:
                print(cyan('Avialiable'),':',f'{green(sub)}')
    ### -i eth0   [OK]    
    if args.i and not args.o and not args.l and not args.d:
   #     print ("-i")
        try:
            ip = (local[args.i])
            subnet = (ip.split('.'))
            subnet = subnet[0]+'.'+subnet[1]+'.'+subnet[2]+'.0'
            print (f'Checking hosts that replying echo on {green(subnet)} via [{cyan(args.i)} -> {green(ip)}]')      
            lst = map_network(ip)
            for host in lst:
                print (green('UP'),':',f'{cyan(host)}')
        except KeyError:
            print(red('Wrong interface'))
            for sub in local:
                print(cyan('Avialiable'),':',f'{green(sub)}')
                
    ### -l  [OK]
    if args.l and not args.o and not args.i and not args.d:
    #    print('-l')
        switch = True
        for x in local:
            if switch:
                print(f'{green(x)}: {cyan(local[x])}]')
                switch=False
            elif not switch:
                print(f'{magenta(x)}: {cyan(local[x])}')
                switch=True
    ###  -d  [OK]                             
    if not args.i and args.d and not args.l and not args.o:
    #    print('-d')
        switch = True
        for x in local:
            if (x !='lo'):
                if switch:
                    print(green(x),':',map_network(local[x]))
                    switch = False
                elif not switch:
                    print(cyan(x),':',map_network(local[x]))
                    switch = True