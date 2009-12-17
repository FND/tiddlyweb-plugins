import sys
import os

from urllib2 import urlopen, URLError
from pkg_resources import resource_filename

from tiddlyweb.util import write_utf8_file, std_error_message

from tiddlywebplugins.instancer import Instance
from tiddlywebplugins.instancer.sourcer import _expand_recipe


def spawn(instance_path, init_config, instance_module):
	"""
	convenience wrapper for instance-creation scripts
	"""
	# extend module search path for access to local tiddlywebconfig.py
	sys.path.insert(0, os.getcwd())
	from tiddlyweb.config import config, merge_config
	merge_config(config, init_config)

	package_name = instance_module.__name__.rsplit(".", 1)[0]
	instance = Instance(instance_path, config, instance_module.instance_config)
	instance.spawn(instance_module.store_structure)
	instance.update_store()


def get_tiddler_locations(store_contents, package_name):
	"""
	returns instance_tiddlers structure using tiddler paths from within the
	package if available

	store_structure is a dictionary listing tiddler URIs per bag

	packaged tiddlers must be listed in <package>/resources/tiddlers.index
	"""
	package_path = os.path.join(*package_name.split("."))
	tiddler_index = os.path.join("resources", "tiddlers.index")
	tiddler_index = resource_filename(package_name, tiddler_index)
	instance_tiddlers = {}
	try:
		filepaths = []
		f = open(tiddler_index)
		for line in f:
			bag, filename = line.rstrip().split("/", 1)
			filepath = os.path.join("resources", bag, filename)
			uri = "file:%s" % resource_filename(package_name, filepath)
			filepaths.append(uri)
			if filename.endswith(".js"): # unpack meta files into egg cache
				resource_filename(package_name, "%s.meta" % filepath)
			instance_tiddlers[bag] = filepaths
		f.close()
	except IOError:
		for bag, uris in store_contents.items():
			instance_tiddlers[bag] = uris
	return instance_tiddlers


def cache_tiddlers(package_name):
	"""
	creates local cache of instance tiddlers to be included in distribution

	reads store_contents from <package>.instance

	tiddler files are stored in <package>/resources/<bag>
	a complete index is stored in <package>/resources
	"""
	instance_module = __import__("%s.instance" % package_name,
		fromlist=["instance"]) # XXX: unnecessarily convoluted and constraining!?
	store_contents = instance_module.store_contents
	package_path = os.path.join(*package_name.split("."))

	sources = {}
	for bag, uris in store_contents.items():
		sources[bag] = []
		for uri in uris:
			if uri.endswith(".recipe"):
				urls = _expand_recipe(uri)
				sources[bag].extend(urls)
			else:
				sources[bag].append(uri)
		metas = []
		for uri in sources[bag]:
			if uri.endswith(".js"):
				metas.append("%s.meta" % uri)
		sources[bag].extend(metas)

	resources_path = os.path.join(package_path, "resources")
	try:
		os.mkdir(resources_path)
	except OSError: # directory exists
		pass

	for bag, uris in sources.items():
		bag_path = os.path.join(resources_path, bag)
		try:
			os.mkdir(bag_path)
		except OSError: # directory exists
			pass

		for uri in uris:
			filepath = os.path.join(bag_path, os.path.basename(uri))
			std_error_message("retrieving %s" % uri)
			try:
				content = urlopen(uri).read()
				content = unicode(content, "utf-8")
				write_utf8_file(filepath, content)
			except URLError:
				if uri.endswith(".meta"):
					std_error_message("no meta file found for %s" % uri[:-5])
				else:
					raise

	tiddler_index = "tiddlers.index"
	tiddler_paths = []
	for base_dir, dirs, files in os.walk(resources_path):
		bag = os.path.basename(base_dir)
		if bag in store_contents:
			filepaths = (os.path.join(bag, filename) for filename in files
				if not filename.endswith(".meta") and not filename == tiddler_index)
			tiddler_paths.extend(filepaths)
	filepath = "/".join([resources_path, tiddler_index])
	std_error_message("creating %s" % filepath)
	write_utf8_file(filepath, "\n".join(tiddler_paths))
