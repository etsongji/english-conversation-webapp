"""
Simple version of English Conversation Practice Desktop App
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import logging
from datetime import datetime

# Import our modules
from config import Config, UIConfig, initialize_config
from ai_tutor import AITutorService

logger = logging.getLogger(__name__)

class SimpleConversationApp:
    """Simplified main application class"""
    
    def __init__(self):
        # Initialize configuration
        try:
            initialize_config()
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Failed to initialize: {e}")
            return
        
        # Initialize AI service
        self.ai_service = None
        
        # Initialize GUI
        self.root = tk.Tk()
        self.setup_gui()
        self.setup_services()
        
        # Start the application
        self.update_status("Ready to start conversation")
    
    def setup_gui(self):
        """Setup the main GUI"""
        self.root.title("English Conversation Practice")
        self.root.geometry("600x500")
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="English Conversation Practice", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Conversation display
        conversation_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="10")
        conversation_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text display
        from tkinter import scrolledtext
        self.conversation_text = scrolledtext.ScrolledText(
            conversation_frame, 
            height=15, 
            width=70,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        
        # Input area
        input_frame = ttk.Frame(conversation_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(input_frame, text="Your message:").pack(anchor=tk.W)
        
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X)
        
        self.message_entry = tk.Entry(entry_frame, font=('Arial', 10))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_message)
        
        send_button = ttk.Button(entry_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(control_frame, text="Start Topic", 
                  command=self.start_topic).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="Clear Chat", 
                  command=self.clear_conversation).pack(side=tk.LEFT, padx=(0, 5))
        
        # Status
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=(10, 0))
    
    def setup_services(self):
        """Initialize AI service"""
        def init_ai():
            try:
                self.update_status("Initializing AI tutor...")
                self.ai_service = AITutorService()
                
                if self.ai_service.is_available:
                    self.update_status("AI tutor ready!")
                    self.add_to_conversation("System", "AI tutor is ready. Type a message to start chatting!")
                else:
                    self.update_status("AI tutor not available")
                    self.add_to_conversation("System", "AI tutor is not available. Please check your configuration.")
                    
            except Exception as e:
                self.update_status(f"AI initialization failed: {e}")
                self.add_to_conversation("System", f"Error: {e}")
        
        # Run in background
        threading.Thread(target=init_ai, daemon=True).start()
    
    def send_message(self, event=None):
        """Send user message"""
        message = self.message_entry.get().strip()
        if not message:
            return
        
        self.message_entry.delete(0, tk.END)
        self.add_to_conversation("You", message)
        
        # Get AI response
        if self.ai_service and self.ai_service.is_available:
            def get_response():
                try:
                    self.update_status("Getting AI response...")
                    response = self.ai_service.get_response(message)
                    if response:
                        self.add_to_conversation("AI Tutor", response)
                    else:
                        self.add_to_conversation("System", "Failed to get AI response")
                    self.update_status("Ready")
                except Exception as e:
                    self.add_to_conversation("System", f"AI Error: {e}")
                    self.update_status("Ready")
            
            threading.Thread(target=get_response, daemon=True).start()
    
    def start_topic(self):
        """Start a conversation topic"""
        from ai_tutor import ConversationTopics
        starter = ConversationTopics.get_random_starter()
        self.add_to_conversation("AI Tutor", starter)
    
    def clear_conversation(self):
        """Clear conversation"""
        if messagebox.askyesno("Clear", "Clear conversation?"):
            self.conversation_text.configure(state=tk.NORMAL)
            self.conversation_text.delete(1.0, tk.END)
            self.conversation_text.configure(state=tk.DISABLED)
            
            if self.ai_service:
                self.ai_service.clear_conversation()
    
    def add_to_conversation(self, speaker, message):
        """Add message to conversation"""
        timestamp = datetime.now().strftime("%H:%M")
        
        self.conversation_text.configure(state=tk.NORMAL)
        
        if speaker == "You":
            prefix = f"[{timestamp}] You: "
            self.conversation_text.insert(tk.END, prefix, "user_prefix")
            self.conversation_text.insert(tk.END, message + "\n\n", "user")
        elif speaker == "AI Tutor":
            prefix = f"[{timestamp}] AI Tutor: "
            self.conversation_text.insert(tk.END, prefix, "ai_prefix")
            self.conversation_text.insert(tk.END, message + "\n\n", "ai")
        else:
            prefix = f"[{timestamp}] {speaker}: "
            self.conversation_text.insert(tk.END, prefix, "system_prefix")
            self.conversation_text.insert(tk.END, message + "\n\n", "system")
        
        # Configure colors
        self.conversation_text.tag_configure("user_prefix", foreground="#2E8B57", font=('Arial', 10, 'bold'))
        self.conversation_text.tag_configure("user", foreground="#2E8B57")
        
        self.conversation_text.tag_configure("ai_prefix", foreground="#4169E1", font=('Arial', 10, 'bold'))
        self.conversation_text.tag_configure("ai", foreground="#4169E1")
        
        self.conversation_text.tag_configure("system_prefix", foreground="#888888", font=('Arial', 10, 'bold'))
        self.conversation_text.tag_configure("system", foreground="#888888")
        
        self.conversation_text.configure(state=tk.DISABLED)
        self.conversation_text.see(tk.END)
    
    def update_status(self, message):
        """Update status"""
        self.status_var.set(message)
        print(f"Status: {message}")
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Application error: {e}")

def main():
    """Main entry point"""
    try:
        app = SimpleConversationApp()
        app.run()
    except Exception as e:
        print(f"Failed to start: {e}")

if __name__ == "__main__":
    main()