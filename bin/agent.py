import datetime
import json
import os
import urllib

from wpt import *

AGENT_SERVER = 'http://moz.xeon.tw:3000/api/builds'

class Config(object):
  def __init__(self, path):
    super(Config, self).__init__()
    self.path = path
    self.config = {
      'timestamp': 0
    }

    if os.path.exists(self.path):
      with open(self.path, 'r') as f:
        self.config.update(json.load(f))

  def __del__(self):
    with open(self.path, 'w') as f:
      json.dump(self.config, f)

class Agent(Config):
  def __init__(self):
    super(Agent, self).__init__('agent.dat')

  def get_builds(self):
    f = urllib.urlopen(AGENT_SERVER)
    try:
      return filter(lambda b: b.get('created_at', 0) > self.config['timestamp'], json.load(f))
    finally:
      f.close()

  def update_timestamp(self, timestamp):
    self.config['timestamp'] = timestamp

def main():
  agent = Agent()

  for b in agent.get_builds():
    build_id = b['id']
    if download(build_id) and install(build_id):
      update()
      agent.update_timestamp(b['created_at'])

if __name__ == '__main__':
  main()