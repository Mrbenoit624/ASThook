
import frida
import time
import os
import sys
from subprocess import Popen, DEVNULL
from asthook.log import error, info
from asthook.conf import PACKAGE_PATH

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

    def check_abi(self):
        abi = self.__device.shell("getprop ro.product.cpu.abi")[:-1]
        if abi[0:3] == "arm":
            if abi[3:5] == "64":
                abi = "arm64"
            else:
                abi = "arm"
        info(f"abi = {abi}")
        return abi


    def __init__(self, device, package):
        self.__device = device
        self.__package = package
        self.__session = None
        self.__store = []

        self.__abi = self.check_abi()

        self.__device.push(f"{PACKAGE_PATH}/bin/frida-server_{self.__abi}", "/data/local/tmp/frida-server")
        self.__device.push(f"{PACKAGE_PATH}/bin/Frida.zip", "/data/local/tmp/Frida.zip")
        self.__device.shell("chmod 700 /data/local/tmp/frida-server")
        null = sys.stdout

        os.system('bash -c \'adb shell <<< "dalvikvm -cp /data/local/tmp/Frida.zip Frida;exit"\'')
        #extcall.external_call(['adb', 'shell', '<<<', '"dalvikvm -cp /data/local/tmp/Frida.zip Frida;exit"'])
        #os.system('bash -c \'adb shell <<< "/data/local/tmp/frida-server&"\';exit')
        
        #self.__server = frida.get_usb_device()
        for device in frida.enumerate_devices():
            if device.id == self.__device.device.serial:
                self.__server = device
    
    def attach(self, pid=None):
        try:
            self.__session = self.__server.attach(pid if pid else self.__package)
        except frida.NotSupportedError as e:
            print(str(e))
            sys.exit(1)
        except frida.ServerNotRunningError as e:
            print(str(e))
            error("Becareful you use a frida-server for the wrong architecture\n"
                    "go to https://github.com/frida/frida/releases and download\n"
                    "the good one and then replace the file /bin/frida-server\n"
                    "on the Asthook folder\n")
            sys.exit(1)

    def spawn(self, arg):
        self.__pid = self.__server.spawn(self.__package)
        self.attach()
        self.resume()
        time.sleep(1)

    def resume(self):
        if self.__pid:
            self.__server.resume(self.__pid)

    def load(self, file, option, function = None, absolute = False):
        if len(file.split(" ")) > 1:
            script = self.__session.create_script(file)
        else:
            if absolute:
                f = open(f"{file}", "r")
            else:
                f = open(f"{PACKAGE_PATH}/{file}", "r")
            try:
                script = self.__session.create_script(f.read())
            except frida.InvalidOperationError as e:
                self.spawn("")
                self.load(file, option, function)
                return

        if option == "print":
            script.on('message', self.on_message_print)
        if option == "store":
            script.on('message', self.on_message_store)
        if option == "custom":
            script.on('message', function)
        self.unload(file)
        while True:
            try:
                script.load()
                self.List_files_loaded[file] = script
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


    def unload(self, file):
        if file in self.List_files_loaded:
            try:
                self.List_files_loaded[file].unload()
            except frida.InvalidOperationError:
                pass
            del self.List_files_loaded[file]

    def reload(self):
        for k, v in self.List_files_loaded:
            self.load(k)

    def get_store(self):
        while len(self.__store) == 0:
            time.sleep(.1)
        return self.__store.pop()

    def post(self, script, message):
        if script in self.List_files_loaded:
            self.List_files_loaded[script].post(message)


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
