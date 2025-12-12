from textual import (
    events, on
)

from textual.screen import Screen
from textual.containers import Vertical

from textual.widgets import (
    Input, Button, Label, 
    Footer, Header, Static,
)


from client.screens.room import RoomScreen


class ConnectScreen(Screen):

    def compose(self):
        yield Header()
        with Vertical(id="connect_layout"):
            yield Label(
                content="Connect to [bold red]Server[/bold red]",
                id="title"
            )
            yield Input(
                value="localhost",
                placeholder="address",
                id="address"
            )

            yield Input(
                value="3000",
                placeholder="port",
                id="port"
            )

            yield Button(
                label="Connect", 
                id="btn_connect"
            )
        yield Footer()
    
    @on(Button.Pressed, "#btn_connect")
    def connect(self, event):
        addr = self.query_one("#address", Input).value.strip()
        port = self.query_one("#port", Input).value.strip()

        try:
            port = int(port)
        except ValueError:
            self.app.notify(
                "Port must be a number.",
                severity="error"
            )
            return
        
        self.app.notify(
            "Connecting attempt...",
            severity="information"
        )
        
        ok = self.app.networker.connect(addr, port)

        if ok:
            self.app.notify(
                f"Connected to {addr} on port {port}",
                severity="success"
            )
            self.app.push_screen(RoomScreen())
        else:
            self.app.notify("Connection failed...", severity="error")
