from .GitFilesStore import GitFilesStore

class ModuleDynamic:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__device = device
        if args.files_store:
            GitFilesStore(frida, device, tmp_dir, args)

