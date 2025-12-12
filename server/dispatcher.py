from shared.constants import TcpMsg

# REQUEST HANDLERS
def room_join(server, sess, msg):
    server.send_tcpmsg(sess, {
        TcpMsg.TYPE: TcpMsg.ROOM_JOINED,
        TcpMsg.STATUS: True
    })

class Dispatcher:
    def __init__(self, server):
        self.server = server
        self.handlers = {
            TcpMsg.ROOM_JOIN: room_join
        }
    
    def dispatch(self, sess, msg):
        msgtype = msg.get(TcpMsg.TYPE)
        if msgtype is None:
            return
        
        handler = self.handlers.get(msgtype)
        if handler:
            handler(self.server, sess, msg)
