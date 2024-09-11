import os
import importlib
import inspect
import itertools
from barfi import Block
import sys
import gen_block

# Get a list of all Python files in the current directory
files = [
    f[:-3]
    for f in os.listdir(os.path.dirname(__file__))
    if f.endswith(".py") and f != "__init__.py"
]

# Get a list of all Python files in the modules directories
modules_paths = [os.path.join("modules", i) for i in os.listdir("modules")]
block_folders = [
    os.path.join(modules_path, "blocks")
    for modules_path in modules_paths
    if os.path.exists(os.path.join(modules_path, "blocks"))
]
full_block_folders = [os.path.abspath(i) for i in block_folders]
modules_files = list(
    itertools.chain.from_iterable(
        [
            [
                os.path.join(block_folder, f[:-3])
                for f in os.listdir(full_block_folder)
                if f.endswith(".py") and f != "__init__.py"
            ]
            for full_block_folder, block_folder in zip(full_block_folders, block_folders)
        ]
    )
)
modules_files = [i.replace('/','.') for i in modules_files]
modules_files = [i.replace('\\','.') for i in modules_files]

# Dynamically import modules and collect Block instances
blocks = []
for file_ in files:
    module = importlib.import_module("." + file_, package=__name__)
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, Block):
            blocks.append(obj)

for p in full_block_folders:
    sys.path.append(p)

for file_ in modules_files:
    module = importlib.import_module(file_, package=__name__)
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, Block):
            blocks.append(obj)

# Export the collected blocks
__all__ = [block.__class__.__name__ for block in blocks]
