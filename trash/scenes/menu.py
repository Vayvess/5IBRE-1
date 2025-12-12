from trash.scenes.scene import *

class SceneMenu(SceneBase):
    def __init__(self, client):
        super().__init__(client)

        # UI
        resx, resy = self.client.BASE_RES
        text_width = 256
        text_height = 64
        center_x = resx // 2
        center_y = resy // 2

        # TEXTLABEL: WELCOME MESSAGE
        self.label_welcome = ui.elements.UILabel(
            pg.Rect(
                center_x - (text_width // 2),
                center_y - 128,
                text_width, text_height
            ),
            "ChatPristi",
            object_id="#test"
        )

        # TEXTENTRY: SERVER ADDRESS
        self.textentry_addr = ui.elements.UITextEntryLine(
            pg.Rect(
                center_x - (text_width // 2),
                center_y - 48,
                text_width, text_height
            ),
            client.manui,
            initial_text="localhost:3000",
            placeholder_text="IP:PORT",
        )

        # BUTTON: CONNECT TO SERVER
        self.btn_connect = ui.elements.UIButton(
            pg.Rect(
                center_x - (text_width // 2),
                center_y + 48,
                text_width, text_height
            ),
            "Connect",
            client.manui
        )
    
    def try_connect(self):
        addr_text = self.textentry_addr.get_text()

        try:
            addr, port = addr_text.split(':')
            addr = addr.strip()
            port = int(port.strip())
        except Exception as e:
            return
        else:
            if self.client.connect(addr, port):
                self.client.load_scene('room')
            else:
                pass

    def process_event(self, event):
        if event.type == ui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_connect:
                self.try_connect()
        
        elif event.type == ui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.textentry_addr:
                self.try_connect()
    
    def handle_tcpmsg(self, msg):
        print(msg)
    
    def update(self, dt):
        pass

    def render(self, canvas):
        pass
