import os
import importlib
import inspect
from barfi import Block
import gen_block

# Get a list of all Python files in the current directory
files = [f[:-3] for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.py') and f != '__init__.py']

# Dynamically import modules and collect Block instances
blocks = []
for file_ in files:
    module = importlib.import_module('.' + file_, package=__name__)
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, Block):
            blocks.append(obj)

# Export the collected blocks
__all__ = [block.__class__.__name__ for block in blocks]
