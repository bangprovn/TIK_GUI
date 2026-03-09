import os
import tempfile
import zipfile
from configparser import ConfigParser
from io import StringIO, BytesIO
from random import randint, choice


def extract(path, path2):
    zipfile.ZipFile(path).extractall(path2)


def get_all_file_paths(directory) -> Ellipsis:
    # Initialize file path list
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join strings to form the complete path
            file_paths.append(os.path.join(root, filename))

    # Return all file paths
    return file_paths


def v_code(num=6) -> str:
    ret = ""
    for i in range(num):
        num = randint(0, 9)
        # num = chr(random.randint(48,57))# ASCII digits
        letter = chr(randint(97, 122))  # lowercase letters
        Letter = chr(randint(65, 90))  # uppercase letters
        s = str(choice([num, letter, Letter]))
        ret += s
    return ret


def modify(path):
    with open(path + os.sep + 'run.sh', 'r', encoding='utf-8', newline='\n') as f, open(path + os.sep + "main.sh", 'w',
                                                                                        encoding='utf-8',
                                                                                        newline='\n') as m:
        for v in f.readlines():
            if v.startswith('subdir=$(dirname $(readlink -f "$0"))'):
                m.write('subdir=$(dirname "$1")\n')
            else:
                m.write(v.replace('$1', '$project'))
    os.remove(path + os.sep + 'run.sh')


def export(path, name, local):
    if not path:
        print("Path does not exist")
        return 1
    (info_ := ConfigParser())['module'] = {
        'name': f'{name}',
        'version': '1.0',
        'author': 'zip2mpk',
        'describe': f'{name}',
        'resource': 'main.zip',
        'identifier': f'{v_code()}',
        'depend': ''
    }
    info_.write((buffer2 := StringIO()))
    with zipfile.ZipFile((buffer := BytesIO()), 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as mpk:
        os.chdir(path)
        for i in get_all_file_paths("."):
            print(f"Writing: %s" % i.rsplit(".\\")[1])
            try:
                mpk.write(i)
            except Exception as e:
                print("Write failed: {}{}".format(i, e))
    with zipfile.ZipFile("".join([local, os.sep, name, ".mpk"]), 'w',
                         compression=zipfile.ZIP_DEFLATED, allowZip64=True) as mpk2:
        mpk2.writestr('main.zip', buffer.getvalue())
        mpk2.writestr('info', buffer2.getvalue())
    os.chdir(local)
    if os.path.exists(local + os.sep + name + ".mpk"):
        return local + os.sep + name + ".mpk"
    else:
        print("Packing %s failed" % (local + os.sep + name + ".mpk"))
        return False


def main(path, local):
    if not os.path.isfile(path):
        print("Not a file")
        return
    elif zipfile.is_zipfile(path):
        print(f"Processing: {path}")
        with tempfile.TemporaryDirectory() as tmpdirname:
            extract(path, tmpdirname)
            print("Modifying main script")
            modify(tmpdirname)
            print("Packing as MPK")
            out = export(tmpdirname, os.path.basename(path.split('.')[0]), os.path.dirname(path))
        os.chdir(local)
        try:
            os.remove(path)
        except:
            pass
        return out
    else:
        print("File format error!")
        return None
