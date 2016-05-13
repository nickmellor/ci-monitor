import yaml
import ostruct

configuration = None
_ostruct_conf = None


def config_changed():
    global configuration, _ostruct_conf
    old_conf = configuration
    get_config()
    changed = old_conf != configuration
    if changed:
        set_oconf()
    return changed


def set_oconf():
    global _ostruct_conf
    _ostruct_conf = ostruct.OpenStruct(configuration)


def o_conf():
    return _ostruct_conf


def get_config():
    global configuration
    with open('conf.yaml') as config_file:
        configuration = yaml.load(config_file)


config_changed()