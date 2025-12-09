import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox, simpledialog
import json
import time

class SimpleChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Chat - Client")
        self.root.geometry("1200x700")
        self.root.configure(bg="#121212")
        
        # Variables d'état
        self.connected = False
        self.username = ""
        
        # Données locales
        self.channels = ["général"]
        self.current_channel = "général"
        self.messages = {}
        self.users = {}
        
        # Palette de couleurs
        self.colors = {
            "bg_dark": "#121212",
            "bg_panel": "#1e1e1e",
            "bg_input": "#252525",
            "primary": "#4a9eff",
            "primary_dark": "#3a7ccc",
            "text_primary": "#ffffff",
            "text_secondary": "#b0b0b0",
            "border": "#333333",
            "success": "#51cf66",
            "error": "#ff6b6b",
            "warning": "#fbbf24"
        }
        
        # Polices
        try:
            self.fonts = {
                "heading": font.Font(family="Segoe UI", size=20, weight="bold"),
                "body": font.Font(family="Segoe UI", size=12),
                "small": font.Font(family="Segoe UI", size=11),
                "body_bold": font.Font(family="Segoe UI", size=12, weight="bold")
            }
        except Exception:
            self.fonts = {
                "heading": font.Font(family="Arial", size=20, weight="bold"),
                "body": font.Font(family="Arial", size=12),
                "small": font.Font(family="Arial", size=11),
                "body_bold": font.Font(family="Arial", size=12, weight="bold")
            }
        
        # Référence WebSocket
        self.ws = None
        
        # Création de l'interface
        self.create_interface()
        self.setup_shortcuts()
        
        # Initialiser les données
        for channel in self.channels:
            self.messages[channel] = []
            self.users[channel] = []
        
        # Message de bienvenue
        self.add_system_message("Connectez-vous pour commencer à discuter.")
        
    def create_interface(self):
        """Crée l'interface utilisateur"""
        main_frame = tk.Frame(self.root, bg=self.colors["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panneau de connexion
        self.connection_frame = tk.Frame(main_frame, bg=self.colors["bg_panel"], width=300)
        self.connection_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.connection_frame.pack_propagate(False)
        self.create_connection_panel()
        
        # Interface de chat
        self.chat_frame = tk.Frame(main_frame, bg=self.colors["bg_dark"])
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
        self.create_chat_panel()
        
    def create_connection_panel(self):
        """Crée le panneau de connexion"""
        content_frame = tk.Frame(self.connection_frame, bg=self.colors["bg_panel"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Titre
        tk.Label(content_frame, text="Connexion", 
                font=self.fonts["heading"],
                fg=self.colors["text_primary"],
                bg=self.colors["bg_panel"]).pack(anchor=tk.W, pady=(0, 30))
        
        # Champ serveur
        tk.Label(content_frame, text="Serveur (host:port)",
                font=self.fonts["small"],
                fg=self.colors["text_secondary"],
                bg=self.colors["bg_panel"]).pack(anchor=tk.W, pady=(0, 5))
        
        self.server_entry = tk.Entry(content_frame,
                                    bg=self.colors["bg_input"],
                                    fg=self.colors["text_primary"],
                                    insertbackground=self.colors["text_primary"],
                                    font=self.fonts["body"],
                                    relief=tk.FLAT)
        self.server_entry.pack(fill=tk.X, pady=(0, 15))
        self.server_entry.insert(0, "localhost:8080")
        
        # Champ username
        tk.Label(content_frame, text="Nom d'utilisateur",
                font=self.fonts["small"],
                fg=self.colors["text_secondary"],
                bg=self.colors["bg_panel"]).pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = tk.Entry(content_frame,
                                      bg=self.colors["bg_input"],
                                      fg=self.colors["text_primary"],
                                      insertbackground=self.colors["text_primary"],
                                      font=self.fonts["body"],
                                      relief=tk.FLAT)
        self.username_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Boutons
        self.connect_button = tk.Button(
            content_frame,
            text="Se connecter",
            font=self.fonts["body"],
            fg=self.colors["text_primary"],
            bg=self.colors["primary"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            command=self.on_connect_clicked,
            height=2
        )
        self.connect_button.pack(fill=tk.X, pady=(0, 10))
        
        self.disconnect_button = tk.Button(
            content_frame,
            text="Déconnecter",
            font=self.fonts["body"],
            fg=self.colors["text_primary"],
            bg="#555555",
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            command=self.on_disconnect_clicked,
            height=2,
            state=tk.DISABLED
        )
        self.disconnect_button.pack(fill=tk.X)
        
        # Statut
        self.status_label = tk.Label(content_frame,
                                    text="🔴 Déconnecté",
                                    font=self.fonts["small"],
                                    fg=self.colors["error"],
                                    bg=self.colors["bg_panel"])
        self.status_label.pack(anchor=tk.W, pady=(30, 0))
        
        # Séparateur
        tk.Frame(content_frame, bg=self.colors["border"], height=1).pack(fill=tk.X, pady=30)
        
        # Instructions
        tk.Label(content_frame, text="Instructions :\n1. Entrez vos infos\n2. Cliquez connecter\n3. Écrivez et envoyez",
                font=self.fonts["small"],
                fg=self.colors["text_secondary"],
                bg=self.colors["bg_panel"],
                justify=tk.LEFT).pack(anchor=tk.W)
        
    def create_chat_panel(self):
        """Crée le panneau de chat"""
        # Barre des salons
        channels_frame = tk.Frame(self.chat_frame, bg=self.colors["bg_panel"], height=50)
        channels_frame.pack(fill=tk.X, pady=(0, 10))
        channels_frame.pack_propagate(False)
        
        tk.Label(channels_frame, text="Salons:", 
                font=self.fonts["small"],
                fg=self.colors["text_secondary"],
                bg=self.colors["bg_panel"]).pack(side=tk.LEFT, padx=20)
        
        # Frame pour les boutons de salons
        self.channels_buttons_frame = tk.Frame(channels_frame, bg=self.colors["bg_panel"])
        self.channels_buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bouton salon général
        self.general_channel_btn = tk.Button(
            self.channels_buttons_frame,
            text="# général",
            font=self.fonts["small"],
            fg=self.colors["text_primary"],
            bg=self.colors["bg_panel"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            command=lambda: self.switch_channel("général")
        )
        self.general_channel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton créer salon
        self.create_channel_btn = tk.Button(
            channels_frame,
            text="+ Nouveau salon",
            font=self.fonts["small"],
            fg=self.colors["text_primary"],
            bg=self.colors["primary"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            command=self.create_channel,
            state=tk.DISABLED
        )
        self.create_channel_btn.pack(side=tk.RIGHT, padx=20)
        
        # En-tête
        header_frame = tk.Frame(self.chat_frame, bg=self.colors["bg_panel"], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        self.channel_title = tk.Label(header_frame, text="# général", 
                                     font=self.fonts["heading"],
                                     fg=self.colors["text_primary"],
                                     bg=self.colors["bg_panel"])
        self.channel_title.pack(side=tk.LEFT, padx=30)
        
        # Zone messages
        messages_frame = tk.Frame(self.chat_frame, bg=self.colors["bg_dark"])
        messages_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.message_display = scrolledtext.ScrolledText(
            messages_frame,
            wrap=tk.WORD,
            bg=self.colors["bg_input"],
            fg=self.colors["text_primary"],
            font=self.fonts["body"],
            insertbackground=self.colors["text_primary"],
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            padx=20,
            pady=20,
            state=tk.DISABLED
        )
        self.message_display.pack(fill=tk.BOTH, expand=True)
        
        # Tags pour le texte
        self.setup_text_tags()
        
        # Zone de saisie
        self.create_input_area()
        
    def create_input_area(self):
        """Crée la zone de saisie"""
        input_frame = tk.Frame(self.chat_frame, bg=self.colors["bg_dark"], height=140)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        input_frame.pack_propagate(False)
        
        # Zone texte
        text_frame = tk.Frame(input_frame, bg=self.colors["bg_input"])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.message_input = tk.Text(
            text_frame,
            bg=self.colors["bg_input"],
            fg=self.colors["text_primary"],
            font=self.fonts["body"],
            height=3,
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT,
            insertbackground=self.colors["text_primary"],
            padx=15,
            pady=10
        )
        
        input_scrollbar = ttk.Scrollbar(text_frame, command=self.message_input.yview)
        self.message_input.configure(yscrollcommand=input_scrollbar.set)
        
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Gestion Entrée
        self.message_input.bind("<Return>", self.on_enter_pressed)
        self.message_input.bind("<Shift-Return>", lambda e: None)
       
    def setup_text_tags(self):
        """Configure les tags de texte"""
        self.message_display.tag_configure("system",
                                          foreground=self.colors["text_secondary"],
                                          font=self.fonts["small"])
        self.message_display.tag_configure("username",
                                          foreground=self.colors["primary"],
                                          font=self.fonts["body_bold"])
        
    def setup_shortcuts(self):
        """Configure les raccourcis"""
        self.root.bind("<Control-Return>", lambda e: self.send_message())
        
    # ============================================================================
    # 🎯 MÉTHODES PRINCIPALES - DOCUMENTATION POUR LE BACKEND
    # ============================================================================
    
    def on_connect_clicked(self):
        """
        ==================== POINT D'INTÉGRATION 1: Connexion WebSocket ====================
        
        DEVOIR DU BACKEND :
        1. Implémenter la connexion WebSocket réelle
        2. Gérer les erreurs de connexion (serveur indisponible, timeout, etc.)
        3. Maintenir la connexion ouverte
        4. Gérer la réception asynchrone des messages
        
        POURQUOI C'EST IMPORTANT :
        - C'est le point d'entrée principal de l'application
        - Toutes les communications passent par cette connexion
        - Doit être asynchrone pour ne pas bloquer l'interface
        
        ÉTAPES À SUIVRE :
        1. Récupérer host:port du champ server_entry
        2. Établir connexion WebSocket (websockets library en Python)
        3. Envoyer message d'authentification avec username
        4. Attendre confirmation du serveur
        5. Mettre à jour l'état UI
        """
        server = self.server_entry.get().strip()
        username = self.username_entry.get().strip()
        
        if not server or not username:
            messagebox.showerror("Erreur", "Remplissez tous les champs")
            return
        
        # ⚠️ SIMULATION À REMPLACER PAR LE BACKEND ⚠️
        print("⚠️  BACKEND À IMPLÉMENTER : Connexion WebSocket réelle")
        print(f"   Host: {server}")
        print(f"   Username: {username}")
        print("   Devrait établir une connexion WebSocket à ws://{host}:{port}/chat")
        
        self.username = username
        self.status_label.config(text="Connexion...", fg=self.colors["warning"])
        self.connect_button.config(state=tk.DISABLED)
        
        # Simuler succès après 1s (À SUPPRIMER)
        self.root.after(1000, self.on_connection_success)
        
    def on_connection_success(self):
        """Appelé quand connexion réussie"""
        self.connected = True
        
        # UI updates
        self.status_label.config(text="🟢 Connecté", fg=self.colors["success"])
        self.connect_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.NORMAL, bg=self.colors["error"])
        self.create_channel_btn.config(state=tk.NORMAL)
        
        # Message système
        self.add_system_message(f"Connecté en tant que {self.username}")
        
    def on_connection_error(self, error_msg):
        """Appelé en cas d'erreur"""
        self.status_label.config(text=f"Erreur: {error_msg}", fg=self.colors["error"])
        self.connect_button.config(state=tk.NORMAL)
        messagebox.showerror("Erreur", f"Échec connexion: {error_msg}")
        
    def on_disconnect_clicked(self):
        """
        ==================== POINT D'INTÉGRATION 2: Déconnexion ====================
        
        DEVOIR DU BACKEND :
        1. Fermer proprement la connexion WebSocket
        2. Envoyer message de déconnexion au serveur
        3. Nettoyer les ressources
        4. Gérer les déconnexions forcées (internet perdu)
        
        POURQUOI C'EST IMPORTANT :
        - Éviter les fuites de mémoire
        - Informer le serveur de la déconnexion
        - Permettre reconnexion propre
        """
        # ⚠️ SIMULATION À REMPLACER PAR LE BACKEND ⚠️
        print("⚠️  BACKEND À IMPLÉMENTER : Fermeture WebSocket réelle")
        print("   Devrait fermer la connexion et envoyer 'disconnect' au serveur")
        
        self.connected = False
        
        # UI updates
        self.status_label.config(text="🔴 Déconnecté", fg=self.colors["error"])
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED, bg="#555555")
        self.create_channel_btn.config(state=tk.DISABLED)
        
        # Message système
        self.add_system_message("Déconnecté")
        
    def send_message(self):
        """
        ==================== POINT D'INTÉGRATION 3: Envoi message ====================
        
        DEVOIR DU BACKEND :
        1. Envoyer le message via WebSocket
        2. Formater le message selon le protocole JSON défini
        3. Gérer les erreurs d'envoi (connexion perdue)
        4. Attendre l'accusé de réception du serveur
        
        STRUCTURE JSON REQUISE :
        {
            "action": "send_message",
            "channel": "nom_du_salon",
            "username": "nom_utilisateur",
            "message": "texte_du_message",
            "timestamp": 1234567890.123
        }
        
        POURQUOI C'EST IMPORTANT :
        - C'est la fonctionnalité principale du chat
        - Doit être fiable (TCP garantit la livraison)
        - Doit être asynchrone (ne pas bloquer l'UI)
        """
        if not self.connected:
            messagebox.showwarning("Erreur", "Connectez-vous d'abord")
            return
        
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # ⚠️ SIMULATION À REMPLACER PAR LE BACKEND ⚠️
        print("⚠️  BACKEND À IMPLÉMENTER : Envoi WebSocket réel")
        
        # Format JSON qui DOIT être envoyé via WebSocket
        json_data = {
            'action': 'send_message',
            'channel': self.current_channel,
            'username': self.username,
            'message': message,
            'timestamp': time.time()
        }
        
        print("📤 JSON à envoyer via WebSocket:")
        print(json.dumps(json_data, indent=2))
        print("   Méthode: ws.send(json.dumps(data))")
        
        # Effacer champ
        self.message_input.delete("1.0", tk.END)
        
        # ⚠️ SIMULATION : À SUPPRIMER quand le backend est implémenté
        # Cette partie simule la réception d'un message (serveur echo)
        self.root.after(500, lambda: self.handle_network_message(json.dumps({
            "type": "message",
            "data": {
                "channel": self.current_channel,
                "username": self.username,
                "message": message,
                "timestamp": time.time()
            }
        })))
        
    def create_channel(self):
        """
        ==================== POINT D'INTÉGRATION 4: Création salon ====================
        
        DEVOIR DU BACKEND :
        1. Envoyer requête de création de salon
        2. Attendre confirmation du serveur
        3. Mettre à jour la liste des salons localement
        4. Gérer les erreurs (nom existant, permissions)
        
        STRUCTURE JSON REQUISE :
        {
            "action": "create_channel",
            "channel_name": "nom_du_salon",
            "username": "nom_utilisateur"
        }
        
        RÉPONSE ATTENDUE DU SERVEUR :
        {
            "type": "channel_created",
            "data": {
                "channel_name": "nom_du_salon",
                "users": ["user1", "user2"]
            }
        }
        """
        if not self.connected:
            messagebox.showwarning("Erreur", "Connectez-vous d'abord")
            return
        
        channel_name = simpledialog.askstring("Nouveau salon", "Nom du salon:")
        if not channel_name:
            return
        
        # ⚠️ SIMULATION À REMPLACER PAR LE BACKEND ⚠️
        print(f"⚠️  BACKEND À IMPLÉMENTER : Création salon '{channel_name}'")
        
        # Format JSON qui DOIT être envoyé via WebSocket
        json_data = {
            'action': 'create_channel',
            'channel_name': channel_name,
            'username': self.username
        }
        
        print("📤 JSON à envoyer via WebSocket:")
        print(json.dumps(json_data, indent=2))
        print("   Attendre réponse du serveur avec confirmation")
        
        # ⚠️ SIMULATION : À SUPPRIMER
        if channel_name not in self.channels:
            self.channels.append(channel_name)
            
            # Créer bouton pour le nouveau salon
            btn = tk.Button(
                self.channels_buttons_frame,
                text=f"# {channel_name}",
                font=self.fonts["small"],
                fg=self.colors["primary"],
                bg=self.colors["bg_panel"],
                relief=tk.FLAT,
                borderwidth=0,
                cursor="hand2",
                command=lambda c=channel_name: self.switch_channel(c)
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Initialiser données
            self.messages[channel_name] = []
            self.users[channel_name] = []
            
            self.add_system_message(f"Salon '{channel_name}' créé")
            
    def handle_network_message(self, json_data):
        """
        ==================== POINT D'INTÉGRATION 5: Réception messages ====================
        
        DEVOIR DU BACKEND :
        1. Écouter en permanence les messages WebSocket
        2. Parser les messages JSON reçus
        3. Déléguer au bon gestionnaire selon le type
        4. Gérer les erreurs de parsing
        
        TYPES DE MESSAGES ATTENDUS :
        1. "message" : Message d'un utilisateur
        2. "channel_list" : Liste mise à jour des salons
        3. "user_list" : Liste mise à jour des utilisateurs dans un salon
        4. "system" : Message système (connexion/déconnexion)
        5. "error" : Message d'erreur du serveur
        
        EXEMPLE DE STRUCTURE :
        {
            "type": "message",
            "data": {
                "channel": "général",
                "username": "Alice",
                "message": "Bonjour !",
                "timestamp": 1234567890.123
            }
        }
        """
        try:
            data = json.loads(json_data)
            msg_type = data.get("type")
            msg_data = data.get("data", {})
            
            print(f"📨 Message reçu du serveur: {msg_type}")
            
            # Router vers le bon gestionnaire
            if msg_type == "message":
                self.receive_message(msg_data)
            elif msg_type == "channel_list":
                self.update_channel_list(msg_data)
            elif msg_type == "user_list":
                self.update_user_list(msg_data)
            elif msg_type == "system":
                self.receive_system_message(msg_data)
            elif msg_type == "error":
                self.receive_error(msg_data)
            elif msg_type == "channel_created":
                self.on_channel_created(msg_data)
            elif msg_type == "channel_joined":
                self.on_channel_joined(msg_data)
                
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"   Données reçues: {json_data}")
        except Exception as e:
            print(f"❌ Erreur traitement message: {e}")
            
    def receive_message(self, data):
        """Traite un message utilisateur"""
        channel = data.get("channel", self.current_channel)
        username = data.get("username", "Inconnu")
        message = data.get("message", "")
        timestamp = data.get("timestamp", time.time())
        
        # Stocker localement
        if channel not in self.messages:
            self.messages[channel] = []
        self.messages[channel].append({
            "username": username,
            "message": message,
            "timestamp": timestamp
        })
        
        # Afficher si salon actuel
        if channel == self.current_channel:
            self.display_message(username, message, timestamp)
            
    def update_channel_list(self, data):
        """Met à jour liste des salons"""
        channels = data.get("channels", [])
        self.channels = channels
        
        print(f"📋 Liste salons mise à jour: {channels}")
        
        # ⚠️ BACKEND : Implémenter la mise à jour des boutons de salons
        # Devrait recréer tous les boutons de salons
        
    def update_user_list(self, data):
        """Met à jour liste utilisateurs"""
        channel = data.get("channel", self.current_channel)
        users = data.get("users", [])
        
        if channel not in self.users:
            self.users[channel] = []
        self.users[channel] = users
        
        print(f"👥 Utilisateurs dans {channel}: {users}")
        
    def receive_system_message(self, data):
        """Traite message système"""
        message = data.get("message", "")
        self.add_system_message(message)
        
    def receive_error(self, data):
        """Traite erreur"""
        error = data.get("error", "Erreur inconnue")
        messagebox.showerror("Erreur", error)
        
    def on_channel_created(self, data):
        """Traite création salon confirmée"""
        channel_name = data.get("channel_name")
        if channel_name:
            self.add_system_message(f"Salon '{channel_name}' créé avec succès")
            
    def on_channel_joined(self, data):
        """Traite rejoindre salon confirmé"""
        channel_name = data.get("channel_name")
        if channel_name:
            self.current_channel = channel_name
            self.channel_title.config(text=f"# {channel_name}")
            self.add_system_message(f"Rejoint le salon '{channel_name}'")
            
    # ============================================================================
    # 🎨 MÉTHODES UI (Complètes - pas besoin de modification backend)
    # ============================================================================
    
    def switch_channel(self, channel_name):
        """Change de salon"""
        if channel_name not in self.channels:
            return
            
        self.current_channel = channel_name
        self.channel_title.config(text=f"# {channel_name}")
        
        # Mettre à jour le style des boutons
        for child in self.channels_buttons_frame.winfo_children():
            if isinstance(child, tk.Button):
                if f"# {channel_name}" == child.cget("text"):
                    child.config(fg=self.colors["text_primary"])
                else:
                    child.config(fg=self.colors["primary"])
        
        # Effacer et réafficher messages
        self.message_display.config(state=tk.NORMAL)
        self.message_display.delete("1.0", tk.END)
        
        # Afficher messages du salon
        messages = self.messages.get(channel_name, [])
        for msg in messages:
            self.display_message(msg["username"], msg["message"], msg["timestamp"])
            
        self.message_display.config(state=tk.DISABLED)
        self.message_display.see(tk.END)
        
    def add_system_message(self, message):
        """Ajoute message système"""
        self.message_display.config(state=tk.NORMAL)
        self.message_display.insert(tk.END, f"⚡ {message}\n\n", "system")
        self.message_display.see(tk.END)
        self.message_display.config(state=tk.DISABLED)
        
    def display_message(self, username, message, timestamp):
        """Affiche un message"""
        self.message_display.config(state=tk.NORMAL)
        
        # Formatage temps
        from datetime import datetime
        try:
            time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M")
        except Exception:
            time_str = "??:??"
            
        self.message_display.insert(tk.END, f"[{time_str}] ", "system")
        self.message_display.insert(tk.END, f"{username}: ", "username")
        self.message_display.insert(tk.END, f"{message}\n\n")
        
        self.message_display.see(tk.END)
        self.message_display.config(state=tk.DISABLED)
        
    def clear_input(self):
        """Efface la zone de saisie"""
        self.message_input.delete("1.0", tk.END)
        
    def on_enter_pressed(self, event):
        """Gère touche Entrée"""
        if not event.state & 0x1:  # Shift non enfoncé
            self.send_message()
            return "break"
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleChatClient(root)
    root.mainloop()
