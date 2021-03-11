
import threading
import time

import os

from git import Repo
import shutil
from asthook.dynamic.module.register import ModuleDynamicCmd, BaseModuleDynamic

@ModuleDynamicCmd("files_store", "store all files read or written by application",
        bool)
class GitFilesStore(BaseModuleDynamic):
    def _init(self):
        self.__files = []
        self.__dict_files = []
        self.__stop = False
        self.load()

    def load(self):
        path = "%s/git_files" % self.tmp_dir
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        self.__repo_files = Repo.init(path)
        self.sc.append("script_frida/hookfile2.js")
        self.frida.load(self.sc[-1], "custom",
                self.on_message_git_files_update)
        self.to_join = threading.Thread(target=self.test, args =(lambda : self.__stop, )) 
        self.to_join.start()

    def on_message_git_files_update(self, message, data):
        if message['type'] == 'send':
            if 'payload' in message:
                file = message['payload']
                self.__files.insert(0, file)

    def test(self, stop):
        path = "%s/git_files" % self.tmp_dir
        while not stop:
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
                self.device.pull(file, "%s/%s" % (path, file))
                if os.stat("%s/%s" % (path, file)).st_size != 0:
                    self.__repo_files.index.add(["./%s" % file])
                    self.__repo_files.index.commit(file)
            except:
                continue

    def _remove(self):
        self.__stop = True
        self.to_join.join()

    @classmethod
    def auto_complete(cls, args):
        return []
