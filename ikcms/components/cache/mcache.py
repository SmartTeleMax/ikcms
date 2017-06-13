import memcache
from . import base


class Component(base.Component):

    DEFAULT_MEMCACHE = '127.0.0.1:11211'
    prefix = b''

    def __init__(self, app, client):
        super(Component, self).__init__(app)
        self.client = client

    @classmethod
    def create(cls, app):
        url = getattr(app.cfg, 'MEMCACHE', cls.DEFAULT_MEMCACHE)
        return cls(app, client=memcache.Client(url))

    def get(self, key):
        return self.client.get(self._key(key))

    def set(self, key, value, expire=0):
        return self.client.set(self._key(key), value, time=expire)

    def delete(self, key):
        return self.client.delete(self._key(key))

    def _key(self, key):
        return self.prefix + key


component = Component.create_cls