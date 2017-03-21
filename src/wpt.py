#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import os
import sys

from downloader import TryBuildDownloader

__all__ = ['download', 'install', 'update']

INSTALLER_DIR =   'C:\\CDP\\installer'
WPT_DRIVER_BASE = 'C:\\CDP\\etc\\wptdriver.ini'
WPT_DRIVER_INI =  'C:\\webpagetest\\wptdriver.ini'
PLATFORM = 'win32'

INSTALL_INI = '''[Install]
InstallDirectoryPath=C:\\CDP\\Try-%(build_id)s\\
QuickLaunchShortcut=false
DesktopShortcut=false
StartMenuShortcuts=false
MaintenanceService=false
'''

WPT_INI = '''[Try-%(build_id_no_dot)s]
exe="C:\\CDP\\Try-%(build_id)s\\firefox.exe"
options='-profile "%%PROFILE%%" -no-remote'
template=firefox
'''

def download(build_id):
  base = os.path.join(INSTALLER_DIR, 'try-%s' % build_id)

  installer_path = '%s.%s' % (base, 'exe')
  if not os.path.exists(installer_path):
    d = TryBuildDownloader(PLATFORM, build_id)
    if d.fetch() and d.check():
        d.save(installer_path)
        print 'success'
    else:
        d.reset()
        print 'failed'
        return False

    config = {
      'build_id': build_id,
      'build_id_no_dot': build_id.replace('.', '_')
    }
    with open(base + '.ini', 'w') as f:
        f.write(INSTALL_INI % config)

    with open(base + '.wpt', 'w') as f:
        f.write(WPT_INI % config)

  return True

def install(build_id):
  base = os.path.join(INSTALLER_DIR, 'try-%s' % build_id)
  return os.system('%s.exe /INI=%s.ini' % (base, base)) == 0

def get_file_list():
  files = filter(lambda f: f.endswith('.wpt'), os.listdir(INSTALLER_DIR))
  paths = map(lambda f: os.path.join(INSTALLER_DIR, f), files)
  return [WPT_DRIVER_BASE] + paths

def read_ini_content():
  for ini in get_file_list():
    with open(ini, 'r') as f:
      yield f.read()

def update():
  with open(WPT_DRIVER_INI, 'w') as f:
    for c in read_ini_content():
      f.write(c + '\r\n')

def main(arg):
  build_id = arg

  if download(build_id) and install(build_id):
    update()

if __name__ == '__main__':
    main(sys.argv[1])
