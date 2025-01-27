import customtkinter as ctk
from enum import Enum
from typing import Optional
import json
from ollama import generate

class ResponseSchema(Enum):
    USER_JSON = "user_json"
    PRODUCT_JSON = "product_json"
    PLAIN = "plain"

class OllamaPromptUI:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("Ollama Prompt Interface")
        self.root.geometry("800x600")
        
        # Schema templates
        self.schema_templates = {
            ResponseSchema.USER_JSON.value: {
                "type": "object",
                "properties": {
                    "users": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "user#": {"type": "integer"},
                                "name": {"type": "string"},
                                "age": {"type": "integer"}
                            },
                            "required": ["user#","name", "age"]
                        }
                    }
                },
                "required": ["users"]
            },
            ResponseSchema.PRODUCT_JSON.value: {
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product#": {"type": "integer"},
                                "name": {"type": "string"},
                                "price": {"type": "number"}
                            },
                            "required": ["product#","name", "price"]
                        }
                    }
                },
                "required": ["products"]
            },
        }
        
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        
        # Create and configure UI elements
        self._setup_ui()
        
    def _setup_ui(self):
        # Prompt input label
        self.prompt_label = ctk.CTkLabel(
            self.root,
            text="Enter your prompt:",
            font=("Arial", 14)
        )
        self.prompt_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        # Prompt input text area
        self.prompt_input = ctk.CTkTextbox(
            self.root,
            height=100,
            font=("Arial", 12)
        )
        self.prompt_input.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        # Schema selection frame
        self.schema_frame = ctk.CTkFrame(self.root)
        self.schema_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        # Schema selection label
        self.schema_label = ctk.CTkLabel(
            self.schema_frame,
            text="Select Response Schema:",
            font=("Arial", 12)
        )
        self.schema_label.pack(side="left", padx=5)
        
        # Schema dropdown
        self.schema_var = ctk.StringVar(value=ResponseSchema.PLAIN.value)
        self.schema_dropdown = ctk.CTkOptionMenu(
            self.schema_frame,
            values=[schema.value for schema in ResponseSchema],
            variable=self.schema_var,
            command=self._update_schema_preview
        )
        self.schema_dropdown.pack(side="left", padx=5)
        
        # Schema preview
        self.schema_preview = ctk.CTkTextbox(
            self.root,
            height=100,
            font=("Arial", 12)
        )
        self.schema_preview.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        # Response area
        self.response_label = ctk.CTkLabel(
            self.root,
            text="Response:",
            font=("Arial", 14)
        )
        self.response_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.response_text = ctk.CTkTextbox(
            self.root,
            height=200,
            font=("Arial", 12)
        )
        self.response_text.grid(row=5, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        # Submit button
        self.submit_button = ctk.CTkButton(
            self.root,
            text="Send to Ollama",
            command=self._send_prompt
        )
        self.submit_button.grid(row=6, column=0, padx=10, pady=10)
        
        # Initialize schema preview
        self._update_schema_preview()
        
    def _update_schema_preview(self, *args):
        """Update the schema preview based on selected schema."""
        schema = self.schema_var.get()
        self.schema_preview.delete("1.0", "end")
        
        if schema in self.schema_templates:
            preview = json.dumps(self.schema_templates[schema], indent=2)
            self.schema_preview.insert("1.0", f"Expected Schema:\n{preview}")
        else:
            self.schema_preview.insert("1.0", "No specific schema required")
        
    def _send_prompt(self):
        prompt = self.prompt_input.get("1.0", "end-1c")
        schema = self.schema_var.get()
        
        # Prepare the request based on selected schema
        format_prompt, responseSchema = self._format_prompt(prompt, schema)
        
        try:
            # Send request using ollama client
            response = generate(
                model="llama3.2:3b",  # Change this to your preferred model
                prompt=format_prompt,
                format=responseSchema
            )
            
            self.response_text.delete("1.0", "end")
            self.response_text.insert("1.0", response['response'])
                
        except Exception as e:
            self.response_text.delete("1.0", "end")
            self.response_text.insert("1.0", f"Error: {str(e)}")
    
    def _format_prompt(self, prompt: str, schema: str) -> str:
        """Format the prompt based on the selected schema."""
        prompt = f"{prompt}\nPlease respond with a JSON object."
        return prompt, self.schema_templates[schema]
    
    def run(self):
        """Start the UI application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = OllamaPromptUI()
    app.run()