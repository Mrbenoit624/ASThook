import yaml

class Config:

    @classmethod
    def load(cls, args):
        with open(args.config) as config_file:
            yaml_config = yaml.full_load(config_file)
            print(args)
            for group in yaml_config:
                if not yaml_config[group]:
                    continue
                for i in yaml_config[group]:
                    for k, v in i.items():
                        if not type(eval("args.%s" % k)) == type(None):
                            continue
                        if isinstance(v, str) == True:
                            exec("args.%s='%s'" % (k, v))
                        else:
                            exec("args.%s=%s" % (k, v))
            print(args)
        return args
