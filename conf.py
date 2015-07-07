from yaml import load, dump
with open('conf.yaml') as conf:
    print(dump(load(conf)))