
# src/ai/ui/agentUi.py

import tkinter as tk
from tkinter import messagebox

class AgentUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Agent UI")
        
        # Create a label
        self.label = tk.Label(root, text="Welcome to Ollama Agent!")
        self.label.pack(pady=10)
        
        # Create a button
        self.button = tk.Button(root, text="Click Me", command=self.on_button_click)
        self.button.pack(pady=5)

    def on_button_click(self):
        messagebox.showinfo("Information", "Button Clicked!")

def main():
    root = tk.Tk()
    app = AgentUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
# write customktinker samle app