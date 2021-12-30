
from channels.generic.websocket import WebsocketConsumer

class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

REGISTERED_WS_CONSUMERS = {}

class RegisteredWSConsumer(WebsocketConsumer):
    def register_key(self):
        return None
    def __new__(cls):
        ret = super().__new__(cls)
        
        key = ret.register_key()
        if key == None:
            key = -1
        ret._key = key
        
        if not cls.__name__ in REGISTERED_WS_CONSUMERS:
            REGISTERED_WS_CONSUMERS[cls.__name__] = {}
        
        if not key in REGISTERED_WS_CONSUMERS[cls.__name__]:
            REGISTERED_WS_CONSUMERS[cls.__name__][key] = set()

        REGISTERED_WS_CONSUMERS[cls.__name__][key].add(ret)
        
        return ret
    def rebuild_key(self):

        key = self.register_key()
        if key == None:
            key = -1
        
        if key != self._key:
            REGISTERED_WS_CONSUMERS[type(self).__name__][self._key].remove(self)
            self._key = key
            if not key in REGISTERED_WS_CONSUMERS[type(self).__name__]:
                REGISTERED_WS_CONSUMERS[type(self).__name__][key] = set()
            REGISTERED_WS_CONSUMERS[type(self).__name__][self._key].add(self)
            print(REGISTERED_WS_CONSUMERS)
    def disconnect(self, code):
        REGISTERED_WS_CONSUMERS[type(self).__name__][self._key].remove(self)

        return super().disconnect(code)
    def get_key_like(self):
        return REGISTERED_WS_CONSUMERS[type(self).__name__][self._key]
    def get_by_key(self, key):
        if not key in REGISTERED_WS_CONSUMERS[type(self).__name__]:
            return set()
        return REGISTERED_WS_CONSUMERS[type(self).__name__][key]
