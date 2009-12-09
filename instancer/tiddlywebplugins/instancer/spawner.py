"""
convenience wrapper for instance-creation scripts
"""

import sys
import os
# extend module search path for access to local tiddlywebconfig.py
sys.path.insert(0, os.getcwd())

from tiddlyweb.config import config

from tiddlywebplugins.instancer import Instance


def spawn(instance_path, init_config, instance_module):
	package_name = instance_module.__name__.rsplit(".", 1)[0]
	instance = Instance(instance_path, init_config, instance_module.instance_config)
	instance.spawn(instance_module.store_structure)
	instance.update_store()
