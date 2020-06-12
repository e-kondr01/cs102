import hashlib
import io
import os
import pathlib
import sys
import zlib


def object_read(sha):
    gitdir = pathlib.Path('.git')
    path = gitdir / 'objects' / sha[:2] / sha[2:]

    with path.open(mode='rb') as f:
        raw = zlib.decompress(f.read())

    space = raw.find(b' ')
    object_type = raw[:space]

    null = raw.find(b'\x00', space)
    size = int(raw[space:null].decode('ascii'))
    if size != len(raw[null+1:]):
        raise Exception('Invalid length')

    return raw[null+1:]


def ls_tree(sha):
    data = object_read(sha)
    tree_items = parse_tree(data)
    for item in tree_items:
        print(item.decode())


def parse_tree(raw):
    pos = 0
    tree_items = []
    while pos < len(raw):
        space = raw.find(b' ', pos)
        null = raw.find(b'\x00', space)
        item = raw[space+1: null]
        tree_items.append(item)
        pos = null + 41
    return tree_items


def write_tree(directory='.', save=True):
    tree_entries = []
    exclude = ['.git']
    raw_entries = []
    for currentpath, folders, files in os.walk(directory, topdown=True):
        raw_entries.extend(folders)
        raw_entries.extend(files)
        for f in raw_entries:
            if f in exclude:
                raw_entries.remove(f)
        break
    for f in raw_entries:
        path = pathlib.Path(currentpath) / f
        filename = path.name.encode()
        try:
            sha1 = object_sha(path.open(mode='rb')).encode()
            f_mode = oct(os.stat(path)[0])[2:].encode()
        except PermissionError:
            f_mode = b'040000'
            sha1 = write_tree(path, save=False).encode()
        tree_entry = f_mode + b' ' + filename + b'\x00' + sha1
        tree_entries.append(tree_entry)
    print(tree_entries)
    obj = io.BytesIO(b''.join(tree_entries))
    if save:
        sha = hash_object(obj, obj_type=b'tree')
        print(sha)
    else:
        sha = object_sha(obj)
        return sha


def cat_file(sha):
    data = object_read(sha)
    print(data.decode())


def object_sha(filename):
    data = filename.read()
    sha = hashlib.sha1(data).hexdigest()
    return sha


def hash_object(filename, obj_type=b'blob'):
    data = filename.read()
    res = obj_type + b' ' + str(len(data)).encode() + b'\x00' + data
    sha = hashlib.sha1(res).hexdigest()
    gitdir = pathlib.Path('.git')
    path = gitdir / 'objects' / sha[:2] / sha[2:]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with path.open(mode='wb') as f:
        f.write(zlib.compress(res))

    return sha


def main():
    command = sys.argv[1]
    try:
        option = sys.argv[2]
    except IndexError:
        pass
    if command == 'init':
        os.mkdir('.git')
        os.mkdir('.git/objects')
        os.mkdir('.git/refs')
        with open('.git/HEAD', 'w') as f:
            f.write('ref: refs/heads/master\n')
        print('Initialized git repository')
    elif command == 'cat-file' and option == '-p':
        sha = sys.argv[3]
        cat_file(sha)
    elif command == 'hash-object' and option == '-w':
        filename = sys.argv[3]
        with open(filename, mode='rb') as f:
            sha = hash_object(f)
        print(sha)
    elif command == 'ls-tree' and option == '--name-only':
        sha = sys.argv[3]
        ls_tree(sha)
    elif command == 'write-tree':
        write_tree()
    else:
        print('Unknown command or invalid option')


if __name__ == '__main__':
    main()
