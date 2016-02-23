import yaml

conf = None


def config_changed():
    global conf
    old_conf = conf
    get_config()
    changed = old_conf != conf
    if changed:
        old_conf = conf
    return changed


def get_config():
    global conf
    with open('conf.yaml') as config_file:
        conf = yaml.load(config_file)


get_config()
