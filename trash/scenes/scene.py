import time
import pygame as pg
import pygame_gui as ui

from shared.constants import TcpMsg

class SceneBase:
    def __init__(self, client):
        self.client = client
    
    def process_event(self, event):
        pass

    def handle_tcpmsg(self, msg):
        pass
    
    def update(self, dt):
        pass

    def render(self, canvas):
        pass

    def dispose(self):
        pass
