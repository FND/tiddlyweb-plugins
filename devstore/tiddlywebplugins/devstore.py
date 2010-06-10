"""
Dev Store
TiddlyWeb store implementation supporting client-side development

primarily intended for TiddlyWiki plugin development

Features:
* supports Cook-style .recipe files
* supports JavaScript (.js) files
* uses config["local_instance_tiddlers"] or config["instance_tiddlers"] files
  for referencing bag contents
* uses .tid files for non-JavaScript content
* no revisions

TODO:
* documentation (esp. local vs. remote versions)
* Unicode handling
* write locks
* testing: policies, non-remotes ({bag,tiddler}_get, list_bags), tiddler_delete, user_*, list_users
"""

import os
import logging

import simplejson

from shutil import rmtree
from urllib import unquote

from tiddlyweb import __version__ as TIDDLYWEB_VERSION
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User
from tiddlyweb.model.policy import Policy
from tiddlyweb.store import (NoRecipeError, NoBagError, NoTiddlerError,
	NoUserError, StoreMethodNotImplemented)
from tiddlyweb.stores import StorageInterface
from tiddlyweb.stores.text import _encode_filename as encode
from tiddlyweb.serializer import Serializer
from tiddlyweb.util import read_utf8_file, write_utf8_file

from tiddlywebplugins.twimport import url_to_tiddler


__version__ = "0.7.6"

# XXX: should be class attributes?
RECIPE_EXT = ".recipe"
TIDDLER_EXT = ".tid"
PLUGIN_EXT = ".js"
USER_EXT = ".user"


class ConfigurationError(Exception):
	pass


class Store(StorageInterface):

	def __init__(self, store_config=None, environ=None):
		logging.debug("initializing Dev Store")
		super(Store, self).__init__(store_config, environ)

		config = self.environ["tiddlyweb.config"]

		self._root = store_config["store_root"]
		if not os.path.isabs(self._root):
			self._root = os.path.join(config["root_dir"], self._root)

		try:
			self._index = config["local_instance_tiddlers"]
		except KeyError:
			try:
				self._index = config["instance_tiddlers"]
			except KeyError:
				raise ConfigurationError("instance_tiddlers not defined")
		self.serializer = Serializer("text")

		if not os.path.exists(self._root):
			os.mkdir(self._root)
		for bag_name in self._index:
			bag = Bag(bag_name)
			bag_path = self._bag_path(bag)
			if not os.path.exists(bag_path):
				self.bag_put(bag)

	def recipe_get(self, recipe):
		logging.debug("get recipe %s" % recipe.name)
		recipe_path = self._recipe_path(recipe)
		try:
			contents = _read_file(recipe_path)
		except IOError, exc:
			raise NoRecipeError(exc)
		self.serializer.object = recipe
		return self.serializer.from_string(contents)

	def recipe_put(self, recipe):
		logging.debug("put recipe %s" % recipe.name)
		recipe_path = self._recipe_path(recipe)
		self.serializer.object = recipe
		write_utf8_file(recipe_path, self.serializer.to_string())

	def recipe_delete(self, recipe):
		logging.debug("delete recipe %s" % recipe.name)
		recipe_path = self._recipe_path(recipe)
		try:
			os.remove(recipe_path)
		except IOError, exc:
			raise NoRecipeError(exc)

	def bag_get(self, bag):
		logging.debug("get bag %s" % bag.name)

		bag_path = self._bag_path(bag)

		if not (self._index.get(bag.name, None) or os.path.isdir(bag_path)):
			raise NoBagError

		if TIDDLYWEB_VERSION.startswith("1.0"):
			if not (hasattr(bag, "skinny") and bag.skinny):
				for tiddler in self.list_bag_tiddlers(bag):
					bag.add_tiddler(tiddler)

		bag.desc = self._read_description(bag_path)
		bag.policy = self._read_policy(bag_path)

		return bag

	def bag_put(self, bag):
		logging.debug("put bag %s" % bag.name)

		bag_path = self._bag_path(bag)
		if not os.path.exists(bag_path):
			os.mkdir(bag_path)

		self._write_description(bag.desc, bag_path)
		self._write_policy(bag.policy, bag_path)

	def bag_delete(self, bag):
		logging.debug("delete bag %s" % bag.name)
		bag_path = self._bag_path(bag)
		rmtree(bag_path)

	def tiddler_get(self, tiddler):
		logging.debug("get tiddler %s" % tiddler)
		try:
			tiddler = self._get_local_tiddler(tiddler)
		except IOError:
			try:
				tiddler = self._get_remote_tiddler(tiddler)
			except KeyError, exc:
				raise NoTiddlerError(exc)
		if not tiddler.created:
			tiddler.created = tiddler.modified
		tiddler.revision = 1
		return tiddler

	def tiddler_put(self, tiddler):
		logging.debug("put tiddler %s" % tiddler)

		tiddler_path = self._tiddler_path(tiddler)
		tiddler.revision = 1

		self.serializer.object = tiddler
		write_utf8_file(tiddler_path, self.serializer.to_string())

		self.tiddler_written(tiddler)

	def tiddler_delete(self, tiddler):
		logging.debug("delete tiddler %s" % tiddler)
		tiddler_path = self._tiddler_path(tiddler)
		os.remove(tiddler_path)

	def user_get(self, user):
		logging.debug("get user %s" % user)
		user_path = self._user_path(user)
		try:
			user_info = _read_file(user_path)
			user_data = simplejson.loads(user_info)
			for key, value in user_data.items():
				if key == "roles":
					user.roles = set(value)
				else:
					if key == "password": # XXX: ???
						key = "_password"
					user.__setattr__(key, value)
			return user
		except IOError, exc:
			raise NoUserError(exc)

	def user_put(self, user):
		logging.debug("put user %s" % user.usersign)
		user_path = self._user_path(user)
		user_dict = {}
		for key in ["usersign", "note", "_password", "roles"]:
			value = user.__getattribute__(key)
			if key == "roles":
				user_dict[key] = list(value)
			else:
				if key == "_password": # XXX: ???
					key = "password"
				user_dict[key] = value
		user_info = simplejson.dumps(user_dict, indent=0)
		write_utf8_file(user_path, user_info)

	def user_delete(self, user):
		logging.debug("delete user %s" % user.usersign)
		user_path = self._user_path(user)
		try:
			os.remove(user_path)
		except IOError, exc:
			raise NoUserError(exc)

	def list_recipes(self):
		logging.debug("list recipes")
		return (Recipe(decode(filename[:-7])) for filename in
			os.listdir(self._root) if filename.endswith(RECIPE_EXT))

	def list_bags(self):
		logging.debug("list bags")
		locals = [decode(dirname) for dirname in os.listdir(self._root)
			if os.path.isdir(os.path.join(self._root, dirname))]
		remotes = [bag_name for bag_name in self._index]
		names = set(locals).union(remotes)
		return (Bag(name) for name in names)

	def list_users(self):
		logging.debug("list users")
		return (User(decode(filename[:-5])) for filename in
			os.listdir(self._root) if filename.endswith(USER_EXT))

	def list_bag_tiddlers(self, bag):
		bag_path = self._bag_path(bag)
		locals = [decode(filename[:-4]) for filename in os.listdir(bag_path)
			if filename.endswith(TIDDLER_EXT)]
		store = self.environ.get("tiddlyweb.store", self)
		try:
			uris = self._index[bag.name]
			remotes = [_extract_title(uri) for uri in
					_resolve_references(uris)]
			titles = set(locals).union(remotes)
		except KeyError: # non-remote bag
			titles = locals
		for title in titles:
			tiddler = self.tiddler_get(Tiddler(title, bag.name))
			tiddler.store = store
			yield tiddler

	def list_tiddler_revisions(self, tiddler):
		logging.debug("list revisions %s" % tiddler)
		raise StoreMethodNotImplemented # store is revisionless

	def search(self, query):
		bags = self.list_bags()
		for bag in bags:
			for tiddler in self.list_bag_tiddlers(bag):
				if query in tiddler.bag:
					yield tiddler
				if query in tiddler.tags:
					yield tiddler
				for field in tiddler.fields:
					if query in tiddler.fields[field]:
						yield tiddler
				if query in tiddler.text:
					yield tiddler

	def _write_description(self, desc, base_path):
		desc_path = self._description_path(base_path)
		write_utf8_file(desc_path, desc)

	def _read_description(self, base_path):
		desc_path = self._description_path(base_path)
		try:
			return _read_file(desc_path)
		except IOError:
			return ""

	def _write_policy(self, policy, base_path):
		policy_dict = {}
		for key in Policy.attributes:
			policy_dict[key] = getattr(policy, key)
		json = simplejson.dumps(policy_dict)
		policy_path = self._policy_path(base_path)
		write_utf8_file(policy_path, json)

	def _read_policy(self, base_path):
		policy_path = self._policy_path(base_path)
		json = _read_file(policy_path)
		policy = Policy()
		for key, value in simplejson.loads(json).items():
			setattr(policy, key, value) # XXX: use setattr function instead of __setattr__ method?
		return policy

	def _get_local_tiddler(self, tiddler):
		tiddler_path = self._tiddler_path(tiddler)
		contents = _read_file(tiddler_path)
		self.serializer.object = tiddler
		return self.serializer.from_string(contents)

	def _get_remote_tiddler(self, tiddler):
		uris = self._index[tiddler.bag]
		candidates = [uri for uri in _resolve_references(uris)
			if _extract_title(uri) == tiddler.title]
		try:
			uri = candidates[-1] # XXX: best guess!?
		except IndexError, exc:
			raise NoTiddlerError(exc)

		bag = tiddler.bag # XXX: caching bag attribute hacky/insufficient?
		tiddler = url_to_tiddler(uri)
		tiddler.bag = bag

		return tiddler

	def _recipe_path(self, recipe):
		return "%s.recipe" % os.path.join(self._root, encode(recipe.name))

	def _bag_path(self, bag):
		return os.path.join(self._root, encode(bag.name))

	def _tiddler_path(self, tiddler):
		return "%s.tid" % os.path.join(self._root, encode(tiddler.bag),
			encode(tiddler.title))

	def _user_path(self, user):
		return "%s.user" % os.path.join(self._root, encode(user.usersign))

	def _policy_path(self, base_path):
		return os.path.join(base_path, "policy")

	def _description_path(self, base_path):
		return os.path.join(base_path, "description")


def _resolve_references(items):
	"""
	returns a list of tiddler references based on list of URIs

	each URI can point to a Cook-style recipe, tiddler or JavaScript file
	"""
	uris = []
	for item in items:
		if item.endswith(RECIPE_EXT):
			uris = uris + _expand_recipe(item)
		else:
			uris.append(item)
	return uris


def _expand_recipe(uri):
	"""
	returns list of tiddler references specified in a Cook-style recipe

	supports recursive references to other recipes
	"""
	base_dir = os.path.dirname(uri)

	lines = _read_file(uri).splitlines()
	rules = [line.rstrip() for line in lines if
		line.startswith("tiddler:") or
		line.startswith("plugin:") or
		line.startswith("recipe:")]

	uris = []
	for rule in rules:
		type, uri = rule.split(": ")
		if not uri.startswith("http") and not uri.startswith("https"):
			uri = os.path.join(base_dir, uri)
		if type == "recipe":
			uris = uris + _expand_recipe(uri)
		else:
			uris.append(uri)

	return uris


def _extract_title(uri):
	"""
	determine title from file path
	"""
	filename = uri.split("/")[-1]
	name, ext = filename.rsplit(".", 1)
	if ".%s" % ext in [TIDDLER_EXT, PLUGIN_EXT]:
		return name
	else:
		return filename


def _read_file(uri):
	if uri.startswith("file://"): # XXX: hack; use twimport's _get_url_handle!?
		uri = uri[7:]
	return read_utf8_file(uri)


def decode(name):
	return unicode(unquote(name), "utf-8")
