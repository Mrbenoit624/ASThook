
import threading
import time

import os

from git import Repo
import shutil

class GitFilesStore:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__device = device
        self.__tmp_dir = tmp_dir
        
        self.__files = []
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
            path = "%s/git_files" % self.__tmp_dir
            print("[++] {0}".format(message['payload']))
            file = message['payload']
            self.__files.insert(0, (file, path))
    
    def test(self):
        while True:
            if len(self.__files) == 0:
                time.sleep(.1)
                continue
            file, path = self.__files.pop()
            if not os.path.exists("%s/%s" % (path, os.path.dirname(file))):
                os.makedirs("%s/%s" % (path, os.path.dirname(file)))
            self.__device.pull(file, "%s/%s" % (path, file))
            if os.stat("%s/%s" % (path, file)).st_size != 0:
                self.__repo_files.index.add(["./%s" % file])
                self.__repo_files.index.commit(file)
