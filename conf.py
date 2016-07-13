import yaml
import ostruct
import os

# configuration in dict form
configuration = None
config_source = ''

# configuration in OStruct form (can use dot notation)
_ostruct_conf = None


def config_changed():
    global config_source, configuration
    old_config = config_source
    config_source = get_config_source()
    changed = old_config != config_source
    if changed:
        configuration = get_config(config_source)
        set_oconf()
    return changed


def get_config_source():
    with open(config_filename()) as config_file:
        return config_file.read()


def get_config(src):
    return yaml.load(src)


def set_oconf():
    global configuration, _ostruct_conf
    _ostruct_conf = ostruct.OpenStruct(configuration)


def config_filename():
    env_filename = os.environ.get('CIMCONFIG')
    filename = env_filename if env_filename else 'default'
    return os.path.join(project_dir(), 'configs', '{0}.yaml'.format(filename))


def project_dir():
    # handle case where running as py2exe
    return '..' if os.path.basename(os.getcwd()) == 'dist' else '.'


def o_conf():
    return _ostruct_conf


config_changed()
