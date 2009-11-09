import os

from urllib2 import HTTPError, URLError

from py.test import raises

from twp.instancer.sourcer import from_list, from_source, from_plugin, \
	from_tid, from_tiddler, _get_uri, _get_title_from_uri


FIXTURES_DIR = "test/fixtures"
REPO_DIR = "%s/repo" % FIXTURES_DIR
REPO_URI = "file:%s" % REPO_DIR


def test_recipe_expansion():
	uri = "%s/alpha/index.recipe" % REPO_URI
	tiddlers = from_list([uri])

	actual = [tiddler.title for tiddler in tiddlers]
	expected = ["common", "Foo", "Lorem", "foo"]
	assert actual == expected


def test_recursive_recipe_expansion():
	uri = "%s/bravo/index.recipe" % REPO_URI
	tiddlers = from_list([uri])

	actual = [tiddler.title for tiddler in tiddlers]
	expected = ["common", "Foo", "Lorem", "foo",
		"common", "Bar", "Ipsum", "BarPlugin"]
	assert actual == expected


def test_from_list():
	uris = [
		"%s/alpha/tiddlers/Foo.tid" % REPO_URI,
		"%s/alpha/tiddlers/lorem.tiddler" % REPO_URI,
		"%s/alpha/plugins/foo.js" % REPO_URI,
		"%s/alpha/index.recipe" % REPO_URI
	]
	tiddlers = from_list(uris)

	actual = [tiddler.title for tiddler in tiddlers]
	expected = ["Foo", "Lorem", "foo", "common", "Foo", "Lorem", "foo"]
	assert actual == expected

	tiddler = tiddlers[0]
	assert tiddler.title == "Foo"
	assert tiddler.tags == ["foo", "bar baz"]
	assert tiddler.text == "lorem ipsum\nfoo\ndolor sit amet"

	tiddler = tiddlers[1]
	assert tiddler.title == "Lorem"
	assert tiddler.tags == ["foo", "bar baz"]
	assert tiddler.text == "lorem ipsum\ndolor sit amet"

	tiddler = tiddlers[2]
	assert tiddler.title == "foo"
	assert tiddler.tags == ["systemConfig"]
	assert tiddler.text == 'alert("foo");'


def test_from_source():
	uri = "%s/alpha/tiddlers/lorem.tiddler" % REPO_URI
	tiddler = from_source(uri)
	assert tiddler.title == "Lorem"
	assert tiddler.tags == ["foo", "bar baz"]
	assert tiddler.text == "lorem ipsum\ndolor sit amet"

	uri = "%s/alpha/tiddlers/Foo.tid" % REPO_URI
	tiddler = from_source(uri)
	assert tiddler.title == "Foo"
	assert tiddler.tags == ["foo", "bar baz"]
	assert tiddler.text == "lorem ipsum\nfoo\ndolor sit amet"

	uri = "%s/alpha/plugins/foo.js" % REPO_URI
	tiddler = from_source(uri)
	assert tiddler.title == "foo"
	assert tiddler.tags == ["systemConfig"]
	assert tiddler.text == 'alert("foo");'


def test_from_plugin():
	uri = "%s/alpha/plugins/foo.js" % REPO_URI
	tiddler = from_plugin(uri)

	assert tiddler.title == "foo"
	assert tiddler.tags == ["systemConfig"]
	assert tiddler.text == 'alert("foo");'

	uri = "%s/bravo/plugins/bar.js" % REPO_URI
	tiddler = from_plugin(uri)

	assert tiddler.title == "BarPlugin"
	assert tiddler.tags == ["foo", "bar baz", "..."]
	assert tiddler.text == 'alert("bar");'


def test_from_tid():
	uri = "%s/alpha/tiddlers/Foo.tid" % REPO_URI
	tiddler = from_tid(uri)

	assert tiddler.title == "Foo"
	assert tiddler.tags == ["foo", "bar baz"]
	assert tiddler.text == "lorem ipsum\nfoo\ndolor sit amet"

	uri = "%s/bravo/tiddlers/Bar.tid" % REPO_URI
	tiddler = from_tid(uri)

	assert tiddler.title == "Bar"
	assert tiddler.tags == ["foo", "bar baz", "..."]
	assert tiddler.text == "lorem ipsum\nbar\ndolor sit amet"

	uri = "%s/alpha/tiddlers/common.tid" % REPO_URI
	tiddler = from_tid(uri)

	assert tiddler.title == "common"
	assert tiddler.tags == []
	assert tiddler.text == "Alpha"

	uri = "%s/bravo/tiddlers/common.tid" % REPO_URI
	tiddler = from_tid(uri)

	assert tiddler.title == "common"
	assert tiddler.tags == []
	assert tiddler.text == "Bravo"


def test_from_tiddler():
	uri = "%s/alpha/tiddlers/lorem.tiddler" % REPO_URI
	tiddler = from_tiddler(uri)

	assert tiddler.title == "Lorem"
	assert tiddler.tags == ["foo", "bar baz"]
	assert tiddler.text == "lorem ipsum\ndolor sit amet"

	uri = "%s/bravo/tiddlers/ipsum.tiddler" % REPO_URI
	tiddler = from_tiddler(uri)

	assert tiddler.title == "Ipsum"
	assert tiddler.tags == ["foo", "bar baz", "..."]
	assert tiddler.text == "lorem ipsum\ndolor sit amet"


def test_get_title_from_uri():
	uri = "foo.bar"
	actual = _get_title_from_uri(uri, ".bar")
	expected = "foo"
	assert actual == expected

	uri = "foo.bar"
	actual = _get_title_from_uri(uri, "")
	expected = "foo.bar"
	assert actual == expected

	uri = "http://example.org/foo%20bar%20baz.foo"
	actual = _get_title_from_uri(uri, ".foo")
	expected = "foo bar baz"
	assert actual == expected

	uri = "%3C%3E%7E%2E%7B%7D%7C%5C%2D%60%5F%5E.bar"
	actual = _get_title_from_uri(uri, ".bar")
	expected = "<>~.{}|\-`_^"
	assert actual == expected


def test_get_uri():
	uri = "file:%s/dummy.txt" % os.path.abspath(FIXTURES_DIR)
	content = _get_uri(uri)
	assert content == "lorem ipsum\ndolor sit amet\n"

	uri = "file:/%s/dummy.txt" % os.path.abspath(FIXTURES_DIR)
	raises(URLError, "_get_uri(uri)")

	uri = "file://%s/dummy.txt" % os.path.abspath(FIXTURES_DIR)
	content = _get_uri(uri)
	assert content == "lorem ipsum\ndolor sit amet\n"

	uri = "file:%s/dummy.txt" % FIXTURES_DIR
	content = _get_uri(uri)
	assert content == "lorem ipsum\ndolor sit amet\n"

	uri = "file:%s/../dummy.txt" % REPO_DIR
	content = _get_uri(uri)
	assert content == "lorem ipsum\ndolor sit amet\n"

	uri = "%s/dummy.txt" % FIXTURES_DIR
	raises(ValueError, "_get_uri(uri)")

	uri = "foo"
	raises(ValueError, "_get_uri(uri)")

	uri = "file:foo"
	raises(URLError, "_get_uri(uri)")

	uri = "file:/foo"
	raises(URLError, "_get_uri(uri)")

	uri = "file://foo"
	raises(URLError, "_get_uri(uri)")

	uri = "file:///foo"
	raises(URLError, "_get_uri(uri)")

	uri = "http://localhost/foo"
	raises(URLError, "_get_uri(uri)")

	# disabled to avoid relying on connectivity
	#uri = "http://example.org/foo"
	#raises(HTTPError, "_get_uri(uri)")
