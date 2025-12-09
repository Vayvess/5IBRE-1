import json

class Session:
    def __init__(self, sock):
        self.sock = sock
        self.rbuff = bytearray()
        self.sbuff = bytearray()
        self.alive = True
    
    def extract(self, data):
        a = 0
        self.rbuff.extend(data)
        view = memoryview(self.rbuff)

        while True:
            n = int.from_bytes(view[a:a + 2], 'big')
            b = a + 2 + n

            if b > len(view):
                self.rbuff = bytearray(view[a:])
                return None
            
            msg = view[a + 2:b].tobytes()
            a = b

            try:
                msg = json.loads(msg)
                yield msg
            except json.JSONDecodeError:
                yield -1
                return None
