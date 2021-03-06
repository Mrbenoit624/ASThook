import yaml

class Config:

    @classmethod
    def load_file(cls, args):
        for config in args.config:
            with open(config) as config_file:
                yaml_config = yaml.full_load(config_file)
                args = cls.load(yaml_config, args)
        return args

    @classmethod
    def load(cls, config, args):
        for group in config:
            if not config[group]:
                continue
            for i in config[group]:
                for k, v in i.items():
                    if not (type(eval("args.%s" % k)) == type(None) or \
                            eval("args.%s" % k) == False):
                        continue
                    if isinstance(v, str) == True:
                        exec("args.%s='%s'" % (k, v))
                    else:
                        exec("args.%s=%s" % (k, v))
        return args
