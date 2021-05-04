from ppadb.client import Client as AdbClient
#from adb_shell.adb_device import AdbDeviceTcp
from asthook.log import debug, warning
import subprocess

class my_adb:
    """
    Class to manage adb it's only a wrapper
    """

    client = None

    def __init__(self, host="127.0.0.1", port=5037):
        self.client = AdbClient(host=host, port=port)

    def devices(self):
        return [ self.device(dev) for dev in self.client.devices()]

    def start_server(self):
        subprocess.call(["adb", "start-server"])

    class device:
        
        device = None
        need_su = False

        def __init__(self, device):
            self.device = device

        def shell(self, arg):
            if self.need_su:
                p = subprocess.Popen(["adb", "-s", self.device.serial, "shell", "su"],
                        stdin  = subprocess.PIPE, 
                        stdout = subprocess.PIPE)
                p.stdin.write(arg.encode() + b"\n")
                return p.stdout.read()
                #return self.device.shell(f"su 0 -c '{arg}'")
            return self.device.shell(arg)

        def root(self):
            if not self.shell("id")[4] == "0":
                return subprocess.call(["adb", "-s", self.device.serial, "root"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
            else:
                return 2

        def remount(self):
            import asthook.log as logging
            logging.debug("Try to remount android partition on rw")
            return subprocess.call(["adb", "-s", self.device.serial, "remount"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)

        def install_multiple(apk, xxhdpi):
            return subprocess.call(["adb", "-s", self.device.serial,
                "install-multiple", apk, xxhdpi],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)


        def set_root(self):
            if not self.shell("id")[4] == "0":
                if not self.shell("su 0 -c id")[4] == "0":
                    return 1
                self.need_su = True
            return 0

        def spawn(self, arg):
            return self.shell("monkey -p %s -c android.intent.category.LAUNCHER 1" %
                    arg)

        def push(self, src, dst):
            try:
                return self.device.push(src, dst)
            except RuntimeError as e:
                print(e)
                return 1

        def pull(self, src, dst):
            return self.device.pull(src, dst)

        def install(self, app, test=False):
            if test:
                return subprocess.call(["adb", "-s", self.device.serial,
                "install", "-t", apk],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
            return self.device.install(app)
            #return subprocess.call(["adb", "install", app])

        def uninstall(self, package):
            return self.device.uninstall(package)

        def dir_exist(self, dir):
            if "True" in self.device.shell("([ -d %s ] && echo 'True') || echo 'False'" % dir):
                return True
            return False

