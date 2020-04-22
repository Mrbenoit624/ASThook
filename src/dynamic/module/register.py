
modules = []

class ModuleDynamicCmd:
    def __init__(self, name, desc, action, nargs=1):
        self.name = name
        self.desc = desc
        self.action = action
        self.nargs = nargs
    def __call__(self, func):
        modules.append((self.name, self.desc, func, self.action, self.nargs))
        return func

def get_dynamic_modules():
    return modules
