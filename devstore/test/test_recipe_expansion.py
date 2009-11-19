"""
test module for recursively resolving references in Cook-style recipes
"""

from tiddlywebplugins.devstore import _expand_recipe


def test_simple_expansion():
	base_path = "test/fixtures/repo"
	filepath = "%s/alpha/index.recipe" % base_path
	expected = [
		"%s/alpha/tiddlers/SiteTitle.tid" % base_path,
		"%s/alpha/tiddlers/lorem.tid" % base_path,
		"%s/alpha/plugins/foo.js" % base_path
	]
	assert _expand_recipe(filepath) == expected


def test_recursive_expansion():
	base_path = "test/fixtures/repo"
	filepath = "%s/bravo/index.recipe" % base_path

	actual = _expand_recipe(filepath)
	assert "%s/bravo/../alpha/tiddlers/SiteTitle.tid" % base_path in actual
	assert "%s/bravo/../alpha/tiddlers/lorem.tid" % base_path in actual
	assert "%s/bravo/../alpha/plugins/foo.js" % base_path in actual
	assert "%s/bravo/tiddlers/SiteTitle.tid" % base_path in actual
	assert "%s/bravo/tiddlers/ipsum.tid" % base_path in actual
	assert "%s/bravo/plugins/bar.js" % base_path in actual

	expected = [
		"%s/bravo/../alpha/tiddlers/SiteTitle.tid" % base_path,
		"%s/bravo/../alpha/tiddlers/lorem.tid" % base_path,
		"%s/bravo/../alpha/plugins/foo.js" % base_path,
		"%s/bravo/tiddlers/SiteTitle.tid" % base_path,
		"%s/bravo/tiddlers/ipsum.tid" % base_path,
		"%s/bravo/plugins/bar.js" % base_path
	]
	assert _expand_recipe(filepath) == expected
