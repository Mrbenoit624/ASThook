
modules = []

class ModuleDynamicCmd:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
    def __call__(self, func):
        modules.append((self.name, self.desc, func))
        return func

def get_dynamic_modules():
    return modules
