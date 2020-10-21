
import subprocess
import threading
import log as logging
import time
import sys
import os

from myadb import my_adb as AdbClient
from ppadb import ClearError, InstallError

from git import Repo
import shutil

from utils import timeout, bprint, extcall
from log import Log
from dynamic.frida import Frida

from dynamic.module import ModuleDynamic

from .cmd import DynCmd


################################################################################
#
# Dynamic Analysis
#
################################################################################

class DynamicAnalysis:
    """
    Class to manage all dynamic analysis
    """

    @staticmethod
    def emulation_f(path, phone, proxy, tmp_dir, no_erase):
        """
        Launch the emulator
        """
        options = ["%s/emulator/emulator" % path, "@%s" % phone, "-selinux",
                "disabled", "-memory", "3192", "-no-boot-anim", "-no-snapshot", "-tcpdump",
                "%s/dumpfile.pcap" % tmp_dir, "-writable-system"]
        #options = ["%s/emulator/emulator" % path, "@%s" % phone,
        #        "-no-snapshot", "-tcpdump",
        #        "%s/dumpfile.pcap" % tmp_dir, "-writable-system"]
        if not proxy == None:
            options.extend(["-http-proxy", proxy])
        if not no_erase:
            options.extend(["-wipe-data"])
        logging.info(" ".join(options))
        #subprocess.call(options, stdout=Log.STD_OUTPOUT, stderr=Log.STD_ERR)
        extcall.external_call(options)

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
        """
        Install a certificate on the mobile
        """
        if not os.path.exists(proxy_cert):
            logging.error("%s file not found" % proxy_cert)
            sys.exit(1)
        os.system("openssl x509 -inform DER -in %s -out %s/cacert.pem" %
                (proxy_cert, self.__tmp_dir))
        hash_cert = subprocess.check_output(["openssl", "x509", "-inform",
            "PEM", "-subject_hash_old", "-in", "%s/cacert.pem" %
            self.__tmp_dir])
        hash_cert = hash_cert.decode().split('\n')[0]
        logging.info(f"certificate: {hash_cert} installed")
        os.system("mv %s/cacert.pem %s/%s.0" %
                (self.__tmp_dir,
                 self.__tmp_dir,
                 hash_cert))
        self.__device.shell("mount -o rw,remount,rw /system")
        self.__device.push("%s/%s.0" % (self.__tmp_dir, hash_cert),
                "/system/etc/security/cacerts/%s" % hash_cert)
        self.__device.shell("chmod 644 /system/etc/security/cacerts/%s.0" % hash_cert)
        self.__device.shell("mount -o ro,remount,ro /system")
        os.system("rm %s/%s.0" % (self.__tmp_dir, hash_cert))
    
    def generalinfo(self):
        """
        Print some information on the storing informations
        """
        self.__frida.load("script_frida/generalinfo.js", "store")
        infos = self.__frida.get_store()
        print ("\033[36mFile Directory :\033[39m \t\t%s" % infos['filesDirectory'])
        print ("\033[36mCache Directory :\033[39m \t\t%s" % infos['cacheDirectory'])
        print ("\033[36mExternal Cache Directory :\033[39m \t%s" % infos['externalCacheDirectory'])
        print ("\033[36mCode Cache Directory :\033[39m \t\t%s" % infos['codeCacheDirectory'])
        print ("\033[36mObb Directory :\033[39m \t\t%s" % infos['obbDir'])
        print ("\033[36mPackage Code path :\033[39m \t\t%s" % infos['packageCodePath'])

    def install_apk(self, apk):
        logging.info(f"install {apk}...")
        while True:
            try:
                if apk == self.__args.app and self.__args.config_xxhdpi:
                    subprocess.call(['adb', 'install-multiple', apk,
                        self.__args.config_xxhdpi] )
                else:
                    self.__device.install(apk)
                break
            except RuntimeError:
                continue
            except InstallError as e:
                if "Is the system running" in str(e):
                    continue
                elif "INSTALL_FAILED_TEST_ONLY" in str(e):
                    logging.warning("becareful install as test")
                    #subprocess.call(['adb', 'install', '-t', apk],
                    #        stdout=Log.STD_OUTPOUT, stderr=Log.STD_ERR, shell=False)
                    extcall.external_call(['adb', 'install', '-t', apk])
                    break
                elif "[INSTALL_FAILED_UPDATE_INCOMPATIBLE]" in str(e):
                    if apk == self.__args.app:
                        self.__device.uninstall(self.__package)
                    else:
                       logging.warning(str(e))
                elif "[INSTALL_FAILED_OLDER_SDK]" in str(e):
                    sys.stderr.write("APK need an Android platform more recent\n")
                    sys.exit(1)
                elif "[[INSTALL_FAILED_ALREADY_EXISTS:" in str(e):
                    logging.warning("application already exist reinstallation of " + self.__package)
                    self.__device.uninstall(self.__package)
                elif "INSTALL_FAILED_OLDER_SDK" in str(e):
                    logging.error("Android Phone use a too older sdk")
                    sys.exit(2)
                elif "INSTALL_FAILED_NO_MATCHING_ABIS" in str(e):
                    logging.error("Android Phone run on not matching architecture (arm/x86)")
                    sys.exit(3)
                else:
                    logging.warning(str(e))

    def __init__(self, package, args, tmp_dir):

        if ( not args.sdktools and not args.no_emulation ) or not args.phone:
            return

        self.__package = package
        self.__tmp_dir = tmp_dir
        self.__args = args
        self.__emulation = None
        self.__client = AdbClient(host="127.0.0.1", port=5037)
        self.__device = None


        bprint("Dynamic analysis")
        subprocess.call(["adb", "start-server"])
        if not args.no_emulation:
            self.__emulation = threading.Thread(target=self.emulation_f,
                    args=(args.sdktools, 
                          args.phone,
                          args.proxy,
                          self.__tmp_dir,
                          args.no_erase))
            self.__emulation.daemon = True
            self.__emulation.start()
        
        logging.info("waiting for connection device...")
        devices = []
        try:
            with timeout(60):
                while True:
                    if not args.no_emulation and not self.__emulation.isAlive():
                        logging.error("Device not found\n")
                        sys.exit(1)
                    devices = self.__client.devices()
                    for device in devices:
                        if not args.no_emulation:
                            if "emulator" in device.device.serial:
                                self.__device = device
                                break
                        else:
                            if device.device.serial == args.phone:
                                self.__device = device
                                break
                    else:
                        time.sleep(1)
                        continue
                    break
        except TimeoutError:
            pass

        if self.__device == None:
            logging.error("No devices found after 60s")
            sys.exit(1)
        else:
        
            wait_boot = False
            while True:
                try:
                    boot = self.__device.shell("getprop sys.boot_completed")[0]
                    if boot == '1':
                        break
                except:
                    if not wait_boot:
                        logging.info("waiting for boot device...")
                        wait_boot = True
                    pass

            #### writable system for recent version ####
            version_android = int(self.__device.shell("getprop ro.build.version.sdk"))
            if version_android >= 27:
                #os.system("adb root")
                extcall.external_call(["adb", "root"])
                while True:
                    if extcall.external_call(['adb', 'remount']) == 0:
                        break

            if self.__device.set_root() == 1:
                logging.error("Phone didn't root. Please root it before")
                sys.exit(1)

            if not args.noinstall:
                self.install_apk(args.app)

            if args.no_emulation:
                if args.proxy:
                    ps = subprocess.check_output('ps -aux', shell = True).decode().split('\n')
                    proxy_set = False
                    for p in ps:
                        if "-http-proxy" in p and "qemu" in p:
                            proxy_set = True
                            break
                    if not proxy_set:
                        self.__device.shell("settings put global http_proxy %s" %
                            args.proxy)
            # TODO add tcpdump for physical device
            # https://www.andreafortuna.org/2018/05/28/how-to-install-and-run-tcpdump-on-android-devices/


            # setup certificate
            if args.proxy_cert:
                self.setup_certificate(args.proxy_cert)
            #apps = device.shell("pm list packages -f")
            self.__frida = Frida(self.__device, self.__package)
            if args.env_apks:
                logging.info("prepare env")
                for apk in args.env_apks:
                    self.install_apk(apk[0])
                    self.__device.spawn(apk[1])
                    #self.__device.shell("monkey -p %s -c android.intent.category.LAUNCHER 1" % apk[1])
            logging.info(f"Spawn package: {self.__package}")
            self.__device.spawn(self.__package)
            #self.__frida.spawn(self.__package)
            #self.__device.shell("monkey -p %s -c android.intent.category.LAUNCHER 1" % self.__package)

            time.sleep(1)
            self.__frida.attach()


            modules = ModuleDynamic(self.__frida, self.__device, self.__tmp_dir,
                    args)

            #self.__frida.resume()

            #self.__frida.load("script_frida/socket.js", "print")

            self.generalinfo()
            cmd = DynCmd(modules, self.__device, self.__frida, self.__args)
            cmd.cmdloop()

            #sys.stdin.read()
            if not self.__args.no_emulation:
                self.__emulation.join()

            self.__frida.detach()


