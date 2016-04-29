import yaml
import ostruct

configuration = None
ostruct_conf = None


def config_changed():
    global configuration, ostruct_conf
    old_conf = configuration
    get_config()
    changed = old_conf != configuration
    if changed:
        ostruct_conf = ostruct.OpenStruct(configuration)
    return changed


def conf():
    return ostruct_conf


def get_config():
    global configuration
    with open('conf.yaml') as config_file:
        configuration = yaml.load(config_file)


get_config()
