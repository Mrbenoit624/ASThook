
import threading
import time

import os

from git import Repo
import shutil
from .register import ModuleDynamicCmd

@ModuleDynamicCmd("files_store", "store all files read or written by application")
class GitFilesStore:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__device = device
        self.__tmp_dir = tmp_dir

        self.__files = []
        self.__dict_files = []
        self.__stop = False
        self.load()

    def load(self):
        path = "%s/git_files" % self.__tmp_dir
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        self.__repo_files = Repo.init(path)
        self.__frida.load("script_frida/hookfile2.js", "custom",
                self.on_message_git_files_update)
        threading.Thread(target=self.test).start()

    def on_message_git_files_update(self, message, data):
        if message['type'] == 'send':
            if 'payload' in message:
                file = message['payload']
                self.__files.insert(0, file)

    def test(self):
        path = "%s/git_files" % self.__tmp_dir
        while not self.__stop:
            if len(self.__files) == 0:
                time.sleep(.1)
                continue
            file = self.__files.pop()
            if not file in self.__dict_files:
                self.__dict_files.append(file)
                print("[++] {0}".format(file))

            if not os.path.exists("%s/%s" % (path, os.path.dirname(file))):
                os.makedirs("%s/%s" % (path, os.path.dirname(file)))
            try:
                self.__device.pull(file, "%s/%s" % (path, file))
                if os.stat("%s/%s" % (path, file)).st_size != 0:
                    self.__repo_files.index.add(["./%s" % file])
                    self.__repo_files.index.commit(file)
            except:
                continue
