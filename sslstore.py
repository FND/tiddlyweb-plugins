"""
SSL Store
TiddlyWeb store implementation allowing certain bags to be served only over SSL

This is a pseudo-store, merely wrapping around an actual store to provide
additional policy checks.

TODO:
* catch SecureConnectionError (middleware?)
* do not raise error when listing bags (merely hide secure bags?)
* rename?
* documentation
** description
** server_store config (module name changes, actual module name moved to store config)
* auto-redirect on error?
* provide init function for use as system plugin (not twanager plugin!?)
"""

import logging

from tiddlyweb.store import Store as Storage
from tiddlyweb.stores import StorageInterface


__version__ = "0.1.0"


class SecureConnectionError(Exception): # TODO: rename?
    """
    Traffic encryption (HTTPS/SSL) is required.
    """
    pass


class Store(StorageInterface):

	def __init__(self, environ=None):
		logging.debug("initializing SSL Store")
		super(self.__class__, self).__init__(environ)
		config = self.environ["tiddlyweb.config"]
		self.ssl_bags = config["ssl_bags"] # intentionally not providing empty fallback -- XXX: rename?
		real_store = config["server_store"][1]["store_module"] # XXX: rename? -- TODO: use pop method to keep config clean?
		self.real_store = Storage(real_store, self.environ)

	def recipe_delete(self, recipe):
		logging.debug("delete recipe %s" % recipe)
		self.real_store.delete(recipe)

	def recipe_get(self, recipe):
		logging.debug("get recipe %s" % recipe)
		return self.real_store.get(recipe)

	def recipe_put(self, recipe):
		logging.debug("put recipe %s" % recipe)
		self.real_store.put(recipe)

	def bag_delete(self, bag):
		logging.debug("delete bag %s" % bag)
		self._check_security(bag.name)
		self.real_store.delete(bag)

	def bag_get(self, bag):
		logging.debug("get bag %s" % bag)
		self._check_security(bag.name)
		return self.real_store.get(bag)

	def bag_put(self, bag):
		logging.debug("put bag %s" % bag)
		self._check_security(bag.name)
		self.real_store.put(bag)

	def tiddler_delete(self, tiddler):
		logging.debug("delete tiddler %s" % tiddler)
		self.real_store.delete(tiddler)

	def tiddler_get(self, tiddler):
		logging.debug("get tiddler %s" % tiddler)
		return self.real_store.get(tiddler)

	def tiddler_put(self, tiddler):
		logging.debug("put tiddler %s" % tiddler)
		self.real_store.put(tiddler)

	def user_delete(self, user):
		logging.debug("delete user %s" % user)
		self.real_store.delete(user)

	def user_get(self, user):
		logging.debug("get user %s" % user)
		return self.real_store.get(user)

	def user_put(self, user):
		logging.debug("put user %s" % user)
		return self.real_store.put(user)

	def list_recipes(self):
		logging.debug("list recipes")
		return self.real_store.list_recipes()

	def list_bags(self):
		logging.debug("list bags")
		return self.real_store.list_bags()

	def list_users(self):
		logging.debug("list users")
		return self.real_store.list_users()

	def list_tiddler_revisions(self, tiddler):
		logging.debug("list revisions %s" % tiddler)
		return self.real_store.list_tiddler_revisions(tiddler)

	def search(self, search_query):
		logging.debug("search %s" % search_query)
		return self.real_store.search(search_query)

	def _check_security(self, bag_name): # TODO: rename? -- TODO: should be decorator!?
		protocol = self.environ.get("wsgi.url_scheme")
		if protocol != "https" and bag_name in self.ssl_bags:
			raise SecureConnectionError("secure connection required")
