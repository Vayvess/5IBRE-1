from textual import on
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import (
    Input, Button, Label, Footer, Header, Static
)

class SplashScreen(Screen):
    def __init__(self, error):
        super().__init__()
        self.error = error
    
    def compose(self):
        yield Header()
        with Vertical(id="splash_layout"):
            yield Label(
                content=self.error
            )
            yield Button(
                label="Back",
                id="go_back"
            )
        yield Footer()
    
    @on(Button.Pressed, "#go_back")
    def go_back(self, event):
        self.dismiss()
