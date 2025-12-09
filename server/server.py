import json
import socket
import selectors

from session import Session
from handlers import DISPATCHER

class Server:
    def __init__(self, host, port):
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.bind((host, port))
        self.tcp_sock.setblocking(False)
        self.tcp_sock.listen()

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.tcp_sock, selectors.EVENT_READ, None)
    
    def handle_accept(self):
        try:
            sock, addr = self.tcp_sock.accept()
            print("anon connected to the server")
        except socket.error as err:
            print(err)
        else:
            sock.setblocking(False)
            sess = Session(sock)
            self.selector.register(sock, selectors.EVENT_READ, sess)
    
    def handle_disconnect(self, sess: Session):
        if sess.alive:
            sess.alive = False
            print(f"{sess.usern} disconnected from server !")
            self.selector.unregister(sess.sock)
            sess.sock.close()
    
    def handle_msg(self, sess, msg):
        msgtype = msg[0]
        handler = DISPATCHER.get(msgtype)
        if handler:
            handler(self, sess, msg)
    
    def handle_tcpread(self, sess: Session):
        try:
            data = sess.sock.recv(4096)
        except OSError as e:
            self.handle_disconnect(sess)
        
        if data:
            for msg in sess.extract(data):
                if msg != -1:
                    self.handle_msg(sess, msg)
                else:
                    self.handle_disconnect()
        else:
            self.handle_disconnect()
    
    def handle_tcpwrite(self, sess: Session):
        if not sess.alive:
            return
        
        try:
            sent = sess.sock.send(sess.sbuff)
            del sess.sbuff[:sent]
        except BlockingIOError:
            return
        except OSError:
            self.handle_disconnect(sess)
            return
        
        if len(sess.sbuff) == 0:
            self.selector.modify(sess.sock, selectors.EVENT_READ, sess)
    
    def handle_network(self, timeout=None):
        events = self.selector.select(timeout)
        for key, mask in events:
            sess = key.data
            if sess is None:
                self.handle_accept()
            else:
                if mask & selectors.EVENT_READ:
                    self.handle_tcpread(sess)
                if mask & selectors.EVENT_WRITE:
                    self.handle_tcpwrite(sess)
    
    def run(self):
        while True:
            self.handle_network()

if __name__ == '__main__':
    server = Server('', 3000)
    try:
        server.run(0)
    except KeyboardInterrupt:
        server.shutdown()
