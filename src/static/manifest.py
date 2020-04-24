
from utils import *
import xml.etree.ElementTree as ET

#TODO add list services

class Manifest:
    
    CONST_ANDROID = "{http://schemas.android.com/apk/res/android}"

    def android(self, name):
        return "%s%s" % (self.CONST_ANDROID, name)

    def __init__(self, path):
        self.__path = path
        tree = ET.parse(path)
        self.root = tree.getroot()
        print(self.root.get('package'))
        self.package = self.root.get('package')
        self.list_permissions()
        self.list_activities()

        h2("Dangerous functionnality")
        # AllowBacup Functionality
        if not self.root.find('application').get("%sallowBackup" % self.CONST_ANDROID) == 'false':
            print(error("allowBackup: allow to backup all sensitive function on the cloud or on a pc"))
        # debuggable Functionality
        if self.root.find('application').get("%sdebuggable" % self.CONST_ANDROID) == 'true':
            print(error("debuggable: allow to debug the application in user mode"))

    def list_activities(self):
        app = self.root.find('application')
        t_all = app.findall('activity')
        t_all = t_all + app.findall('activity-alias')
        h2("Activities  Exported")
        print("All theses activities can be launch externaly as follow:")
        print("adb shell am start -S -n %s/%s" % (self.package, "<activity>"),
                end='\n\n')
        for obj in t_all:
            for intent_filter in obj.findall('intent-filter'):
                for action in intent_filter.findall('action'):
                    Output.add_to_store("manifest", "activity", "actions",
                            [obj.attrib[self.android('name')],
                             action.attrib[self.android('name')]])
                    #print(action.attrib[self.android('name')])
            if not self.android('exported') in obj.attrib or \
            obj.attrib[self.android('exported')]:
                print(obj.attrib[self.android('name')])
                Output.add_to_store("manifest", "activity", "exported",
                        obj.attrib[self.android('name')])

    def list_permissions(self):
        h2("Permission")
        print(warning("permissions used:"))
        for permissions in self.root.findall('uses-permission'):
            name = permissions.get(self.android('name'))
            print(name)
            Output.add_to_store("manifest", "permissions", "uses", name)
        print(warning("\npermissions created:"))
        for permissions in self.root.findall('permission'):
            name = permissions.get(self.android('name'))
            print(name)
            Output.add_to_store("manifest", "permissions", "create", name)

#
#    def Manifest(self, path):
#        """
#        Analyse the manifest
#        """
#        tree = ET.parse(path)
#        self.root = tree.getroot()
#        print(self.root.get('package'))
#        self.package = self.root.get('package')
#        #print(root.find('application').attrib)
#    
#        
#        self.list_activities()
# 
