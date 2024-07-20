import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Scrollbar
import os
import openai
import threading
from datetime import datetime
import winsound
import tiktoken
from cryptography.fernet import Fernet, InvalidToken

# Constants
MAX_TOKEN_LIMIT = 128000
OPENAI_TIMEOUT = (60, 360)  # (connect_timeout, read_timeout) in seconds

# Dictionary of model names and their corresponding maximum token limits
# Add new models to this list to make them available in the dropdown (last updated: 20/07/2024)
MODEL_MAX_TOKENS = {
    # GPT-4o models
    "gpt-4o": 128000, 
    "gpt-4o-2024-05-13": 128000,
    
    # GPT-4o mini models
    "gpt-4o-mini": 128000, 
    "gpt-4o-mini-2024-07-18": 128000,
    
    # GPT-4 Turbo and GPT-4 models
    "gpt-4-turbo": 128000, 
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-4-turbo-preview": 128000, 
    "gpt-4-0125-preview": 4096,  
    "gpt-4-1106-preview": 4096,  
    "gpt-4": 8192,
    "gpt-4-0613": 8192, 
    "gpt-4-0314": 8192,
    
    # GPT-4-32k models
    "gpt-4-32k": 32768, 
    "gpt-4-32k-0613": 32768, 
    "gpt-4-32k-0314": 32768,
    
    # GPT-3.5 Turbo models
    "gpt-3.5-turbo-0125": 16385, 
    "gpt-3.5-turbo": 16385,
    "gpt-3.5-turbo-1106": 16385, 
    "gpt-3.5-turbo-instruct": 4096,
    "gpt-3.5-turbo-16k": 16385, 
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k-0613": 16385, 
    "gpt-3.5-turbo-0301": 4096,
}


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Merger")
        self.state("zoomed")
        
        # Initialize application variables
        self.debug_logs = []
        self.cs_file_contents = []
        self.is_request_in_progress = False
        self.gpt_response_counter = 0
        self.available_models = []
        
        # Initialize token count variables
        self.start_text_token_count_var = tk.StringVar()
        self.final_prompt_token_count_var = tk.StringVar()
        self.end_text_token_count_var = tk.StringVar()
        
        # Load or generate encryption key and API key
        self.encryption_key = self.load_or_generate_key()
        self.api_key_loaded = self.load_api_key()
        
        # Create UI widgets
        self._create_widgets()
        
        # Initialize OpenAI API and load models if API key is available
        self.initialize_openai_api()

    def _create_widgets(self):
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Prompt Creation")
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="GPT Response")
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Debug Logs")

        # Create top frame for API key and model selection
        top_frame = tk.Frame(self.tab1)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # API Key entry and save button
        tk.Label(top_frame, text="API Key: ").pack(side=tk.LEFT, padx=5, pady=5)
        self.api_key_entry = tk.Entry(top_frame, show="*", width=50)
        self.api_key_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.api_key_entry.insert(0, self.load_api_key())
        save_api_key_button = tk.Button(
            top_frame,
            text="Save API Key",
            command=self.handle_save_api_key_button_click,
        )
        save_api_key_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Model selection dropdown
        self.model_var = tk.StringVar()
        self.model_var.set("gpt-3.5-turbo")
        self.model_dropdown = ttk.Combobox(
            top_frame,
            textvariable=self.model_var,
            values=self.available_models,
            width=30,
        )
        self.model_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.on_model_change)

        # Max tokens frame
        self.max_tokens_frame = tk.Frame(top_frame)
        self.max_tokens_frame.pack(side=tk.LEFT, padx=5)

        self.max_tokens_var = tk.StringVar()
        self.max_tokens_entry = tk.Entry(
            self.max_tokens_frame, textvariable=self.max_tokens_var, width=10
        )
        self.max_tokens_entry.pack(side=tk.LEFT)

        self.use_max_tokens_var = tk.BooleanVar(value=False)
        self.use_max_tokens_check = tk.Checkbutton(
            self.max_tokens_frame,
            text="Use Max Tokens",
            variable=self.use_max_tokens_var,
            command=self.use_max_tokens,
        )
        self.use_max_tokens_check.pack(side=tk.LEFT)

        self.manual_token_entry_var = tk.BooleanVar(value=False)
        self.manual_token_entry_check = tk.Checkbutton(
            self.max_tokens_frame,
            text="Manual Token Entry",
            variable=self.manual_token_entry_var,
        )
        self.manual_token_entry_check.pack(side=tk.LEFT, padx=5)

        # Buttons for loading messages, emptying fields, and resetting logs
        load_standard_messages_button = tk.Button(
            top_frame,
            text="Load Standard Messages",
            command=self.load_standard_messages,
        )
        load_standard_messages_button.pack(side=tk.RIGHT, padx=5, pady=5)

        empty_textfields_button = tk.Button(
            top_frame, text="Empty Textfields", command=self.empty_textfields
        )
        empty_textfields_button.pack(side=tk.RIGHT, padx=5, pady=5)

        empty_responses_button = tk.Button(
            top_frame, text="Empty Responses", command=self.empty_responses
        )
        empty_responses_button.pack(side=tk.RIGHT, padx=5, pady=5)

        reset_debug_button = tk.Button(
            top_frame, text="Reset Debug Logs", command=self.reset_debug_logs
        )
        reset_debug_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(
            top_frame, orient="horizontal", length=200, mode="determinate"
        )
        self.progress.pack(side=tk.RIGHT, padx=5, pady=5)

        # Text fields for start, middle, and end message parts
        tk.Label(self.tab1, text="Start Message Part", anchor="w").pack(
            fill="x", padx=5, pady=5
        )
        self.start_text_field = tk.Text(self.tab1, wrap=tk.WORD, height=10)
        self.start_text_field.pack(fill=tk.X, padx=5, pady=5)
        self.start_text_field.bind("<KeyRelease>", self.update_start_text_token_count)

        tk.Button(
            self.tab1, text="Open File Explorer", command=self.open_file_explorer
        ).pack(pady=10)

        tk.Label(self.tab1, text="Middle Message Part", anchor="w").pack(
            fill="x", padx=5, pady=5
        )
        self.final_prompt = tk.Text(self.tab1, wrap=tk.WORD)
        self.final_prompt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.final_prompt.bind("<KeyRelease>", self.update_final_prompt_token_count)

        tk.Label(self.tab1, text="End Message Part", anchor="w").pack(
            fill="x", padx=5, pady=5
        )
        self.end_text_field = tk.Text(self.tab1, wrap=tk.WORD, height=10)
        self.end_text_field.pack(fill=tk.X, padx=5, pady=5)
        self.end_text_field.bind("<KeyRelease>", self.update_end_text_token_count)

        # Debug mode checkbox
        self.debug_var = tk.BooleanVar()
        tk.Checkbutton(self.tab1, text="Debug Mode", variable=self.debug_var).pack(
            pady=5
        )

        # Send to GPT button
        self.send_button = tk.Button(
            self.tab1, text="Send to GPT", command=self.threaded_send_prompt
        )
        self.send_button.pack(pady=10)

        # GPT Response field
        yscrollbar = Scrollbar(self.tab2)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.gpt_response_field = tk.Text(
            self.tab2, wrap=tk.WORD, yscrollcommand=yscrollbar.set
        )
        self.gpt_response_field.pack(fill=tk.BOTH, expand=True)

        yscrollbar.config(command=self.gpt_response_field.yview)

        # Debug log field
        self.debug_scrollbar = Scrollbar(self.tab3)
        self.debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.debug_log_field = tk.Text(
            self.tab3, wrap=tk.WORD, yscrollcommand=self.debug_scrollbar.set
        )
        self.debug_log_field.pack(fill=tk.BOTH, expand=True)
        self.debug_scrollbar.config(command=self.debug_log_field.yview)

    def initialize_openai_api(self):
        """Initialize the OpenAI API with the loaded API key and update the model dropdown."""
        if self.api_key_loaded:
            openai.api_key = self.api_key_loaded
            self.update_model_dropdown()
        else:
            self.add_debug_log("API Key is missing or could not be loaded.")

    def handle_save_api_key_button_click(self):
        """Handle the click event for the Save API Key button."""
        api_key = self.api_key_entry.get()
        self.save_api_key(api_key)
        openai.api_key = api_key  # Set the API key for immediate use
        self.update_model_dropdown()  # Update the model dropdown after saving the API key

    def empty_textfields(self):
        """Clear all text fields in the application."""
        self.start_text_field.delete("1.0", tk.END)
        self.final_prompt.delete("1.0", tk.END)
        self.end_text_field.delete("1.0", tk.END)

    def empty_responses(self):
        """Clear the GPT response field."""
        self.gpt_response_field.delete("1.0", tk.END)

    def update_start_text_token_count(self, event=None):
        """Update the token count for the start text field."""
        text = self.start_text_field.get("1.0", tk.END).strip()
        token_count = self.num_tokens_from_messages([{"content": text}])
        self.start_text_token_count_var.set(str(token_count))

    def update_final_prompt_token_count(self, event=None):
        """Update the token count for the final prompt field."""
        text = self.final_prompt.get("1.0", tk.END).strip()
        token_count = self.num_tokens_from_messages([{"content": text}])
        self.final_prompt_token_count_var.set(str(token_count))

    def update_end_text_token_count(self, event=None):
        """Update the token count for the end text field."""
        text = self.end_text_field.get("1.0", tk.END).strip()
        token_count = self.num_tokens_from_messages([{"content": text}])
        self.end_text_token_count_var.set(str(token_count))

    def on_model_change(self, event=None):
        """Handle the event when the model is changed in the dropdown."""
        if self.use_max_tokens_var.get():
            self.use_max_tokens()

    def use_max_tokens(self):
        """Set the max tokens value based on the selected model."""
        model_max_tokens = MODEL_MAX_TOKENS.get(self.model_var.get(), MAX_TOKEN_LIMIT)
        self.max_tokens_var.set(model_max_tokens)
        self.max_tokens_entry.config(
            state="disabled" if self.use_max_tokens_var.get() else "normal"
        )

    def reset_debug_logs(self):
        """Clear all debug logs."""
        self.debug_logs.clear()
        self.debug_log_field.delete("1.0", tk.END)

    def load_or_generate_key(self):
        """Load the encryption key from file or generate a new one if not found."""
        try:
            with open("encryption_key.key", "rb") as f:
                return f.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open("encryption_key.key", "wb") as f:
                f.write(key)
            return key

    def decrypt_key(self, key, encrypted_api_key):
        """Decrypt the API key using the encryption key."""
        cipher_suite = Fernet(key)
        try:
            return cipher_suite.decrypt(encrypted_api_key).decode()
        except InvalidToken:
            return ""

    def load_api_key(self):
        """Load the API key from file and decrypt it."""
        try:
            with open("api_key.txt", "rb") as f:
                encrypted_api_key = f.read()
            return self.decrypt_key(self.encryption_key, encrypted_api_key)
        except FileNotFoundError:
            return ""

    def get_available_models(self):
        """Fetch available models from OpenAI API."""
        if not openai.api_key:
            self.add_debug_log("No API key set. Unable to fetch models.")
            return []
        
        try:
            response = openai.Model.list()
            allowed_models = set(MODEL_MAX_TOKENS.keys())
            models = [model["id"] for model in response["data"] if model["id"] in allowed_models]
            models.sort()
            return models
        except openai.error.AuthenticationError:
            self.add_debug_log("Invalid API key. Unable to fetch models.")
            return []
        except Exception as e:
            self.add_debug_log(f"Error fetching models: {str(e)}")
            return []

    def update_model_dropdown(self):
        """Update the model dropdown with the latest available models."""
        try:
            available_models = self.get_available_models()
            if available_models:
                self.model_dropdown['values'] = available_models
                self.model_var.set(available_models[0])  # Set the first model as default
                self.add_debug_log("Model dropdown updated successfully.")
            else:
                self.add_debug_log("No models available.")
        except Exception as e:
            self.add_debug_log(f"Error updating model dropdown: {str(e)}")

    def is_chat_model(self, model_name):
        """Determine if the given model is a chat model."""
        chat_models = [
            "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", 
            "gpt-3.5-turbo-16k", "gpt-3.5-turbo-instruct", "gpt-3.5-turbo-16k-0613",
            "gpt-4", "gpt-4-0613", "gpt-4-0314"
        ]
        return model_name in chat_models

    def add_debug_log(self, message):
        """Add a message to the debug log and update the debug log field."""
        self.debug_logs.append(message)
        self.debug_log_field.delete("1.0", tk.END)
        for log in self.debug_logs:
            self.debug_log_field.insert(tk.END, f"{log}\n")
        self.debug_log_field.insert(tk.END, "-----\n")

    def encrypt_key(self, key, api_key):
        """Encrypt the API key using the encryption key."""
        cipher_suite = Fernet(key)
        return cipher_suite.encrypt(api_key.encode())

    def save_api_key(self, api_key):
        """Save the encrypted API key to file."""
        encrypted_api_key = self.encrypt_key(self.encryption_key, api_key)
        file_path = os.path.join(os.path.dirname(__file__), "api_key.txt")
        with open(file_path, "wb") as f:
            f.write(encrypted_api_key)
        self.add_debug_log("API key saved.")
        openai.api_key = api_key

    def load_standard_messages(self):
        """Load standard start and end messages from files in the active_templates directory."""
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            templates_dir = os.path.join(dir_path, "active_templates")
            
            with open(os.path.join(templates_dir, "start_message.txt"), "r", encoding="utf-8") as f:
                start_message = f.read()
            self.start_text_field.delete("1.0", tk.END)
            self.start_text_field.insert(tk.END, start_message)
    
            with open(os.path.join(templates_dir, "end_message.txt"), "r", encoding="utf-8") as f:
                end_message = f.read()
            self.end_text_field.delete("1.0", tk.END)
            self.end_text_field.insert(tk.END, end_message)
    
            self.add_debug_log("Standard Start/End messages loaded from active_templates directory.")
    
        except FileNotFoundError as e:
            self.add_debug_log(f"Error loading standard messages from active_templates: {e}")
        except Exception as e:
            self.add_debug_log(f"Unexpected error loading standard messages: {e}")

    def read_cs_files(self, filenames):
        """Read selected C# files and update the final prompt field."""
        self.cs_file_contents = []
        self.final_prompt.delete("1.0", tk.END)
        for filename in filenames:
            with open(filename, "r", encoding="utf-8") as f:
                file_content = f.read()
            self.cs_file_contents.append(
                f"--- {os.path.basename(filename)} ---\n{file_content}"
            )
            self.final_prompt.insert(
                tk.END, f"--- {os.path.basename(filename)} ---\n{file_content}\n"
            )

        self.add_debug_log("Selected and read .cs files.")

    def open_file_explorer(self):
        """Open file explorer to select C# files."""
        filenames = filedialog.askopenfilenames(filetypes=[("C# files", "*.cs")])
        self.read_cs_files(filenames)

    def save_prompt(self):
        """Save the current prompt to a file."""
        start_text = self.start_text_field.get("1.0", tk.END).strip()
        end_text = self.end_text_field.get("1.0", tk.END).strip()
        final_prompt = f"{start_text}\n{''.join(self.cs_file_contents)}\n{end_text}"

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not filename:
            return

        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_prompt)

        self.add_debug_log(f"Prompt saved to {filename}.")

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Calculate the number of tokens in a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Approximate overhead for each message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens -= 1  # Adjustment if "name" key exists
        num_tokens += 2  # Approximate overhead for start and end of messages

        return num_tokens

    def threaded_send_prompt(self):
        """Start a new thread to send the prompt to GPT."""
        if self.is_request_in_progress:
            messagebox.showinfo(
                "GPT Request", "Another request is already in progress."
            )
            return

        self.is_request_in_progress = True
        self.send_button.config(state="disabled")
        threading.Thread(target=self.send_prompt_to_gpt, daemon=True).start()

    def send_prompt_to_gpt(self):
        """Send the constructed prompt to GPT and handle the response."""
        if self.debug_var.get():
            self.add_debug_log("Debug mode is enabled. Prompt will not be sent to GPT.")
            start_text = self.start_text_field.get("1.0", tk.END).strip()
            middle_text = ("".join(self.cs_file_contents) if self.cs_file_contents else self.final_prompt.get("1.0", tk.END).strip())
            end_text = self.end_text_field.get("1.0", tk.END).strip()
            final_prompt = f"{start_text}\n{middle_text}\n{end_text}"
            self.add_debug_log("Debug Prompt Content:")
            self.add_debug_log(final_prompt)
            self.is_request_in_progress = False
            self.send_button.config(state="normal")
            return

        try:
            self.progress["value"] = 0
            self.update_idletasks()

            start_text = self.start_text_field.get("1.0", tk.END).strip()
            middle_text = ("".join(self.cs_file_contents) if self.cs_file_contents else self.final_prompt.get("1.0", tk.END).strip())
            end_text = self.end_text_field.get("1.0", tk.END).strip()
            final_prompt = f"{start_text}\n{middle_text}\n{end_text}"

            total_prompt_tokens = self.num_tokens_from_messages([{"content": final_prompt}])
            model_max_tokens = MODEL_MAX_TOKENS.get(self.model_var.get(), MAX_TOKEN_LIMIT)
            max_tokens = min(model_max_tokens, 4096)  # Use the smaller of model max tokens or 4096 as a safeguard

            if total_prompt_tokens > model_max_tokens:
                messagebox.showerror("Error", "Prompt token count exceeds the model's limit.")
                self.add_debug_log("Prompt token count exceeds the model's limit.")
                self.is_request_in_progress = False
                return

            self.add_debug_log("Sending prompt to GPT...")
            self.add_debug_log("Prompt Content:")
            self.add_debug_log(final_prompt)

            response = openai.ChatCompletion.create(
                model=self.model_var.get(),
                messages=[{"role": "system", "content": final_prompt}],
                max_tokens=max_tokens,
            )

            self.gpt_response_counter += 1
            response_text = f"--- Response {self.gpt_response_counter} ---\n{response['choices'][0]['message']['content']}\n"

            self.gpt_response_field.insert(tk.END, response_text)
            self.progress["value"] = 100
            self.update_idletasks()
            winsound.MessageBeep(winsound.MB_ICONASTERISK)

            if self.debug_var.get():
                self.add_debug_log("Received GPT response.")

            self.save_gpt_response(response_text, self.model_var.get())
            self.is_request_in_progress = False

        except Exception as e:
            self.add_debug_log(f"An error occurred: {e}")
            self.is_request_in_progress = False
            self.progress["value"] = 0
            self.update_idletasks()
            winsound.MessageBeep(winsound.MB_ICONHAND)
        finally:
            self.send_button.config(state="normal")

    def save_gpt_response(self, response_text, model_name):
        """Save the GPT response to a file."""
        base_dir = os.path.dirname(os.path.realpath(__file__))
        responses_dir = os.path.join(
            base_dir, "Responses", datetime.now().strftime("%Y-%m-%d")
        )
        os.makedirs(responses_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}-{model_name}-Response.txt"
        file_path = os.path.join(responses_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response_text)

        self.add_debug_log(f"GPT response saved to {file_path}.")

    def close_window(self):
        """Handle the window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
