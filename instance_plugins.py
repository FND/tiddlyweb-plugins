"""
Instance Plugins
TiddlyWeb plugin providing a default "plugins" folder in instance directories

N.B.: This should be the first plugin to be invoked in system_plugins.

TODO:
* rename?
"""

import sys
import os


def init(config):
	plugins_path = os.path.join(os.getcwd(), "plugins")
	try:
		os.mkdir(plugins_path)
	except OSError: # directory exists
		pass
	sys.path.insert(0, plugins_path)
