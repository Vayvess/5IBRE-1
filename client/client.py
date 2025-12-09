import time
import socket
import threading
import selectors
import tkinter as tk
from queue import Queue, Empty


class Networker(threading.Thread):
    def __init__(self, msgq):
        super().__init__(daemon=True)

        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.msgq = msgq
        self.rbuff = bytearray()
        self.sbuff = bytearray()
        self.selector = selectors.DefaultSelector()
        
    
    def connect(self, host, port, username):
        self.sock.connect((host, port))
        self.selector.register(self.sock, selectors.EVENT_READ, None)

        self.username = username

    def handle_tcpread(self):
        pass

    def handle_tcpwrite(self):
        pass
    
    def run(self):
        while self.running:
            events = self.selector.select()
            for key, mask in events:
                if mask & selectors.EVENT_READ:
                    self.handle_tcpread()
                if mask & selectors.EVENT_WRITE:
                    self.handle_tcpwrite()
    
    def stop(self):
        self.running = False

class Client:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("My Tkinter App")

        self.msg_queue = Queue()
        self.networker = Networker(self.msg_queue)
    
    def on_close(self):
        pass
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
        

if __name__ == "__main__":
    client = Client()
    client.run()
