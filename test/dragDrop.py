import customtkinter as ctk

# Initialize the main app
class DragDropApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Drag and Drop UI")
        self.geometry("600x400")

        # Variables
        self.selected_value = None

        # Instructions label
        self.instruction_label = ctk.CTkLabel(self, text="Drag a label into the selection area below:", font=("Arial", 16))
        self.instruction_label.pack(pady=10)

        # Labels container
        self.label_frame = ctk.CTkFrame(self, height=100)
        self.label_frame.pack(fill="x", pady=10)

        # Draggable labels
        self.create_draggable_label("Option 1")
        self.create_draggable_label("Option 2")
        self.create_draggable_label("Option 3")

        # Drop area
        self.drop_area = ctk.CTkFrame(self, height=150, border_color="blue", border_width=2)
        self.drop_area.pack(fill="x", pady=10)

        self.drop_label = ctk.CTkLabel(self.drop_area, text="Drop here", font=("Arial", 14))
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        # Button to print selected value
        self.print_button = ctk.CTkButton(self, text="Print Selection", command=self.print_selection)
        self.print_button.pack(pady=10)

    def create_draggable_label(self, text):
        label = ctk.CTkLabel(self.label_frame, text=text, font=("Arial", 14), bg_color="#333333", fg_color="white", width=100)
        label.pack(side="left", padx=10)
        label.bind("<Button-1>", self.start_drag)

    def start_drag(self, event):
        widget = event.widget
        widget.start_x = event.x
        widget.start_y = event.y
        widget.bind("<B1-Motion>", self.drag)
        widget.bind("<ButtonRelease-1>", self.stop_drag)

    def drag(self, event):
        widget = event.widget
        widget.lift()

    def stop_drag(self, event):
        widget = event.widget
        widget.unbind("<B1-Motion>")
        widget.unbind("<ButtonRelease-1>")
        if self.drop_area.winfo_containing(event.x_root, event.y_root):
            self.selected_value = widget.cget("text")
            self.drop_label.configure(text=f"Selected: {self.selected_value}")
            widget.pack_forget()
            widget.pack(in_=self.drop_area, pady=5)
        else:
            # Reset label to its original container if not dropped in the drop area
            widget.pack_forget()
            widget.pack(side="left", padx=10)

    def print_selection(self):
        if self.selected_value:
            print(f"Selected Value: {self.selected_value}")
        else:
            print("No value selected")

if __name__ == "__main__":
    app = DragDropApp()
    app.mainloop()
