"""
DevText Store
TiddlyWeb StorageInterface intended to ease client-side plugin development

Features:
* supports JavaScript (.js) files
* uses .tid files for non-JavaScript content
* no revisions
"""

import os
import os.path
import urllib
import codecs
import simplejson

from tiddlyweb.serializer import Serializer

from tiddlyweb.stores.text import Store as Text, _encode_filename
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User
from tiddlyweb.store import NoBagError, NoTiddlerError, StoreLockError
from tiddlyweb.util import write_lock, write_unlock


class Store(Text):

    def __init__(self, environ={}):
        self.environ = environ
        self.serializer = Serializer('text')
        store_config = self.environ['tiddlyweb.config']['server_store'][1]
        self._root = store_config['store_root']
        if not os.path.exists(self._store_root()):
            os.mkdir(self._store_root())

    def list_bags(self):
        bags = self._bag_filenames()
        return [Bag(urllib.unquote(bag).decode('utf-8')) for bag in bags]

    def list_recipes(self):
        recipes = [file.replace('.recipe', '') for file in self._files_in_dir(self._store_root())
            if file.endswith('.recipe')]
        return [Recipe(urllib.unquote(recipe).decode('utf-8')) for recipe in recipes]

    def list_users(self):
        users = [file.replace('.user', '') for file in self._files_in_dir(self._store_root())
            if file.endswith('.user')]
        return [User(urllib.unquote(user).decode('utf-8')) for user in users]

    def list_tiddler_revisions(self, tiddler):
        return [self._tiddler_revision_filename(tiddler)]

    def bag_get(self, bag):
        bag_path = self._bag_path(bag.name)
        tiddlers_dir = self._tiddlers_dir(bag.name)
        try:
            tiddlers = self._files_in_dir(tiddlers_dir)
        except OSError, exc:
            raise NoBagError('unable to list tiddlers in bag: %s' % exc)
        for filename in tiddlers:
            title = self._tiddler_title_from_file(filename)
            if title:
                bag.add_tiddler(Tiddler(title))
        bag.desc = self._read_bag_description(bag_path)
        bag.policy = self._read_policy(bag_path)
        return bag

    def _tiddler_title_from_file(self, filename):
        title = None
        if filename.endswith('.tid'):
            title = urllib.unquote(filename[:-4]).decode('utf-8')
        elif filename.endswith('.js'):
            title = urllib.unquote(filename[:-3]).decode('utf-8')
        return title

    def tiddler_put(self, tiddler):
        tiddler_base_filename = self._tiddler_base_filename(tiddler)
        if not os.path.exists(tiddler_base_filename):
            os.mkdir(tiddler_base_filename)
        locked = 0
        lock_attempts = 0
        while (not locked):
            try:
                lock_attempts = lock_attempts + 1
                write_lock(tiddler_base_filename)
                locked = 1
            except StoreLockError, exc:
                if lock_attempts > 4:
                    raise StoreLockError(exc)
                time.sleep(.1)
        revision = 1
        tiddler_filename = self._tiddler_full_filename(tiddler, revision)
        tiddler_file = codecs.open(tiddler_filename, 'w', encoding='utf-8')
        if tiddler.type and tiddler.type != 'None':
            tiddler.text = b64encode(tiddler.text)
        self.serializer.object = tiddler
        tiddler_file.write(self.serializer.to_string())
        write_unlock(tiddler_base_filename)
        tiddler.revision = revision
        tiddler_file.close()
        self.tiddler_written(tiddler)

    def tiddler_delete(self, tiddler):
        try:
            tiddler_full_filename = self._tiddler_full_filename(tiddler, 1)
            if not os.path.exists(tiddler_full_filename):
                raise NoTiddlerError('%s not present' % tiddler_full_filename)
            os.unlink(tiddler_full_filename)
        except NoTiddlerError:
            raise
        except Exception, exc:
            raise IOError('unable to delete %s: %s' % (tiddler.title, exc))

    def search(self, search_query):
        """
        Search in the store for tiddlers that match search_query.
        This is intentionally simple, slow and broken to encourage overriding.
        """
        bag_filenames = self._bag_filenames()
        found_tiddlers = []

        query = search_query.lower()

        for bagname in bag_filenames:
            bagname = urllib.unquote(bagname).decode('utf-8')
            tiddler_dir = self._tiddlers_dir(bagname)
            tiddler_files = self._files_in_dir(tiddler_dir)
            for tiddler_name in (self._tiddler_title_from_file(filename) for filename in tiddler_files):
                tiddler = Tiddler(tiddler_name, bagname)
                try:
                    revision_id = self.list_tiddler_revisions(tiddler)[0]
                    if query in tiddler.title.lower():
                        found_tiddlers.append(tiddler)
                        continue
                    tiddler_file = codecs.open(
                        self._tiddler_full_filename(tiddler, revision_id),
                        encoding='utf-8')
                    for line in tiddler_file:
                        if query in line.lower():
                            found_tiddlers.append(tiddler)
                            break
                except (OSError, NoTiddlerError), exc:
                    logging.warn('malformed tiddler during search: %s:%s' %
                            (bagname, tiddler_name))
        return found_tiddlers

    def _bag_filenames(self):
        """
        List the filenames that are bags.
        """
        return self._dirs_in_dir(self._store_root())

    def _bag_path(self, bag_name):
        try:
            return os.path.join(self._store_root(), _encode_filename(bag_name))
        except (AttributeError, StoreEncodingError), exc:
            raise NoBagError('No bag name: %s' % exc)

    def _recipe_path(self, recipe):
        return os.path.join(self._store_root(), _encode_filename(recipe.name) + '.recipe')

    def _user_path(self, user):
        return os.path.join(self._store_root(), user.usersign + '.user')

    def _tiddlers_dir(self, bag_name):
        return self._bag_path(bag_name)

    def _tiddler_base_filename(self, tiddler):
        bag_name = tiddler.bag
        store_dir = self._tiddlers_dir(bag_name)
        if not os.path.exists(store_dir):
            raise NoBagError('%s does not exist' % store_dir)
        try:
            return store_dir
        except StoreEncodingError, exc:
            raise NoTiddlerError(exc)

    def _tiddler_full_filename(self, tiddler, revision):
        return os.path.join(self._tiddlers_dir(tiddler.bag),
            '%s.tid' % _encode_filename(tiddler.title))

    def _tiddler_revision_filename(self, tiddler, index=0):
        return 1

    def _read_tiddler_file(self, tiddler, tiddler_filename):
        try:
            tiddler_file = codecs.open(tiddler_filename, encoding='utf-8')
        except IOError:
            tiddler_filename = tiddler_filename.replace('.tid', '.js')
            tiddler_file = codecs.open(tiddler_filename, encoding='utf-8')
        tiddler_string = tiddler_file.read()
        tiddler_file.close()
        if tiddler_filename.endswith('.js'):
            header = 'tags: systemConfig'
            notice = '/***\n> source: {{{%s}}}\n***/' % tiddler_filename
            tiddler_string = '%s\n\n%s\n%s' % (header, notice, tiddler_string)
        self.serializer.object = tiddler
        tiddler = self.serializer.from_string(tiddler_string)
        return tiddler

    def _read_policy(self, bag_path):
        policy_filename = os.path.join(bag_path, 'policy')
        try:
            policy_file = codecs.open(policy_filename, encoding='utf-8')
            policy = policy_file.read()
            policy_file.close()
            policy_data = simplejson.loads(policy)
            policy = Policy()
            for key, value in policy_data.items():
                policy.__setattr__(key, value)
        except IOError:
            policy = Policy()
        return policy

    def _dirs_in_dir(self, path):
        return [dir for dir in self._files_in_dir(path) if os.path.isdir(os.path.join(path, dir))]

    def _files_in_dir(self, path):
        return [x for x in os.listdir(path) if
            not x.startswith('.') and not x == 'policy' and not x == 'description']
