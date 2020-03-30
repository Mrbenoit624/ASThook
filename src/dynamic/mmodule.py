
from analysis import add_module_dynamic

class Module_dynamic:
    def __init__(self, name, desc):
        add_module_dynamic(name, desc)
    def __call__(self, fun):
        print("", end='')
