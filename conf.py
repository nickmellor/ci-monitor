import yaml

conf = None


def config_changed():
    global conf
    new_conf = get_config()
    changed = new_conf != conf
    if changed:
        conf = new_conf
    return changed


def get_config():
    with open('conf.yaml') as config_file:
        return yaml.load(config_file)


conf = get_config()
