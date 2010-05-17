"""
test module for searching the store
"""

import os

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, _cleanup



def test_basic_search_store():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], env)

	bagone = Bag('bagone')
	bagtwo = Bag('bagtwo')
	tiddler1 = Tiddler('tiddler1', 'bagone')
	tiddler2 = Tiddler('tiddler2', 'bagtwo')
	tiddler1.text = tiddler2.text = 'ohhai'
	store.put(bagone)
	store.put(bagtwo)
	store.put(tiddler1)
	store.put(tiddler2)

	tiddlers = list(store.search('ohhai'))
	assert len(tiddlers) == 2
	assert ['tiddler1', 'tiddler2'] == sorted([tiddler.title for tiddler in tiddlers])
