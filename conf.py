import yaml
import ostruct

configuration = None


def config_changed():
    global configuration
    old_conf = configuration
    get_config()
    changed = old_conf != configuration
    if changed:
        old_conf = configuration
    return changed

def conf():
    return ostruct.OpenStruct(configuration)

def get_config():
    global configuration
    with open('conf.yaml') as config_file:
        configuration = yaml.load(config_file)


get_config()
