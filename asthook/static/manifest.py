
from asthook.utils import *
import xml.etree.ElementTree as ET

#TODO add list services

class Manifest:
    
    CONST_ANDROID = "{http://schemas.android.com/apk/res/android}"

    PERMISSIONS_DANGEROUS = {
        'SEND_SMS' : 'Application can send premium sms without user interaction',
        'WRITE_EXTERNAL_STORAGE' : 'Write data on external storage',
        'READ_EXTERNAL_STORAGE'  : 'Read data on external storage',
        'RECEIVE_BOOT_COMPLETED' : 'Launch activity when phone boot',
        }

    def android(self, name):
        return "%s%s" % (self.CONST_ANDROID, name)

    @classmethod
    def convertA2path(cls, name):
        if not name:
            return name
        ret = name.replace("@drawable", "res/drawable*/")
        ret = ret.replace("@mipmap", "res/mipmap-*/")
        return ret

    def __init__(self, path):
        self.__path = path
        tree = ET.parse(path)
        self.root = tree.getroot()

        #### packages name ####
        print(self.root.get('package'))
        self.package = self.root.get('package')
        Output.add_to_store("manifest", "activity", "package", self.package)

        #### SdkVersion ####
        if 'platformBuildVersionCode' in self.root.attrib:
            self.version = self.root.attrib['platformBuildVersionCode']
        elif 'compileSdkVersion' in self.root.attrib:
            self.version = self.root.attrib['compileSdkVersion']
        else:
            self.version = '? latest ?'
        print('Build: ' + self.version)
        Output.add_to_store("manifest", "general", "version", self.version)
        logo = Manifest.convertA2path(
                    self.root.find('application').get(f"{self.CONST_ANDROID}icon"))
        if logo:
            Output.add_to_store("manifest", "general", "logo", logo)

        self.dangerous_functionality()
        self.list_permissions()
        self.list_activities()
        self.list_services()
        self.list_broadcasts()
        self.list_providers()


    def dangerous_functionality(self):
        h2("Dangerous functionnality")
        # AllowBacup Functionality
        if not self.root.find('application').get(
                "%sallowBackup" % self.CONST_ANDROID) == 'false':
            print(error("allowBackup: allow to backup all sensitive function"\
                        "on the cloud or on a pc"))
        # debuggable Functionality
        if self.root.find('application').get(
                "%sdebuggable" % self.CONST_ANDROID) == 'true':
            print(error(
                "debuggable: allow to debug the application in user mode"))

    def get_actions_activity(self, intent_filter, obj):
        actions = []
        deeplink = self.get_deeplink(intent_filter, obj)
        if deeplink:
            actions.append(deeplink)
        if not deeplink:
            #data_ = []
            #for data in intent_filter.findall('data'):
            #    data_.append(
            for action in intent_filter.findall('action'):
                action_ = "adb shell am start -n %s/%s -a %s " % (
                        self.package,
                        obj.attrib[self.android('name')],
                        action.attrib[self.android('name')])
                actions.append(action_)
                Output.add_to_store("manifest", "activity", "action",
                        {'name' : obj.attrib[self.android('name')],
                         'action': action.attrib[self.android('name')]})
        return actions

    def get_deeplink(self, intent_filter, obj):
        view = False
        browsable = False
        scheme = []
        host = []
        pathPrefix = []
        for action in intent_filter.findall('action'):
            if action.attrib[self.android('name')] == \
            "android.intent.action.VIEW":
                view = True
        for category in intent_filter.findall('category'):
            if category.attrib[self.android('name')] == \
            "android.intent.category.BROWSABLE":
                browsable = True
        for data_ in intent_filter.findall('data'):
            if self.android('scheme') in data_.attrib:
                scheme.append(data_.attrib[self.android('scheme')])
            if self.android('host') in data_.attrib:
                host.append(data_.attrib[self.android('host')])
            if self.android('pathPrefix') in data_.attrib:
                pathPrefix.append(data_.attrib[self.android('pathPrefix')])
        if view and browsable:
            #print(obj.attrib[self.android('name')] + " : " + str(data))
            Output.add_to_store("manifest", "deeplink",
                    obj.attrib[self.android('name')],
                    {'scheme': scheme,
                     'host' : host,
                     'pathPrefix': pathPrefix})
            return "adb shell am start -n %s/%s -a %s -d '%s://%s%s'" % (
                    self.package,
                    obj.attrib[self.android('name')],
                    "android.intent.action.VIEW",
                    info(str(scheme)),
                    info(str(host)),
                    info(str(pathPrefix)))
        return None

    def list_activities(self):
        app = self.root.find('application')
        t_all = app.findall('activity')
        t_all = t_all + app.findall('activity-alias')
        h2("Activities  Exported")
        print("All these activities can be launch externaly as follow:")
        print("adb shell am start -S -n %s/%s" % (self.package, "<activity>"),
                end='\n')
        for obj in t_all:
            actions_ = []
            for intent_filter in obj.findall('intent-filter'):
                actions_.extend(self.get_actions_activity(intent_filter, obj))
                #actions = intent_filter.findall('action')
                #if len(actions) > 0:
                #    is_action = True
                #for action in actions:
                #    Output.add_to_store("manifest", "activity", "actions",
                #            [obj.attrib[self.android('name')],
                #             action.attrib[self.android('name')]])
            if (self.android('exported') in obj.attrib and \
                    obj.attrib[self.android('exported')] == "true") or \
                    len(actions_) > 0:
                print('\n' + warning(obj.attrib[self.android('name')]), end=' ')
                self.check_need_permissions(obj)
                Output.add_to_store("manifest", "activity", "exported",
                        obj.attrib[self.android('name')])
                for action in actions_:
                    print('\t%s' % action)

    def get_actions_service(self, intent_filter, obj):
        actions = []
        for action in intent_filter.findall('action'):
            action_ = "adb shell am startservice -n %s/%s -a %s " % (
                    self.package,
                    obj.attrib[self.android('name')],
                    action.attrib[self.android('name')])
            actions.append(action_)
            Output.add_to_store("manifest", "service", "action",
                    {'name' : obj.attrib[self.android('name')],
                     'action': action.attrib[self.android('name')]})
        return actions

    def list_services(self):
        app = self.root.find('application')
        t_all = app.findall('service')
        h2("Services  Exported")
        print("All these services can be launch externaly as follow:")
        print("adb shell am startservice -S -n %s/%s" % (self.package, "<service>"),
                end='\n')
        for obj in t_all:
            actions_ = []
            for intent_filter in obj.findall('intent-filter'):
                actions_.extend(self.get_actions_service(intent_filter, obj))
            if (self.android('exported') in obj.attrib and \
                    obj.attrib[self.android('exported')] == "true") or \
                    len(actions_) > 0:
                print('\n' + warning(obj.attrib[self.android('name')]), end=' ')
                self.check_need_permissions(obj)
                Output.add_to_store("manifest", "service", "exported",
                        obj.attrib[self.android('name')])
                for action in actions_:
                    print('\t%s' % action)

    def check_need_permissions(self, obj):
        if self.android('permission') in obj.attrib:
            try:
                p_c = Output.get_store()['manifest']['permissions']['create']
            except KeyError:
                p_c = []
            pl_ = None
            for p, pl in p_c:
                if obj.attrib[self.android('permission')] == p:
                    pl_ = pl
            if not pl_ or pl == 'normal':
                print('| need permission: ' + obj.attrib[self.android('permission')], end='')
            elif pl_ == 'dangerous':
                print('| need permission: ' + error(obj.attrib[self.android('permission')]), end='')
            elif pl_ == 'signature':
                print('| need permission: ' + good(obj.attrib[self.android('permission')]), end='')

        print()

    def list_broadcasts(self):
        app = self.root.find('application')
        t_all = app.findall('receiver')
        # TODO: check if a permission is set with signature like that:
        # <permission android:name="package.mybroadcast_perm"
        # android:protectionLevel=signature" />
        h2("Receiver Exported")
        
        print("All these broadcasts can be launch externaly as follow:")
        print("adb shell am broadcast -a <action> --receiver-permission"\
                " <permission-needed>", end='\n\n')
        
        for obj in t_all:
            if self.android('exported') in obj.attrib and \
                    obj.attrib[self.android('exported')] == 'True':
                print(obj.attrib[self.android('name')])
                continue
            for intent_filter in obj.findall('intent-filter'):
                print(obj.attrib[self.android('name')], end=' ')
                self.check_need_permissions(obj)
                for action in intent_filter.findall('action'):
                    print('\t' + action.attrib[self.android('name')])
        pass

    def list_permissions(self):
        h2("Permission")
        print(warning("permissions used:"))
        for permissions in self.root.findall('uses-permission'):
            name = permissions.get(self.android('name'))
            if name.split('.')[-1] in self.PERMISSIONS_DANGEROUS:
                print("%s%s%s" % (
                    error(name),
                    " " * (80 - len(name)) + "| ",
                    self.PERMISSIONS_DANGEROUS[name.split('.')[-1]]))
            else:
                print("%s%s" % (name, " " * (80 - len(name)) + "|"))
            Output.add_to_store("manifest", "permissions", "uses", name)
        print(warning("\npermissions created:"))
        for permissions in self.root.findall('permission'):
            name = permissions.get(self.android('name'))
            protectionLevel = permissions.get(self.android('protectionLevel'))
            print("%s%s%s" % (
                error(name) if protectionLevel == 'dangerous' else good(name) if protectionLevel == 'signature' else name,
                " " * (80 - len(name)) + "| ",
                protectionLevel))
            Output.add_to_store("manifest", "permissions", "create", (name, protectionLevel))

    def list_providers(self):
        h2("Providers")
        
        app = self.root.find('application')
        t_all = app.findall('provider')

        for obj in t_all:
            if not (self.android('exported') in obj.attrib and \
                    obj.attrib[self.android('exported')] == "true"):
                    continue
            if self.android("authorities") in obj.attrib:
                authorities = obj.attrib[self.android('authorities')]
                name = obj.attrib[self.android('name')]
                Output.add_to_store("manifest", "provider", "exported",
                        (authorities, name))
                print(f"authorities: {authorities} | name: {name}", end=' ')
                self.check_need_permissions(obj)

