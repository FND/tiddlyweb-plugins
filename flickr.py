"""
Flickr Store
TiddlyWeb StorageInterface interfacing with Flickr

Tiddler Mapping:
* bag ~ user
* title ~ ID
* created ~ date uploaded
* tags ~ tags
* text ~ description

To Do:
* cache tiddlers when generating bag
"""

import urllib2
import logging

import simplejson

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.stores import StorageInterface


class Store(StorageInterface):

	def __init__(self, environ=None):
		super(Store, self).__init__(environ)

	def list_bags(self):
		logging.debug("listing bag: %s" % bag.name)
		raise NotImplementedError("list of bags not available") # TODO?

	def list_tiddlers(self):
		logging.debug("listing bag: %s" % bag.name)
		raise NotImplementedError("list of bags not available") # TODO?

	def bag_get(self, bag):
		logging.debug("retrieving bag: %s" % bag.name)

		bag.desc = None # TODO
		#bag.policy = None # TODO

		if not (hasattr(bag, "skinny") and bag.skinny):
			for photo in _get_photos(bag.name):
				tiddler = Tiddler(photo["id"])
				tiddler = _populate_tiddler(tiddler)
				bag.add_tiddler(tiddler)

		return bag

	def tiddler_get(self, tiddler):
		logging.debug("retrieving tiddler %s from %s" % (tiddler.title, tiddler.bag))
		tiddler = _populate_tiddler(tiddler)
		img = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (
			tiddler.fields["flickr.farm"], tiddler.fields["flickr.server"],
			tiddler.title, tiddler.fields["flickr.secret"])
		link = "http://www.flickr.com/photos/%s/%s/" % (tiddler.bag, tiddler.title)
		label = tiddler.fields["flickr.caption"]
		tiddler.text += "\n\n[img[%s|%s][%s]]" % (label, img, link) # XXX: for demo purposes only
		return tiddler


def _get_photos(user_id):
	uri_template = "http://query.yahooapis.com/v1/public/yql?q=SELECT%20id%20FROM%20flickr.photos.search%20WHERE%20user_id%3D%22%s%22%20AND%20ispublic%3D%221%22&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env"
	uri = uri_template.replace("%s", urllib2.quote(user_id)) # N.B.: regular string substitution does not work well with URL-encoded strings
	data = urllib2.urlopen(uri)
	data = simplejson.loads(data.read())
	return data["query"]["results"]["photo"]


def _get_photo(id):
	uri_template = "http://query.yahooapis.com/v1/public/yql?q=SELECT%20title%2C%20dateuploaded%2C%20description%2C%20tags%2C%20license%2C%20farm%2C%20server%2C%20secret%20FROM%20flickr.photos.info%20WHERE%20photo_id%3D%22%s%22&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env"
	uri = uri_template.replace("%s", urllib2.quote(id)) # N.B.: regular string substitution does not work well with URL-encoded strings
	data = urllib2.urlopen(uri)
	data = simplejson.loads(data.read())
	photo = data["query"]["results"]["photo"]
	 # TODO: convert dateuploaded to date object, resolve license, store source URI
	tags = []
	try:
		for tag in photo["tags"]["tag"]:
			tags.append(tag["content"])
	except TypeError: # XXX: not quite sure why this fails sometimes
		pass
	photo["tags"] = tags
	return photo


def _populate_tiddler(tiddler):
	photo = _get_photo(tiddler.title)
	tiddler.created = photo["dateuploaded"] # TODO: convert to tiddly timestamp
	tiddler.text = photo["description"] or ""
	tiddler.tags = photo["tags"]
	tiddler.fields["flickr.caption"] = photo["title"]
	tiddler.fields["flickr.farm"] = photo["farm"]
	tiddler.fields["flickr.server"] = photo["server"]
	tiddler.fields["flickr.secret"] = photo["secret"]
	tiddler.fields["flickr.license"] = photo["license"]
	return tiddler
