
modules = []

class ModuleStaticCmd:
    """
    Class decorator to manage module
    """
    def __init__(self, name, desc, action, nargs=1, choices=None):
        self.name = name
        self.desc = desc
        self.action = action
        self.nargs = nargs
        self.choices = choices
    def __call__(self, func):
        modules.append((self.name, self.desc, func, self.action, self.nargs,
            self.choices))
        return func

def get_static_modules():
    return modules
