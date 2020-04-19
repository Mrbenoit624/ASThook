
modules = []

class ModuleDynamicCmd:
    def __init__(self, name, desc, action):
        self.name = name
        self.desc = desc
        self.action = action
    def __call__(self, func):
        modules.append((self.name, self.desc, func, self.action))
        return func

def get_dynamic_modules():
    return modules
