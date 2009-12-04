import os


def get_tiddler_locations(store_contents, package):
	"""
	returns instance_tiddlers structure using tiddler paths from within the
	package if available

	store_structure is a dictionary listing tiddler URIs per bag

	packaged tiddlers must be listed in <package>/resources/tiddlers.index
	"""
	tiddler_index = os.path.join(package, "resources", "tiddlers.index")
	instance_tiddlers = []
	try:
		filepaths = []
		f = open(tiddler_index)
		for line in f:
			bag, filename = line.rstrip().split("/", 1)
			filepath = os.path.join("resources", bag, filename)
			uri = "file:%s" % resource_filename(package, filepath)
			filepaths.append(uri)
			if filename.endswith(".js"): # unpack meta files into egg cache
				resource_filename(package, "%s.meta" % filepath)
			instance_tiddlers.append((bag, filepaths))
		f.close()
	except IOError:
		for bag, uris in store_contents.items():
			instance_tiddlers.append((bag, uris))
	return instance_tiddlers
