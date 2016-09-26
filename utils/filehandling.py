import errno
import os
import stat
import shutil

not_deleted = 0


def clear_dir(path):
    global not_deleted
    shutil.rmtree(path, ignore_errors=False, onerror=handle_remove_readonly)
    # print('Not deleted: {0}'.format(not_deleted))


def handle_remove_readonly(func, path, exc):
    global not_deleted
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        # os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO | stat.S_IWRITE | stat.S_IREAD) # 0777
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD) # 0777
        func(path)
    else:
        # not_deleted += 1
        print(exc)
        print("couldn't delete this file:\n{0}".format(path))
