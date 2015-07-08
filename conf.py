from yaml import load

def reload_config():
    with open('conf.yaml') as config_file:
        return load(config_file)

conf = reload_config()
