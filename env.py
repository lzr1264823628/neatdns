import json
import os
import socket

import requests
from environs import Env

env = Env()
env.read_env()

TMP_FOLDER = env.str("TMP_FOLDER", "/tmp/neatdns_new")
POISONING_DOMAINS_LIST = env.str("POISONING_DOMAINS_LIST", "domain_list_poisoning.json")
BIND_QUEEY_LOG_PATH = env.str("BIND_QUEEY_LOG_PATH", "/tmp/named/query.log")
BIND_RESOLVE_LOG_PATH = env.str("BIND_RESOLVE_LOG_PATH", "/tmp/named/resolver.log")
ALEXA_LOCAL = env.bool("ALEXA_LOCAL", False)
ADD_NTA = env.bool("ADD_NTA", True)

if ALEXA_LOCAL:
    ALEXA_TOP_1M_URL = 'http://127.0.0.1:8000/top-1m.csv.zip'
else:
    ALEXA_TOP_1M_URL = 'https://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

TLD_LIST_PATH = os.path.join(TMP_FOLDER, 'tld_list.json')

if not os.path.exists(TMP_FOLDER):
    os.mkdir(TMP_FOLDER, 0o700)

if not os.path.exists(POISONING_DOMAINS_LIST):
    with open(POISONING_DOMAINS_LIST, 'w') as f:
        f.write('[]')

if os.path.exists(TLD_LIST_PATH):
    with open(TLD_LIST_PATH, 'r') as f:
        TLD_LIST = json.load(f)
else:
    resp = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt', timeout=5)
    lines = resp.text.splitlines()
    lines.pop(0)
    TLD_LIST = [x.lower() for x in lines]
    with open(TLD_LIST_PATH, 'w') as f:
        json.dump(TLD_LIST, f)

nameserver_config = 'nameserver %s\n' % socket.gethostbyname('example.com')
RESOLVE_CONF_FNAME = os.path.join(TMP_FOLDER, 'resolv.conf')
with open(RESOLVE_CONF_FNAME, 'w') as f:
    f.write(nameserver_config)
