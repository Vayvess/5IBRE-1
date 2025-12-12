import pygame as pg
import pygame_gui as ui

from trash.networker import Networker
from trash.scenes.menu import SceneMenu
from trash.scenes.room import SceneRoom


class Client:
    BASE_RES = (1280, 720)

    def __init__(self):
        # NETWORKING
        self.connected = False
        self.networker = None

        # RENDERING
        self.curr_res = Client.BASE_RES
        self.canvas = pg.Surface(Client.BASE_RES)
        self.display = pg.display.set_mode(self.curr_res)
        pg.display.set_caption("Sandbox")

        self.manui = ui.UIManager(Client.BASE_RES)
        self.manui.add_font_paths(
            "Roboto",
            "./trash/assets/Roboto-Regular.ttf"
        )

        theme = self.manui.get_theme()
        theme.load_theme("./trash/assets/theme.json")

        # SCENE MANAGEMENT
        self.scene = SceneMenu(self)
        self.next_scene = None
        self.loadable_scene = {
            "menu": SceneMenu,
            "room": SceneRoom,
        }
    
    def load_scene(self, scene_name, *args):
        if self.next_scene is None:
            scene_class = self.loadable_scene.get(scene_name)
            if scene_class:
                self.next_scene = (scene_class, args)
    
    def get_scene(self):
        if self.next_scene:
            self.scene.dispose()
            self.manui.clear_and_reset()

            scene_class, args = self.next_scene
            self.scene = scene_class(self, *args)
            self.next_scene = None
        
        return self.scene
    
    def connect(self, addr, port):
        if self.connected:
            return True
        
        if self.networker is None:
            self.networker = Networker()
        
        connected = self.networker.connect(addr, port)
        if connected:
            self.connected = True
            self.networker.start()
        
        return connected
    
    def send_tcpmsg(self, msg):
        self.networker.send_tcpmsg(msg)
    
    def handle_network(self):
        for tcpmsg in self.networker.drain_incoming(8):
            self.scene.handle_tcpmsg(tcpmsg)
    
    def run(self):
        running = True
        clock = pg.time.Clock()

        ORIGIN = (0, 0)
        BLACK = (0, 0, 0)

        while running:
            scene = self.get_scene()
            dt = clock.tick(30) / 1000.0
            
            # EVENT HANDLING
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                
                scene.process_event(event)
                self.manui.process_events(event)
            
            # UPDATING
            scene.update(dt)
            self.manui.update(dt)
            
            # RENDERING
            self.canvas.fill(BLACK)
            self.scene.render(self.canvas)
            self.manui.draw_ui(self.canvas)

            scaled = pg.transform.scale(self.canvas, self.curr_res)
            self.display.blit(scaled, ORIGIN)
            pg.display.flip()

            # NETWORKING
            if self.connected:
                self.handle_network()
    
    def stop(self):
        pass

if __name__ == '__main__':
    pg.init()
    client = Client()
    client.run()
    client.stop()
    pg.quit()
