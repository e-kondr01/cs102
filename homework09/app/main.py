import hashlib
import sys
import os
import pathlib
import zlib
import io


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


def parse_tree_entry(raw, start):
    space = raw.find(b' ', start)
    mode = raw[start:space]
    null = raw.find(b'\x00', space)
    item = raw[space+1, null]
    return null+39, item


def parse_tree(raw):
    pos = 0
    tree_items = []
    while pos < len(raw):
        pos, data = parse_tree_entry(raw, pos)
        tree_items.append(data)
    return tree_items


def write_tree(delimeter=''):
    tree_entries = []
    exclude = ['.git']
    for currentpath, folders, files in os.walk('.', topdown=True):
        folders[:] = [f for f in folders if f not in exclude]
        for file in files:
            path = pathlib.Path(currentpath) / file

            kt = os.stat(path)
            filename = path.name
            mode_path = f'{filename}'.encode()
            sha1 = object_sha(path, open(mode='rb'))
            tree_entry = mode_path + b'\x00' + sha1.encode()
            tree_entries.append(tree_entry)

    print(tree_entries)
    return
    obj = io.BytesIO(b''.join(tree_entries))
    sha = hash_object(obj, b'tree')
    print(sha)


def cat_file(sha):
    data = object_read(sha)
    print(data.decode())


def object_sha():
    pass


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
    if command == 'init':
        os.mkdir('.git')
        os.mkdir('.git/objects')
        os.mkdir('.git/refs')
        with open('.git/HEAD', 'w') as f:
            f.write('ref: refs/heads/master\n')
        print('Initialized git repository')
    elif command == 'cat-file':
        sha = sys.argv[3]
        cat_file(sha)
    elif command == 'hash-object':
        filename = sys.argv[3]
        with open(filename, mode='rb') as f:
            sha = hash_object(f)
        print(sha)
    elif command == 'ls-tree':
        sha = sys.argv[3]
        ls_tree(sha)
    elif command == 'write-tree':
        write_tree()
    else:
        raise RuntimeError('Unknown command')


if __name__ == '__main__':
    main()
