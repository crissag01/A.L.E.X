import os

def find_file(filename, root="."):

    for path, dirs, files in os.walk(root):

        if filename in files:

            return os.path.join(path, filename)

    return "No encontrado."