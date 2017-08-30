#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import gzip
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import urllib2

from StringIO import StringIO

class BuildDownloader(object):
    def __init__(self, url):
        super(BuildDownloader, self).__init__()
        self.url = url

    def __del__(self):
        self.reset()

    def requestDownload(self, url):
        request = urllib2.Request(self.url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)

        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            return gzip.GzipFile(fileobj=buf)

        return response

    def fetch(self):
        req = self.requestDownload(self.url)

        fd, path = tempfile.mkstemp(prefix='moz')
        filesize = 0

        with os.fdopen(fd, 'w', 65536) as f:
            while True:
                buf = req.read(65536)
                if not buf: break;

                filesize += len(buf)

                f.write(buf)
                print 'downloading: %d bytes\r' % filesize,
        print ''

        self.path = path
        self.filesize = filesize
        return True

    def check(self):
        return True

    def save(self, path):
        shutil.move(self.path, path)

    def reset(self):
        if os.path.exists(self.path):
            os.remove(self.path)

class TryBuildDownloader(BuildDownloader):
    CONFIG = {
        'protocol': 'https',
        'host': 'archive.mozilla.org',
        'path': '/pub/firefox/try-builds/%(build_id)s/try-%(platform)s',
    }

    def __init__(self, platform, build_id):
        super(TryBuildDownloader, self).__init__('')

        self.config = self.CONFIG.copy()

        self.config['platform'] = platform
        self.config['build_id'] = build_id
        self.config['path'] = self.config['path'] % (self.config)
        self.config['lang'] = 'en-US'
        self.config['version'] = self._check_version()
        self.config['installer'] = 'firefox-%(version)s.%(lang)s.%(platform)s.installer.exe' % (self.config)

        self.checksums = {}
        self.digests = {}
        self.path = ''
        self.filesize = 0

    def _check_version(self):
        url = '%(protocol)s://%(host)s%(path)s/' % (self.config)
        req = urllib2.urlopen(url)
        for line in req.read().split('\n'):
            pat = 'firefox-(\d+.\w+).%(lang)s.%(platform)s.installer.exe' % self.config
            m = re.search(pat, line)
            if m:
                return m.group(1)
        return None

    def _prepare_checksums(self):
        url = '%(protocol)s://%(host)s%(path)s/firefox-%(version)s.%(lang)s.%(platform)s.checksums' % (self.config)
        req = urllib2.urlopen(url)

        checksums = {}
        for line in req.read().split('\r\n'):
            if not line: continue

            checksum, name, size, filename = line.split()
            checksum = checksum.lower()
            name = name.lower()
            size = int(size, 10)
            filename = filename.split('/')[-1]

            if filename != self.config['installer']: continue
            checksums[name] = {
                'checksum': checksum.lower(),
                'size': int(size),
            }
        self.checksums = checksums

    def fetch(self):
        self._prepare_checksums()

        self.url = '%(protocol)s://%(host)s%(path)s/%(installer)s' % (self.config)
        req = self.requestDownload(self.url)

        fd, path = tempfile.mkstemp(prefix='moz')
        filesize = 0
        hashes = dict((m, hashlib.new(m)) for m in self.checksums)

        with os.fdopen(fd, 'w', 65536) as f:
            while True:
                buf = req.read(65536)
                if not buf: break;

                filesize += len(buf)
                for m in hashes.itervalues():
                    m.update(buf)

                f.write(buf)
                print 'downloading: %d bytes\r' % filesize,
        print ''

        for k, v in hashes.iteritems():
            self.digests[k] = v.hexdigest().lower()

        self.path = path
        self.filesize = filesize
        return True

    def check(self):
        for k, v in self.digests.iteritems():
            if self.checksums[k]['checksum'] != v:
                print 'checksum %s mismatch' % k
                return False
            if self.checksums[k]['size'] != self.filesize:
                print 'size %s mismatch' % k
                return False
        return True

    def save(self, path):
        super(TryBuildDownloader, self).save(path)

        base, ext = os.path.splitext(path)
        with open(base + '.checksum', 'w') as f:
            json.dump(self.digests, f, indent=2)
            f.write('\n')

