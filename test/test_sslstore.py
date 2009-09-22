from py.test import raises

from fixtures import _teststore, bagone, bagtwo, bagthree, bagfour # XXX: only available to core

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.config import config

from sslstore import SecureConnectionError


def setup_module(module):
	server_store = module.config["server_store"]
	store_config = server_store[1]
	store_config.update({ "store_module": server_store[0] })
	module.config["server_store"] = ["sslstore", store_config]
	module.config["ssl_bags"] = ["bagtwo", "bagfour"]
	module.store = _teststore()


def test_restricted_access():
	insecure_environ = {
		"wsgi.url_scheme": "http",
	}
	store.environ.update(insecure_environ)

	assert store.put(bagone) == None
	assert store.put(bagthree) == None
	raises(SecureConnectionError, "store.put(bagtwo)")
	raises(SecureConnectionError, "store.put(bagfour)")

	assert store.get(bagone)
	assert store.get(bagthree)
	raises(SecureConnectionError, "store.get(bagtwo)")
	raises(SecureConnectionError, "store.get(bagfour)")

	assert store.delete(bagone) == None
	assert store.delete(bagthree) == None
	raises(SecureConnectionError, "store.delete(bagtwo)")
	raises(SecureConnectionError, "store.delete(bagfour)")


def test_unrestrictedccess():
	secure_environ = {
		"wsgi.url_scheme": "https",
	}
	store.environ.update(secure_environ)

	assert store.put(bagone) == None
	assert store.put(bagtwo) == None
	assert store.put(bagthree) == None
	assert store.put(bagfour) == None

	assert store.get(bagone)
	assert store.get(bagtwo)
	assert store.get(bagthree)
	assert store.get(bagfour)

	assert store.delete(bagone) == None
	assert store.delete(bagtwo) == None
	assert store.delete(bagthree) == None
	assert store.delete(bagfour) == None


def test_storage(): # ensure actual store still works as expected
	bag_name = "Bar"
	title = "Foo"
	text = "lorem ipsum\ndolor sit amet"

	store = _teststore()
	bag = Bag(bag_name)
	store.put(bag)
	tiddler = Tiddler(title, bag_name)
	tiddler.text = "lorem ipsum\ndolor sit amet"
	store.put(tiddler)

	b = store.get(Bag(bag_name))
	t = store.get(Tiddler(title, bag_name))

	assert b.name == bag_name
	assert t.title == title
	assert t.bag == bag_name
	assert t.text == text
