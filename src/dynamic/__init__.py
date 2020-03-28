
import subprocess
import threading
import time
import sys

from myadb import my_adb as AdbClient
from ppadb import ClearError, InstallError


from utils import timeout, bprint
from log import Log
from dynamic.frida import Frida

################################################################################
#
# Dynamic Analysis
#
################################################################################

class DynamicAnalysis:

    @staticmethod
    def emulation_f(path, phone, proxy, tmp_dir):
        options = ["%s/emulator/emulator" % path, "@%s" % phone, "-selinux",
                "disabled", "-memory", "3192", "-no-boot-anim", "-no-snapshot", "-tcpdump",
                "%s/dumpfile.pcap" % tmp_dir, "-wipe-data", "-writable-system"]
        if not proxy == None:
            options.extend(["-http-proxy", proxy])
        print(options)
        subprocess.call(options, stdout=Log.STD_OUTPOUT, stderr=Log.STD_ERR)
    
    def get_user_share(self):
        if "False" in self.__device.shell("([ -d /data/data/%s/shared_prefs/ ] && echo 'True') || echo 'False'" % self.__package):
            print("No shared preference")
            return
        test = self.__device.shell("([ -d /data/data/%s/shared_prefs/ ] && echo 'True') || echo 'False'" % self.__package)
        print(test)
        files = self.__device.shell("ls /data/data/%s/shared_prefs/" % self.__package)
        print(files)
        os.mkdir("%s/user_share" % self.__tmp_dir)
        for f in files.split("\n"):
            f = f.replace('\r', '')
            if not f == "":
                self.__device.pull("/data/data/%s/shared_prefs/%s" % (self.__package, f),
                        "%s/user_share/%s" % (self.tmp_dir, f))
    
    def setup_certificate(self, proxy_cert):
        os.system("openssl x509 -inform DER -in %s -out %s/cacert.pem" %
                (proxy_cert, self.__tmp_dir))
        hash_cert = subprocess.check_output(["openssl", "x509", "-inform",
            "PEM", "-subject_hash_old", "-in", "%s/cacert.pem" %
            self.__tmp_dir])
        hash_cert = hash_cert.decode().split('\n')[0]
        print(hash_cert)
        os.system("mv %s/cacert.pem %s/%s.0" %
                (self.__tmp_dir,
                 self.__tmp_dir,
                 hash_cert))
        self.__device.shell("mount -o rw,remount,rw /system")
        self.__device.push("%s/%s.0" % (self.__tmp_dir, hash_cert),
                "/system/etc/security/cacerts/%s" % hash_cert)
        self.__device.shell("chmod 644 /system/etc/security/cacerts/%s.0" % hash_cert)
        self.__device.shell("mount -o ro,remount,ro /system")
    
    def generalinfo(self):
        self.__frida.load("script_frida/generalinfo.js", "store")
        infos = self.__frida.get_store()
        print ("\033[36mFile Directory :\033[39m \t\t%s" % infos['filesDirectory'])
        print ("\033[36mCache Directory :\033[39m \t\t%s" % infos['cacheDirectory'])
        print ("\033[36mExternal Cache Directory :\033[39m \t%s" % infos['externalCacheDirectory'])
        print ("\033[36mCode Cache Directory :\033[39m \t\t%s" % infos['codeCacheDirectory'])
        print ("\033[36mObb Directory :\033[39m \t\t%s" % infos['obbDir'])
        print ("\033[36mPackage Code path :\033[39m \t\t%s" % infos['packageCodePath'])



    def __init__(self, package, args, tmp_dir):

        self.__package = package
        self.__tmp_dir = tmp_dir
        self.__args = args
        self.__emulation = None
        self.__client = AdbClient(host="127.0.0.1", port=5037)
        self.__device = None


        bprint("Dynamic analysis")
        subprocess.call(["adb", "start-server"])
        if args.emulator:
            self.__emulation = threading.Thread(target=self.emulation_f,
                    args=(args.emulator, 
                          args.phone,
                          args.proxy,
                          self.__tmp_dir))
            self.__emulation.daemon = True
            self.__emulation.start()
        
        print("waiting for connection device...")
        devices = []
        try:
            with timeout(45):
                while devices == []:
                    devices = self.__client.devices()
                    time.sleep(1)
                self.__device = devices[0]
        except:
            print("No devices found after 30s")
            sys.exit(1)
        if self.__device == None:
            sys.exit(1)
        while True:
            try:
                self.__device.install(args.app)
                break
            except RuntimeError:
                continue
            except InstallError as e:
                if "Is the system running" in str(e):
                    continue
                elif "[INSTALL_FAILED_TEST_ONLY]" in str(e):
                    print("becareful install as test")
                    subprocess.call(['adb', 'install', '-t', args.app],
                            stdout=Log.STD_OUTPOUT, stderr=Log.STD_ERR, shell=False)
                    break
                else:
                    print(str(e))
        # setup certificate
        if args.proxy_cert:
            self.setup_certificate(args.proxy_cert)
        #apps = device.shell("pm list packages -f")
        self.__frida = Frida(self.__device, self.__package)
        print(self.__package)
        self.__device.shell("monkey -p %s -c android.intent.category.LAUNCHER 1" % self.__package)
        time.sleep(1)
        self.__frida.attach()
        self.generalinfo()
        self.__frida.load("script_frida/sslpinning.js", "print")
        self.__frida.load("script_frida/hookfile2.js", "print")
        #self.__frida.load("script_frida/hookfile.js", "print")
        sys.stdin.read()
        self.__frida.detach()
        self.get_user_share()
    
    
