import dns.resolver
import _socket
import socket
import os
import re
import traceback
import sys

DEBUG = False
ROOTPATH = os.path.dirname(os.path.realpath(__file__))
EGGPATH = os.path.join(ROOTPATH, "eggs")
PLUGINPATH = os.path.join(ROOTPATH, "data", "plugins")

def printd(*args):
    if DEBUG:
        print(*args)

# make plugins importable
sys.path.append(PLUGINPATH)

# import the eggs, for some reason they dont work with pythonpath
for p in os.listdir(EGGPATH):
    if p.endswith(".egg"):
        sys.path.append(os.path.join(EGGPATH, p))

# monkey patch socket and dns mechanism which was meant for android
DNSSERVERS=["8.8.8.8"]
RESOLVER = dns.resolver.Resolver()
RESOLVER.nameservers=DNSSERVERS

def isipv4(adr):
    s = re.search(r"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", adr)
    return s and s.group(1) == adr


def gethostbyname(name=''):
    if isipv4(name):
        return name
    try:
        answer = RESOLVER.resolve(name)
    except dns.resolver.NXDOMAIN:
        printd("Cant't resolve %s" % name)
        return
    host=answer[0].address
    printd("Resolved %s to %s" % (name, host))
    return host

def getipnodebyname(name, *args, **kwargs):
    return gethostbyname(name)

def getaddrinfo(name, *args, **kwargs):
    return _socket.getaddrinfo(gethostbyname(name=name), *args, **kwargs)

_socket.gethostbyname = gethostbyname
_socket.getipnodebyname = getipnodebyname
socket.gethostbyname = gethostbyname
socket.getipnodebyname = getipnodebyname
socket.getaddrinfo = getaddrinfo

# spoof taskmanager so that annoying 5min timout video playback stop can be bypassed
from ACEStream.Utilities import TimedTaskQueue

SKIPTASKS = ["remove_playing_download_wrapper"]

def faketask(*args, **kwargs):
    return

class NewTimedTaskQueue(TimedTaskQueue.TimedTaskQueue):
    def add_task(self, *args, **kwargs):
        printd("task added", args, kwargs)
        if len(args) and hasattr(args[0], "__name__") and args[0].__name__ in SKIPTASKS:
            printd("task skipped", args, kwargs)
            args = list(args)
            args[0] = faketask
        super().add_task(*args, **kwargs)

TimedTaskQueue.TimedTaskQueue = NewTimedTaskQueue

# monkey patch app_bridge to spoof fake android behaviour
import app_bridge

class Android:
  def getAceStreamHome(self, *args, **kwargs):
    return os.path.abspath(os.path.dirname(sys.argv[0]))

  def getDisplayLanguage(self, *args, **kwargs):
    return 'en'

  def getRAMSize(self, *args, **kwargs):
    return 1024 * 1024 * 1024

  def getMaxMemory(self, *args, **kwargs):
    return 1024 * 1024 * 1024

  def getDeviceId(self, *args, **kwargs):
    return 'd3efefe5-4ce4-345b-adb6-adfa3ba92eab'

  def getAppId(self, *args, **kwargs):
    return 'd3efefe5-4ce4-345b-adb6-adfa3ba92eab'

  def getDeviceManufacturer(self, *args, **kwargs):
    return 'Samsung'

  def getDeviceModel(self, *args, **kwargs):
    return 'Galaxy S3'

  def onSettingsUpdated(self, *args, **kwargs):
    return

  def onEvent(self, *args, **kwargs):
    return

  def getAppVersionCode(self, *args, **kwargs):
    return "6.6"

  def getArch(self, *args, **kwargs):
    return "armv7h"

  def getLocale(self, *args, **kwargs):
    return "en-US"

  def isAndroidTv(self, *args, **kwargs):
    return False

  def hasBrowser(self, *args, **kwargs):
    return False

  def hasWebView(self, *args, **kwargs):
    return False

  def getMemoryClass(self, *args, **kwargs):
    return

  def getAvailableBlocks(self):
      return 0

  def startInternalActivity(self, *args, **kwargs):
      return

  def _fake_rpc(self, method, *args):
    if hasattr(Android, method):
      return getattr(Android, method)(self, *args)
    print("Unknown RPC:", method, *args)
    raise Exception("Unknown method: %s" % (method,))


for k, v in vars(Android).items():
    if k.startswith("__"):
        continue
    setattr(app_bridge.Android, k, v)

# import actual acestream core function

import sys
from acestreamengine import Core
Core.run(sys.argv)
