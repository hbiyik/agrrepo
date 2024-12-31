import dns.resolver
import _socket
import socket
import os
import re

# monkey patch socket
DNSSERVERS=["8.8.8.8"]
RESOLVER = dns.resolver.Resolver()
RESOLVER.nameservers=DNSSERVERS
DEBUG=0


def isipv4(adr):
    s = re.search(r"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", adr)
    return s and s.group(1) == adr


def gethostbyname(name=''):
    if isipv4(name):
        return name
    try:
        answer = RESOLVER.resolve(name)
    except dns.resolver.NXDOMAIN:
        if DEBUG:
            print("Cant't resolve %s" % name)
        return
    host=answer[0].address
    if DEBUG:
        print("Resolved %s to %s" % (name, host))
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

# monkey patch app_bridge
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

  def _fake_rpc(self, method, *args):
    if hasattr(Android, method):
      return getattr(Android, method)(self, *args)
    raise Exception("Unknown method: %s" % (method,))


for k, v in vars(Android).items():
    if k.startswith("__"):
        continue
    setattr(app_bridge.Android, k, v)

import sys
from acestreamengine import Core
Core.run(sys.argv)