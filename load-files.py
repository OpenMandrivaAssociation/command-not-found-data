#!/usr/bin/python

from misc import execute_command
import urllib2
import shutil
import lzma
from lxml import etree
import os
import re
import sys

def fetch_file(url, path):
    response = urllib2.urlopen(url)
    fd = open(path, 'wb')
    shutil.copyfileobj(response, fd)
    fd.close()

if len(sys.argv) < 2:
    print 'usage: load-files.py platfrom_name'
    exit(1)
platform = sys.argv[1]
repos = ['main', 'contrib', 'restricted', 'non-free']
subrepos = ['release', 'updates']
url_template = 'http://abf.rosalinux.ru/downloads/%s/repository/x86_64/%s/%s'
urls = {}
for repo in repos:
    for subrepo in subrepos:
        url = url_template % (platform, repo, subrepo)
        urls[url] = repo

re_bin = re.compile('((/usr/bin/)|(/bin/)|(/usr/local/bin)|(/sbin)|(/usr/sbin)|(/usr/local/sbin)|(/usr/games)).+')
binaries = {}
for url in urls:
    files_url = url + '/media_info/files.xml.lzma'
    print files_url
    repo = urls[url]
    try:
        fetch_file(files_url, '/tmp/files.xml.lzma')
    except urllib2.URLError, ex:
        print str(ex)
        continue
    fd = lzma.LZMAFile('/tmp/files.xml.lzma', 'b')
    tree = etree.XML(fd.read())
    fd.close()
    files = tree.xpath('/media_info/files')
    for f in files:
        pkg = dict(f.items())['fn']
        pkg_name = '-'.join(pkg.split('-')[:-3])
        items = [x for x in f.text.split('\n') if re_bin.match(x)]
        for bin_name in items:
            bin_name = os.path.basename(bin_name)
            if bin_name not in binaries:
                binaries[bin_name] = []
            binaries[bin_name].append((repo, pkg_name))
    
    os.remove('/tmp/files.xml.lzma')

print len(binaries)
import json
with open('data.json', 'w') as fd:
    json.dump(binaries, fd)

    
    
    
    
    
    
    
    
    