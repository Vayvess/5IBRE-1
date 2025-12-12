from trash.scenes.scene import *

class SceneRoom(SceneBase):
    def __init__(self, client):
        super().__init__(client)

        resx, resy = self.client.BASE_RES

        center_x = resx // 2
        center_y = resy // 2
        manager = client.manui

        MARGIN = 16
        INPUT_HEIGHT = 48
        INPUT_WIDTH = center_x
        self.textentryline_msg = ui.elements.UITextEntryLine(
            pg.Rect(
                resx // 2 - INPUT_WIDTH // 2,
                resy - INPUT_HEIGHT - MARGIN,
                INPUT_WIDTH, INPUT_HEIGHT
            ),
            manager=manager,
            object_id='#message_input'
        )

        LOG_WIDTH = resx - (MARGIN * 2)
        LOG_HEIGHT = resy - INPUT_HEIGHT - (MARGIN * 3)
        self.message_log_container = ui.elements.UIScrollingContainer(
            pg.Rect(MARGIN, MARGIN, LOG_WIDTH, LOG_HEIGHT),
            manager=manager,
            should_grow_automatically=True,
            allow_scroll_x=False
        )
        
        self.next_message_y_pos = 0
        self.message_height = 48
        self.add_message_to_log("System: Welcome to the room!")
    
    def format_msg(self, msg):
        z = 1
        arr = []
        for x, v in enumerate(msg, 1):
            if x % 64 == 0:
                arr.append("\n")
                z += 1
            arr.append(v)
        
        return ''.join(arr), z * self.message_height

    def add_message_to_log(self, msg):
        """Dynamically adds a new message label to the scrollable container."""

        msg, msg_y = self.format_msg(msg)

        # Create the label inside the scrolling container
        msg_label = ui.elements.UILabel(
            pg.Rect(
                0, self.next_message_y_pos, 
                len(msg) * 32, msg_y
            ),
            msg,
            self.client.manui,
            self.message_log_container,
            object_id='#chat_message'
        )

        # Update position for the next message
        self.next_message_y_pos += msg_y

        # Force the container to scroll to the bottom to show the newest message
        # self.message_log_container. # 1.0 = scroll to bottom

    def process_event(self, event):
        # Pass the event to the UI manager (handled in the client's main loop usually)
        # We only need to check for specific UI events we care about
        
        if event.type == pg.USEREVENT:
            if event.user_type == ui.UI_BUTTON_PRESSED:
                pass
            
            # Handle Enter/Return key press in the text input
            if event.user_type == ui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == self.textentryline_msg:
                    self._send_message()

    def _send_message(self):
        """Logic to get the text, display it, and clear the input."""
        message = self.textentryline_msg.get_text().strip()
        
        if message:
            # 1. Add the sent message to the log (for immediate feedback)
            self.add_message_to_log(f"You: {message}")
            
            # 2. **Actual sending logic goes here** (e.g., self.client.send_tcp_message(message))
            # ... 
            
            # 3. Clear the input field
            self.textentryline_msg.set_text('')

    def handle_tcpmsg(self, msg):
        """Called when a message is received over the network."""
        
        # Assuming 'msg' is the formatted string you want to display, e.g., "User: Hello!"
        self.add_message_to_log(msg)
    
    def update(self, dt):
        # Update is handled by the client's main loop and manager.update(dt)
        pass

    def render(self, canvas):
        # Draw background color (optional)
        canvas.fill(pg.Color('#202020'))
        # UI rendering is handled by the client's main loop and manager.draw_ui(canvas)

    def dispose(self):
        # Clean up UI elements when the scene is closed to prevent memory leaks
        self.textentryline_msg.kill()
        self.button_send.kill()
        self.message_log_container.kill()