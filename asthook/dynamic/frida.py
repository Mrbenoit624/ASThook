
import frida
import time
import os
import sys
import threading
from subprocess import Popen, DEVNULL, PIPE
from asthook.log import error, info, debug

from asthook.conf import DIR, PACKAGE_PATH

from asthook.utils import extcall


class Frida:
    """
    Manage all interation with frida
    """

    List_files_loaded = {}

    def on_message_print(self, message, data):
        if message['type'] == 'send':
            print("[*] {0}".format(message['payload']))
        else:
            print(message)

    def on_message_store(self, message, data):
        data = data
        if message['type'] == 'send':
            self.__store.append(message['payload'])

    @classmethod
    def check_abi(cls, device):
        abi = device.shell("getprop ro.product.cpu.abi")[:-1]
        if abi[0:3] == "arm":
            if abi[3:5] == "64":
                abi = "arm64"
            else:
                abi = "arm"
        info(f"abi = {abi}")
        return abi


    def __init__(self, device, package, rooted):
        self.__device = device
        self.__package = package
        self.__session = None
        self.__store = []
        self.__rooted = rooted
        self.__pid = None

        if rooted:
            self.__abi = Frida.check_abi(self.__device)

            self.__device.push(f"{PACKAGE_PATH}/bin/frida-server_{self.__abi}", "/data/local/tmp/frida-server")
            self.__device.push(f"{PACKAGE_PATH}/bin/Frida.zip", "/data/local/tmp/Frida.zip")
            self.__device.shell("chmod 700 /data/local/tmp/frida-server")
            null = sys.stdout

            self.__frida_launch = threading.Thread(target=self.launch_frida,
                    args=())
            self.__frida_launch.start()
        
        for device in frida.enumerate_devices():
            if device.id == self.__device.device.serial:
                self.__server = device

    def launch_frida(self):
        if self.__device.need_su:
            p = Popen(["adb", "-s", self.__device.device.serial, "shell",
                "su", "-c",
                "dalvikvm\ -cp\ /data/local/tmp/Frida.zip\ Frida"],
                stdin  = PIPE, 
                stdout = PIPE)
        else:
            p = Popen(["adb", "-s", self.__device.device.serial, "shell",
                "dalvikvm", "-cp", "/data/local/tmp/Frida.zip", "Frida"],
                stdin  = PIPE, 
                stdout = PIPE)

    def check_frida_server(self):
        if not self.__frida_launch.is_alive():
            self.__frida_launch.start()


    def _attach(self, pid=None):
        try:
            if self.__rooted:
                self.__session = self.__server.attach(pid if pid else self.__package)
            else:
                if not pid:
                    try:
                        debug(f"pidof {self.__package}")
                        try:
                            package = self.__device.shell(f"ps {self.__package}").split('\n')[1].split()[1]
                            pid=int(package)
                        except IndexError:
                            pid=int(self.__device.shell(f"pidof {self.__package}")[:-1])
                        self.__session = self.__server.attach(pid)
                    except ValueError as e:
                        return 3
        except frida.NotSupportedError as e:
            print(str(e))
            sys.exit(1)
        except frida.ServerNotRunningError as e:
            return 1
        except frida.ProcessNotFoundError as e:
            return 2
        return 0

    def attach(self, pid=None):
        if not self.__rooted:
            for i in range(0, 10):
                if self._attach(pid) == 0:
                    return
                time.sleep(.1)
        ret = self._attach(pid)
        if ret == 2:
            while True:
                time.sleep(.1)
                self.attach(pid)
        if ret == 1:
            error("Becareful you use a frida-server for the wrong architecture\n"
                    "go to https://github.com/frida/frida/releases and download\n"
                    "the good one and then replace the file /bin/frida-server\n"
                    "on the Asthook folder\n")
            sys.exit(1)
        if ret == 3:
            error("Command to get pid of process failed\n")
            sys.exit(1)

    def spawn(self, arg):
        print(self.__rooted)
        if self.__rooted:
            self.__pid = self.__server.spawn(self.__package)
        else:
            self.__device.spawn(self.__package)
        time.sleep(1)
        self.attach()
        #self.resume()
        #time.sleep(1)

    def resume(self):
        if self.__rooted and self.__pid:
            debug("resume application")
            try:
                self.__server.resume(self.__pid)
            except frida.NotSupportedError as e:
                time.sleep(1)
                self.resume()

    def load(self, file, option, function = None, absolute = False, script=None):
        if script != None:
            script_ = self.__session.create_script(script)
        else:
            try:
                if absolute:
                    f = open(f"{file}", "r")
                else:
                    f = open(f"{PACKAGE_PATH}/{file}", "r")
            except FileNotFoundError as e:
                return 1, e
            except IsADirectoryError as e:
                return 2, e
            try:
                script_ = self.__session.create_script(f.read())
            except frida.InvalidOperationError as e:
                self.spawn("")
                self.load(file, option, function, absolute)
                return 0, ""
            except frida.InvalidArgumentError as e:
                return 3, e
            except UnicodeDecodeError as e:
                return 4, e

        if option == "print":
            script_.on('message', self.on_message_print)
        if option == "store":
            script_.on('message', self.on_message_store)
        if option == "custom":
            script_.on('message', function)
        self.unload(file)
        while True:
            try:
                script_.load()
                self.List_files_loaded[file] = {
                        "script": script_,
                        "option": option,
                        "function": function,
                        "absolute": absolute}

                break
            except frida.InvalidArgumentError as e:
                print(str(e))
                raise Exception("Your script js sucks!\n")
            except frida.TransportError as e:
                print(str(e))
                time.sleep(1)
                # raise Exception("Error frida")
            except frida.InvalidOperationError as e:
                print(str(e))
                time.sleep(1)
        return 0, ""


    def unload(self, file):
        if file in self.List_files_loaded:
            try:
                self.List_files_loaded[file]["script"].unload()
            except frida.InvalidOperationError:
                pass
            del self.List_files_loaded[file]

    def reload(self):
        for k, v in self.List_files_loaded:
            self.load(k, v["option"], v["function"], v["absolute"], script=v["script"])

    def get_store(self):
        while len(self.__store) == 0:
            time.sleep(.1)
        return self.__store.pop()

    def post(self, script, message):
        if script in self.List_files_loaded:
            self.List_files_loaded[script]["script"].post(message)


    def detach(self):
        self.__session.detach()


        #os.system('frida -D emulator-5554 -l test.js -f %s --no-pause' % \
                #        self.__package)
        #myPopen = Popen(['frida', '-D', 'emulator-5554', 'l',
        #            'test.js', '-f', self.__package, '--no-pause'],
        #            stdin = sys.stdin,
        #            stdout = sys.stdout,
        #            stderr = DEVNULL,
        #            encoding = 'utf8')
        #while True:
        #    status = myPopen.poll()
        #    if status is not None:
        #        break
#try:
#    outs, errs = proc.communicate(timeout=15)
#except TimeoutExpired:
#    proc.kill()
#    outs, errs = proc.communicate()
