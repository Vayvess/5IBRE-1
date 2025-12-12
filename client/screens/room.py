from textual import on
from textual.screen import Screen

from textual.widgets import (
    Input, Button, Label, 
    Footer, Header, Static,
)

class RoomScreen(Screen):

    def compose(self):
        yield Header()
        yield Label("Room")
        yield Footer()
