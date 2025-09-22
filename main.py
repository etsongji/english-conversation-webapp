"""
English Conversation Practice Desktop App
Main GUI Application using tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import logging
from pathlib import Path
from datetime import datetime
import json

# Import our modules
from config import Config, UIConfig, initialize_config
from google_speech import SpeechService
from ai_tutor import AITutorService, ConversationTopics

logger = logging.getLogger(__name__)

class ConversationApp:
    """Main application class"""
    
    def __init__(self):
        # Initialize configuration
        try:
            initialize_config()
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Failed to initialize: {e}")
            return
        
        # Initialize services
        self.speech_service = None
        self.ai_service = None
        self.is_recording = False
        self.conversation_active = False
        
        # Initialize GUI
        self.root = tk.Tk()
        self.setup_gui()
        self.setup_services()
        
        # Start the application
        self.update_status("Ready to start conversation")
    
    def setup_gui(self):
        """Setup the main GUI"""
        self.root.title("English Conversation Practice")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        
        # Get color scheme
        self.colors = UIConfig.get_colors()
        self.root.configure(bg=self.colors['bg'])
        
        # Setup styles
        self.setup_styles()
        
        # Create main layout
        self.create_widgets()
        
        # Bind events
        self.setup_events()
    
    def setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', 
                       font=UIConfig.FONTS['heading'],
                       background=self.colors['bg'],
                       foreground=self.colors['fg'])
        
        style.configure('Status.TLabel',
                       font=UIConfig.FONTS['default'],
                       background=self.colors['bg'],
                       foreground=self.colors['secondary'])
        
        style.configure('Record.TButton',
                       font=UIConfig.FONTS['default'],
                       background=self.colors['success'])
        
        style.configure('Stop.TButton',
                       font=UIConfig.FONTS['default'],
                       background=self.colors['error'])
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎤 English Conversation Practice", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Controls
        self.create_control_panel(main_frame)
        
        # Center panel - Conversation
        self.create_conversation_panel(main_frame)
        
        # Right panel - Stats and Settings
        self.create_info_panel(main_frame)
        
        # Bottom panel - Status
        self.create_status_panel(main_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel"""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Recording controls
        self.record_button = ttk.Button(control_frame, text="🎤 Start Recording",
                                       command=self.toggle_recording,
                                       style='Record.TButton')
        self.record_button.pack(fill=tk.X, pady=5)
        
        # Audio level indicator
        ttk.Label(control_frame, text="Audio Level:").pack(anchor=tk.W, pady=(10, 2))
        self.audio_level_var = tk.DoubleVar()
        self.audio_level_bar = ttk.Progressbar(control_frame, 
                                             variable=self.audio_level_var,
                                             maximum=1.0)
        self.audio_level_bar.pack(fill=tk.X, pady=2)
        
        # Topic selection
        ttk.Label(control_frame, text="Conversation Topic:").pack(anchor=tk.W, pady=(10, 2))
        self.topic_var = tk.StringVar(value="daily_life")
        topics = [("Daily Life", "daily_life"), ("Travel", "travel"), 
                 ("Food & Cooking", "food"), ("Hobbies", "hobbies"),
                 ("Work & Study", "work_study"), ("Goals & Dreams", "future_goals")]
        
        for text, value in topics:
            ttk.Radiobutton(control_frame, text=text, variable=self.topic_var,
                           value=value).pack(anchor=tk.W)
        
        # Action buttons
        ttk.Button(control_frame, text="🎯 Start Topic",
                  command=self.start_topic_conversation).pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="🔄 Clear Chat",
                  command=self.clear_conversation).pack(fill=tk.X, pady=2)
        
        ttk.Button(control_frame, text="💾 Save Chat",
                  command=self.save_conversation).pack(fill=tk.X, pady=2)
        
        ttk.Button(control_frame, text="📁 Load Chat",
                  command=self.load_conversation).pack(fill=tk.X, pady=2)
    
    def create_conversation_panel(self, parent):
        """Create the conversation display panel"""
        conv_frame = ttk.LabelFrame(parent, text="💬 Conversation", padding="10")
        conv_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        conv_frame.columnconfigure(0, weight=1)
        conv_frame.rowconfigure(0, weight=1)
        
        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            conv_frame, 
            height=20, 
            width=50,
            font=UIConfig.FONTS['default'],
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.conversation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input area
        input_frame = ttk.Frame(conv_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        ttk.Label(input_frame, text="Type your message:").grid(row=0, column=0, sticky=tk.W)
        
        self.message_entry = tk.Entry(input_frame, font=UIConfig.FONTS['default'])
        self.message_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_text_message)
        
        ttk.Button(input_frame, text="Send", 
                  command=self.send_text_message).grid(row=1, column=1)
        
        # Current transcription display
        ttk.Label(conv_frame, text="Current transcription:").grid(row=2, column=0, sticky=tk.W, pady=(10, 2))
        self.transcription_var = tk.StringVar(value="Click 'Start Recording' and speak...")
        transcription_label = ttk.Label(conv_frame, textvariable=self.transcription_var,
                                       foreground=self.colors['secondary'],
                                       font=UIConfig.FONTS['default'])
        transcription_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)\n    \n    def create_info_panel(self, parent):\n        \"\"\"Create the information panel\"\"\"\n        info_frame = ttk.LabelFrame(parent, text=\"📊 Information\", padding=\"10\")\n        info_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))\n        \n        # Service status\n        ttk.Label(info_frame, text=\"🔧 Service Status:\", \n                 font=UIConfig.FONTS['heading']).pack(anchor=tk.W, pady=(0, 5))\n        \n        self.speech_status_var = tk.StringVar(value=\"Speech: Checking...\")\n        ttk.Label(info_frame, textvariable=self.speech_status_var).pack(anchor=tk.W)\n        \n        self.ai_status_var = tk.StringVar(value=\"AI: Checking...\")\n        ttk.Label(info_frame, textvariable=self.ai_status_var).pack(anchor=tk.W)\n        \n        # Statistics\n        ttk.Label(info_frame, text=\"📈 Session Stats:\", \n                 font=UIConfig.FONTS['heading']).pack(anchor=tk.W, pady=(15, 5))\n        \n        self.messages_count_var = tk.StringVar(value=\"Messages: 0\")\n        ttk.Label(info_frame, textvariable=self.messages_count_var).pack(anchor=tk.W)\n        \n        self.session_time_var = tk.StringVar(value=\"Duration: 0:00\")\n        ttk.Label(info_frame, textvariable=self.session_time_var).pack(anchor=tk.W)\n        \n        self.tokens_var = tk.StringVar(value=\"Tokens: 0\")\n        ttk.Label(info_frame, textvariable=self.tokens_var).pack(anchor=tk.W)\n        \n        # Settings\n        ttk.Label(info_frame, text=\"⚙️ Settings:\", \n                 font=UIConfig.FONTS['heading']).pack(anchor=tk.W, pady=(15, 5))\n        \n        # AI Provider selection\n        self.ai_provider_var = tk.StringVar(value=Config.AI_PROVIDER)\n        ttk.Label(info_frame, text=\"AI Provider:\").pack(anchor=tk.W)\n        provider_frame = ttk.Frame(info_frame)\n        provider_frame.pack(fill=tk.X, pady=2)\n        \n        ttk.Radiobutton(provider_frame, text=\"OpenAI\", variable=self.ai_provider_var,\n                       value=\"openai\", command=self.change_ai_provider).pack(anchor=tk.W)\n        ttk.Radiobutton(provider_frame, text=\"Ollama\", variable=self.ai_provider_var,\n                       value=\"ollama\", command=self.change_ai_provider).pack(anchor=tk.W)\n        \n        # Offline mode toggle\n        self.offline_mode_var = tk.BooleanVar(value=Config.OFFLINE_MODE)\n        ttk.Checkbutton(info_frame, text=\"Offline Mode (Whisper)\",\n                       variable=self.offline_mode_var,\n                       command=self.toggle_offline_mode).pack(anchor=tk.W, pady=5)\n        \n        # TTS Speed control\n        ttk.Label(info_frame, text=\"Speech Speed:\").pack(anchor=tk.W, pady=(10, 2))\n        self.tts_speed_var = tk.DoubleVar(value=Config.TTS_SPEED)\n        speed_scale = ttk.Scale(info_frame, from_=0.5, to=2.0, \n                               variable=self.tts_speed_var, orient=tk.HORIZONTAL)\n        speed_scale.pack(fill=tk.X)\n        \n        # Test buttons\n        ttk.Button(info_frame, text=\"🔊 Test TTS\",\n                  command=self.test_tts).pack(fill=tk.X, pady=(10, 2))\n        \n        ttk.Button(info_frame, text=\"🎤 Test Recording\",\n                  command=self.test_recording).pack(fill=tk.X, pady=2)\n    \n    def create_status_panel(self, parent):\n        \"\"\"Create the status panel\"\"\"\n        status_frame = ttk.Frame(parent)\n        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))\n        status_frame.columnconfigure(0, weight=1)\n        \n        self.status_var = tk.StringVar(value=\"Initializing...\")\n        status_label = ttk.Label(status_frame, textvariable=self.status_var,\n                                style='Status.TLabel')\n        status_label.grid(row=0, column=0, sticky=tk.W)\n        \n        # Progress bar for loading operations\n        self.progress_var = tk.DoubleVar()\n        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var,\n                                          mode='indeterminate')\n        self.progress_bar.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))\n    \n    def setup_events(self):\n        \"\"\"Setup event handlers\"\"\"\n        self.root.protocol(\"WM_DELETE_WINDOW\", self.on_closing)\n        \n        # Start periodic updates\n        self.update_stats()\n        self.update_session_time()\n    \n    def setup_services(self):\n        \"\"\"Initialize speech and AI services\"\"\"\n        def init_services():\n            try:\n                self.progress_bar.start()\n                \n                # Initialize speech service\n                self.update_status(\"Initializing speech services...\")\n                self.speech_service = SpeechService()\n                \n                if self.speech_service.is_available():\n                    self.speech_status_var.set(\"Speech: ✅ Ready\")\n                    logger.info(\"Speech service initialized successfully\")\n                else:\n                    self.speech_status_var.set(\"Speech: ❌ Not available\")\n                    logger.warning(\"Speech service not available\")\n                \n                # Initialize AI service\n                self.update_status(\"Initializing AI tutor...\")\n                self.ai_service = AITutorService()\n                \n                if self.ai_service.is_available:\n                    self.ai_status_var.set(f\"AI: ✅ {self.ai_service.provider.title()}\")\n                    logger.info(\"AI service initialized successfully\")\n                else:\n                    self.ai_status_var.set(\"AI: ❌ Not available\")\n                    logger.warning(\"AI service not available\")\n                \n                self.progress_bar.stop()\n                self.update_status(\"All services ready!\")\n                \n            except Exception as e:\n                logger.error(f\"Service initialization failed: {e}\")\n                self.progress_bar.stop()\n                self.update_status(f\"Service error: {e}\")\n                messagebox.showerror(\"Service Error\", f\"Failed to initialize services: {e}\")\n        \n        # Run initialization in background\n        threading.Thread(target=init_services, daemon=True).start()\n    \n    def toggle_recording(self):\n        \"\"\"Toggle audio recording\"\"\"\n        if not self.speech_service or not self.speech_service.is_available():\n            messagebox.showerror(\"Error\", \"Speech service not available\")\n            return\n        \n        if not self.is_recording:\n            self.start_recording()\n        else:\n            self.stop_recording()\n    \n    def start_recording(self):\n        \"\"\"Start audio recording\"\"\"\n        try:\n            self.is_recording = True\n            self.record_button.configure(text=\"🛑 Stop Recording\", style='Stop.TButton')\n            self.transcription_var.set(\"🎤 Recording... Speak now!\")\n            \n            # Start recording with audio level callback\n            self.speech_service.start_recording(callback=self.update_audio_level)\n            \n            self.update_status(\"Recording audio...\")\n            logger.info(\"Started recording\")\n            \n        except Exception as e:\n            self.is_recording = False\n            self.record_button.configure(text=\"🎤 Start Recording\", style='Record.TButton')\n            self.update_status(f\"Recording failed: {e}\")\n            messagebox.showerror(\"Recording Error\", f\"Failed to start recording: {e}\")\n    \n    def stop_recording(self):\n        \"\"\"Stop audio recording and process\"\"\"\n        if not self.is_recording:\n            return\n        \n        def process_recording():\n            try:\n                self.update_status(\"Processing audio...\")\n                self.transcription_var.set(\"🔄 Processing audio...\")\n                \n                # Stop recording and get transcription\n                transcript = self.speech_service.stop_recording_and_transcribe()\n                \n                if transcript:\n                    self.transcription_var.set(f\"📝 Transcribed: {transcript}\")\n                    self.add_to_conversation(\"You\", transcript)\n                    \n                    # Get AI response\n                    self.get_ai_response(transcript)\n                else:\n                    self.transcription_var.set(\"❌ No speech detected\")\n                    self.update_status(\"No speech detected\")\n                \n            except Exception as e:\n                logger.error(f\"Recording processing failed: {e}\")\n                self.transcription_var.set(f\"❌ Error: {e}\")\n                self.update_status(f\"Processing failed: {e}\")\n            finally:\n                self.is_recording = False\n                self.record_button.configure(text=\"🎤 Start Recording\", style='Record.TButton')\n                self.audio_level_var.set(0)\n        \n        # Process in background thread\n        threading.Thread(target=process_recording, daemon=True).start()\n    \n    def update_audio_level(self, level):\n        \"\"\"Update audio level indicator\"\"\"\n        self.audio_level_var.set(level)\n    \n    def get_ai_response(self, user_input):\n        \"\"\"Get AI response and play it\"\"\"\n        if not self.ai_service or not self.ai_service.is_available:\n            self.add_to_conversation(\"System\", \"AI service not available\")\n            return\n        \n        def process_ai_response():\n            try:\n                self.update_status(\"Getting AI response...\")\n                \n                # Get AI response\n                ai_response = self.ai_service.get_response(user_input)\n                \n                if ai_response:\n                    self.add_to_conversation(\"AI Tutor\", ai_response)\n                    \n                    # Convert to speech and play\n                    if self.speech_service and self.speech_service.is_available():\n                        self.update_status(\"Converting to speech...\")\n                        success = self.speech_service.text_to_speech(ai_response)\n                        if success:\n                            self.update_status(\"Playing AI response\")\n                        else:\n                            self.update_status(\"TTS failed\")\n                    else:\n                        self.update_status(\"TTS not available\")\n                else:\n                    self.add_to_conversation(\"System\", \"Failed to get AI response\")\n                    self.update_status(\"AI response failed\")\n                \n            except Exception as e:\n                logger.error(f\"AI response failed: {e}\")\n                self.add_to_conversation(\"System\", f\"AI Error: {e}\")\n                self.update_status(f\"AI error: {e}\")\n        \n        # Process in background thread\n        threading.Thread(target=process_ai_response, daemon=True).start()\n    \n    def send_text_message(self, event=None):\n        \"\"\"Send text message from entry widget\"\"\"\n        message = self.message_entry.get().strip()\n        if not message:\n            return\n        \n        self.message_entry.delete(0, tk.END)\n        self.add_to_conversation(\"You\", message)\n        self.get_ai_response(message)\n    \n    def add_to_conversation(self, speaker, message):\n        \"\"\"Add message to conversation display\"\"\"\n        timestamp = datetime.now().strftime(\"%H:%M\")\n        \n        self.conversation_text.configure(state=tk.NORMAL)\n        \n        # Add speaker and timestamp\n        if speaker == \"You\":\n            tag = \"user\"\n            prefix = f\"[{timestamp}] 🙋 You: \"\n        elif speaker == \"AI Tutor\":\n            tag = \"ai\"\n            prefix = f\"[{timestamp}] 🤖 AI Tutor: \"\n        else:\n            tag = \"system\"\n            prefix = f\"[{timestamp}] ℹ️ {speaker}: \"\n        \n        self.conversation_text.insert(tk.END, prefix, tag + \"_prefix\")\n        self.conversation_text.insert(tk.END, message + \"\\n\\n\", tag)\n        \n        # Configure tags for different speakers\n        self.conversation_text.tag_configure(\"user_prefix\", foreground=\"#2E8B57\", font=UIConfig.FONTS['default'])\n        self.conversation_text.tag_configure(\"user\", foreground=\"#2E8B57\")\n        \n        self.conversation_text.tag_configure(\"ai_prefix\", foreground=\"#4169E1\", font=UIConfig.FONTS['default'])\n        self.conversation_text.tag_configure(\"ai\", foreground=\"#4169E1\")\n        \n        self.conversation_text.tag_configure(\"system_prefix\", foreground=\"#888888\", font=UIConfig.FONTS['default'])\n        self.conversation_text.tag_configure(\"system\", foreground=\"#888888\")\n        \n        self.conversation_text.configure(state=tk.DISABLED)\n        self.conversation_text.see(tk.END)\n    \n    def start_topic_conversation(self):\n        \"\"\"Start conversation with selected topic\"\"\"\n        topic = self.topic_var.get()\n        starter = ConversationTopics.get_random_starter(topic)\n        \n        self.add_to_conversation(\"AI Tutor\", starter)\n        \n        # Play the starter if TTS is available\n        if self.speech_service and self.speech_service.is_available():\n            threading.Thread(target=lambda: self.speech_service.text_to_speech(starter), \n                           daemon=True).start()\n    \n    def clear_conversation(self):\n        \"\"\"Clear conversation history\"\"\"\n        if messagebox.askyesno(\"Clear Conversation\", \"Are you sure you want to clear the conversation?\"):\n            self.conversation_text.configure(state=tk.NORMAL)\n            self.conversation_text.delete(1.0, tk.END)\n            self.conversation_text.configure(state=tk.DISABLED)\n            \n            if self.ai_service:\n                self.ai_service.clear_conversation()\n            \n            self.update_status(\"Conversation cleared\")\n    \n    def save_conversation(self):\n        \"\"\"Save conversation to file\"\"\"\n        if not self.ai_service:\n            messagebox.showerror(\"Error\", \"No conversation to save\")\n            return\n        \n        filename = filedialog.asksaveasfilename(\n            defaultextension=\".json\",\n            filetypes=[(\"JSON files\", \"*.json\"), (\"All files\", \"*.*\")],\n            title=\"Save Conversation\"\n        )\n        \n        if filename:\n            try:\n                saved_path = self.ai_service.save_conversation(filename)\n                if saved_path:\n                    self.update_status(f\"Conversation saved to {saved_path}\")\n                    messagebox.showinfo(\"Success\", f\"Conversation saved to:\\n{saved_path}\")\n                else:\n                    messagebox.showerror(\"Error\", \"Failed to save conversation\")\n            except Exception as e:\n                messagebox.showerror(\"Error\", f\"Failed to save conversation: {e}\")\n    \n    def load_conversation(self):\n        \"\"\"Load conversation from file\"\"\"\n        filename = filedialog.askopenfilename(\n            filetypes=[(\"JSON files\", \"*.json\"), (\"All files\", \"*.*\")],\n            title=\"Load Conversation\"\n        )\n        \n        if filename and self.ai_service:\n            try:\n                if self.ai_service.load_conversation(filename):\n                    # Refresh conversation display\n                    self.refresh_conversation_display()\n                    self.update_status(f\"Conversation loaded from {filename}\")\n                    messagebox.showinfo(\"Success\", \"Conversation loaded successfully\")\n                else:\n                    messagebox.showerror(\"Error\", \"Failed to load conversation\")\n            except Exception as e:\n                messagebox.showerror(\"Error\", f\"Failed to load conversation: {e}\")\n    \n    def refresh_conversation_display(self):\n        \"\"\"Refresh conversation display from loaded history\"\"\"\n        if not self.ai_service:\n            return\n        \n        history = self.ai_service.get_conversation_history()\n        \n        # Clear current display\n        self.conversation_text.configure(state=tk.NORMAL)\n        self.conversation_text.delete(1.0, tk.END)\n        \n        # Add messages from history\n        for msg in history.messages:\n            if msg[\"role\"] == \"user\":\n                self.add_to_conversation(\"You\", msg[\"content\"])\n            elif msg[\"role\"] == \"assistant\":\n                self.add_to_conversation(\"AI Tutor\", msg[\"content\"])\n        \n        self.conversation_text.configure(state=tk.DISABLED)\n    \n    def change_ai_provider(self):\n        \"\"\"Change AI provider\"\"\"\n        new_provider = self.ai_provider_var.get()\n        \n        def switch_provider():\n            try:\n                self.update_status(f\"Switching to {new_provider}...\")\n                Config.AI_PROVIDER = new_provider\n                \n                # Reinitialize AI service\n                self.ai_service = AITutorService()\n                \n                if self.ai_service.is_available:\n                    self.ai_status_var.set(f\"AI: ✅ {self.ai_service.provider.title()}\")\n                    self.update_status(f\"Switched to {new_provider}\")\n                else:\n                    self.ai_status_var.set(\"AI: ❌ Not available\")\n                    self.update_status(f\"Failed to switch to {new_provider}\")\n                    \n            except Exception as e:\n                self.ai_status_var.set(\"AI: ❌ Error\")\n                self.update_status(f\"Provider switch failed: {e}\")\n        \n        threading.Thread(target=switch_provider, daemon=True).start()\n    \n    def toggle_offline_mode(self):\n        \"\"\"Toggle offline mode\"\"\"\n        Config.OFFLINE_MODE = self.offline_mode_var.get()\n        \n        # Reinitialize services with new mode\n        self.setup_services()\n    \n    def test_tts(self):\n        \"\"\"Test text-to-speech\"\"\"\n        if self.speech_service and self.speech_service.is_available():\n            test_text = \"Hello! This is a test of the text to speech system. How does it sound?\"\n            threading.Thread(target=lambda: self.speech_service.text_to_speech(test_text), \n                           daemon=True).start()\n            self.update_status(\"Testing TTS...\")\n        else:\n            messagebox.showerror(\"Error\", \"Speech service not available\")\n    \n    def test_recording(self):\n        \"\"\"Test audio recording\"\"\"\n        if not self.speech_service or not self.speech_service.is_available():\n            messagebox.showerror(\"Error\", \"Speech service not available\")\n            return\n        \n        if self.is_recording:\n            messagebox.showwarning(\"Warning\", \"Already recording. Stop current recording first.\")\n            return\n        \n        # Start a 3-second test recording\n        def test_record():\n            try:\n                self.update_status(\"Test recording for 3 seconds...\")\n                self.speech_service.start_recording()\n                time.sleep(3)\n                transcript = self.speech_service.stop_recording_and_transcribe()\n                \n                if transcript:\n                    messagebox.showinfo(\"Test Result\", f\"Recording successful!\\nTranscribed: {transcript}\")\n                else:\n                    messagebox.showwarning(\"Test Result\", \"No speech detected in test recording\")\n                \n                self.update_status(\"Test recording completed\")\n                \n            except Exception as e:\n                messagebox.showerror(\"Test Failed\", f\"Recording test failed: {e}\")\n                self.update_status(\"Test recording failed\")\n        \n        threading.Thread(target=test_record, daemon=True).start()\n    \n    def update_stats(self):\n        \"\"\"Update statistics display\"\"\"\n        if self.ai_service:\n            stats = self.ai_service.get_stats()\n            self.messages_count_var.set(f\"Messages: {stats.get('total_messages', 0)}\")\n            self.tokens_var.set(f\"Tokens: {stats.get('total_tokens', 0)}\")\n        \n        # Schedule next update\n        self.root.after(5000, self.update_stats)  # Update every 5 seconds\n    \n    def update_session_time(self):\n        \"\"\"Update session time display\"\"\"\n        if self.ai_service:\n            stats = self.ai_service.get_stats()\n            duration = stats.get('session_duration', 0)\n            \n            minutes = int(duration // 60)\n            seconds = int(duration % 60)\n            self.session_time_var.set(f\"Duration: {minutes}:{seconds:02d}\")\n        \n        # Schedule next update\n        self.root.after(1000, self.update_session_time)  # Update every second\n    \n    def update_status(self, message):\n        \"\"\"Update status message\"\"\"\n        self.status_var.set(message)\n        logger.info(f\"Status: {message}\")\n    \n    def on_closing(self):\n        \"\"\"Handle application closing\"\"\"\n        try:\n            # Stop any ongoing recording\n            if self.is_recording:\n                self.stop_recording()\n            \n            # Cleanup services\n            if self.speech_service:\n                self.speech_service.cleanup()\n            \n            # Save current conversation if there are messages\n            if self.ai_service:\n                stats = self.ai_service.get_stats()\n                if stats.get('total_messages', 0) > 0:\n                    if messagebox.askyesno(\"Save Conversation\", \n                                         \"Would you like to save the current conversation?\"):\n                        timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n                        filename = f\"conversation_{timestamp}.json\"\n                        self.ai_service.save_conversation(filename)\n            \n            logger.info(\"Application closing\")\n            \n        except Exception as e:\n            logger.error(f\"Error during cleanup: {e}\")\n        finally:\n            self.root.destroy()\n    \n    def run(self):\n        \"\"\"Start the application\"\"\"\n        try:\n            self.root.mainloop()\n        except KeyboardInterrupt:\n            logger.info(\"Application interrupted\")\n        except Exception as e:\n            logger.error(f\"Application error: {e}\")\n            messagebox.showerror(\"Application Error\", f\"An error occurred: {e}\")\n\ndef main():\n    \"\"\"Main application entry point\"\"\"\n    try:\n        app = ConversationApp()\n        app.run()\n    except Exception as e:\n        print(f\"Failed to start application: {e}\")\n        if tk:\n            messagebox.showerror(\"Startup Error\", f\"Failed to start application: {e}\")\n\nif __name__ == \"__main__\":\n    main()