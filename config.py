#!/usr/bin/env python
# coding:utf-8
# Build By LandGrey
#

import os
import sys
import platform


def ver_egt_3():
    if int(platform.python_version()[0]) == 3:
        return True
    else:
        return False


def is_64bit():
    if len(platform.architecture()) == 2 and platform.architecture()[0] == '64bit':
        return True
    else:
        return False


# Script Root path
root_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0]))).encode('utf-8').decode() if ver_egt_3 else \
    os.path.dirname(os.path.abspath(sys.argv[0])).decode('utf-8')

# SSLScan tool path
if 'Windows' in platform.system():
    sslscan_path = os.path.join(root_path, 'sslscan', 'sslscan.exe')
else:
    sslscan_path = "/usr/local/bin/sslscan"

# CURL tool path
if 'Windows' in platform.system():
    if is_64bit():
        curl_path = os.path.join(root_path, 'curl/AMD64', 'curl.exe')
    else:
        curl_path = os.path.join(root_path, 'curl/I386', 'curl.exe')
else:
    curl_path = "/usr/bin/curl"

# hit waf keyword
enable_waf_keyword = False
hit_waf_regex = "<!-- event_id: (.*?) -->"

# CURL check target alive command
# alive_command = '{} --connect-timeout 5 ' \
#                 '-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0" -L '.format(curl_path)

alive_command = [
    curl_path,
    '--connect-timeout', '5',
    '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0',
    '-L'
]

# CURL request Command
# curl_command = '{} --connect-timeout 6 --retry 2 --location --max-redirs 3 --max-time 5 --no-keepalive ' \
#                   '-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0" '.format(curl_path)

curl_command = [
    curl_path,
    '--connect-timeout', '6',
    '--retry', '2',
    '--location',
    '--max-redirs', '3',
    '--max-time', '5',
    '--no-keepalive',
    '-A', '"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0"'
]


# SSL/TLS Accepted Cipher Test Command
# ciphers_command = "{} --no-colour --no-heartbleed --show-ciphers --sleep 500 --timeout=45 ".format(sslscan_path)
ciphers_command = [
    sslscan_path,
    '--no-colour',
    '--no-heartbleed',
    '--show-ciphers',
    '--sleep', '500',
    '--timeout', '45'
]

# common request param
normal_request = "/?Lid=1008610086"

# waf test param compared common request
payload_request = "/?Lid=1%27or%271%27=%271..%2F..%2F..%2Fetc%2Fpasswd"
