from textual.app import App

from trash.networker import Networker
from client.screens.connect import ConnectScreen


class Client(App):
    CSS_PATH = "./app.tcss"

    def on_mount(self):
        self.networker = Networker()
        self.push_screen(ConnectScreen())

if __name__ == '__main__':
    client = Client()
    client.run()
