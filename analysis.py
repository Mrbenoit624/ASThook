import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import argparse
import threading
import time
from ppadb.client import Client as AdbClient
import signal
from contextlib import contextmanager
import pyjadx



CONST_ANDROID = "{http://schemas.android.com/apk/res/android}"
package=""
DIR="temp"

def bprint(text):
    size = int(len(text)/2)
    print()
    print("#" * 80)
    print("%s%s" % (" " * (40 - size), text))
    print("#" * 80, end='\n\n')


@contextmanager
def timeout(time):
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError



################################################################################
#
# Static Analysis
#
################################################################################

def Manifest():
    global package
    tree = ET.parse('%s/%s/AndroidManifest.xml' % (DIR, "decompiled_app"))
    root = tree.getroot()
    print(root.get('package'))
    package = root.get('package')
    bprint("Permission")
    for permissions in root.findall('uses-permission'):
        #print(permissions.attrib[0])
        name = permissions.get('%sname' % CONST_ANDROID)
        print(name)
    bprint("Dangerous fonctionnality")
    #print(root.find('application').attrib)

    # AllowBacup Functionality
    if not root.find('application').get("%sallowBackup" % CONST_ANDROID) == 'false':
        print("allowBackup: allow to backup all sensitive function on the \
cloud or on a pc")
    
    # debuggable Functionality
    if root.find('application').get("%sdebuggable" % CONST_ANDROID) == 'true':
        print("debuggable: allow to debug the application in user mode")

def UserInput(app):
   jadx = pyjadx.Jadx()
   app = jadx.load(app)

   for cls in app.classes:
     #print(cls.name)
     code = cls.code.split('\n')
     print(cls.name)
     for i in range(len(code)):
         if "getString(" in code[i]:
            print("l%d: %s" % (i, code[i]))

def static(app):
    bprint("Static Analysis")
    subprocess.call(["apktool", "d", app, "-o", "%s/decompiled_app" % DIR, "-f"],
            stdout=subprocess.DEVNULL, shell=False)
    Manifest()
    UserInput(app)
    subprocess.call(["rm", "-rf", "%s/decompiled_app" % DIR], shell=False)

################################################################################
#
# Dynamic Analysis
#
################################################################################

def emulation_f(path, phone, proxy):
    options = ["%s/emulator" % path, "@%s" % phone, "-selinux",
    "disabled", "-memory", "3192", "-no-boot-anim", "-no-snapshot", "-tcpdump",
    "%s/dumpfile.pcap" % DIR, "-wipe-data", "-writable-system"]
    if not proxy == "":
        options.extend(["-http-proxy", proxy])
    print(options)
    subprocess.call(options, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_user_share(device):
    files = device.shell("ls /data/data/%s/shared_prefs/" % package)
    print(files)
    os.mkdir("%s/user_share" % DIR)
    for f in files.split("\n"):
        f = f.replace('\r', '')
        if not f == "":
            device.pull("/data/data/%s/shared_prefs/%s" % (package, f),
                    "%s/user_share/%s" % (DIR, f))

def dynamic(args):
    bprint("Dinamic analysis")
    if args.emulator:
        emulation = threading.Thread(target=emulation_f, args=(args.emulator,
            args.phone, args.proxy))
        emulation.daemon = True
        emulation.start()
    client = AdbClient(host="127.0.0.1", port=5037)
    print("waiting for connection device...")
    devices = []
    try:
        with timeout(30):
            while devices == []:
                devices = client.devices()
            device = devices[0]
    except:
        print("No devices found after 30s")
        sys.exit(1)
    while True:
        try:
            device.install(args.app)
            break
        except:
            continue
    # setup certificate
    if args.proxy_cert:
        os.system("openssl x509 -inform DER -in %s -out %s/cacert.pem" %
                (args.proxy_cert, DIR))
        hash_cert = subprocess.check_output(["openssl", "x509", "-inform",
            "PEM", "-subject_hash_old", "-in", "%s/cacert.pem" % DIR])
        hash_cert = hash_cert.decode().split('\n')[0]
        print(hash_cert)
        os.system("mv %s/cacert.pem %s/%s.0" % (DIR, DIR, hash_cert))
        device.shell("mount -o rw,remount,rw /system")
        device.push("%s/%s.0" % (DIR, hash_cert),
                "/system/etc/security/cacerts/%s" % hash_cert)
        device.shell("chmod 644 /system/etc/security/cacerts/%s.0" % hash_cert)
        device.shell("mount -o ro,remount,ro /system")
    #apps = device.shell("pm list packages -f")
    print(package)
    device.shell("monkey -p %s -c android.intent.category.LAUNCHER 1" % package)
    time.sleep(1)
    get_user_share(device)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Analysis for smartphone')
    
    parser.add_argument(
        'app',
        type=str,
        help='app target <filename.apk>')
    
    
    group = parser.add_argument_group('dynamic')
    
    group.add_argument(
        '--emulator',
        type=str,
        help='path of the emulator if used')
    
    group.add_argument(
        '--phone',
        type=str,
        help='phones target emulator -list-avds')
    
    group.add_argument(
        '--proxy',
        type=str,
        help='setup proxy address <ip>:<port>')
    
    group.add_argument(
        '--proxy_cert',
        type=str,
        help='setup proxy address <filename>.cer')
    
    args = parser.parse_args()
    
    os.mkdir("temp")
    static(args.app)
#    dynamic(args)
