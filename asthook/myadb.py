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
        #self.client = AdbDeviceTcp(host, port, default_timeout_s=9.)
        self.client = AdbClient(host=host, port=port)

    def devices(self):
        return [ self.device(dev) for dev in self.client.devices()]
        #self.client.connect(auth_timeout_s=20)
        #ret = []
        #ret.append(self.device(self.client))
        #return ret

    class device:
        
        device = None
        need_su = False

        def __init__(self, device):
            self.device = device

        def shell(self, arg):
            if self.need_su:
                return self.device.shell(f"su 0 {arg}")
            return self.device.shell(arg)

        def set_root(self):
            if not self.shell("id")[4] == "0":
                if not self.shell("su 0 id")[4] == "0":
                    return 1
                self.need_su = True
            return 0

        def spawn(self, arg):
            return self.shell("monkey -p %s -c android.intent.category.LAUNCHER 1" %
                    arg)

        def push(self, src, dst):
            return self.device.push(src, dst)

        def pull(self, src, dst):
            return self.device.pull(src, dst)

        def install(self, app):
            return self.device.install(app)
            #return subprocess.call(["adb", "install", app])

        def uninstall(self, package):
            return self.device.uninstall(package)

        def dir_exist(self, dir):
            if "True" in self.device.shell("([ -d %s ] && echo 'True') || echo 'False'" % dir):
                return True
            return False

