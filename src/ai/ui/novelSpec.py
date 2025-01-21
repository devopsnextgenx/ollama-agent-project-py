import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk, Canvas, Frame, Scrollbar
import yaml
from ai.models.novel.Schema import NovelSpec, Character, ChapterSpec
from ai.models.SafetyConfig import SafetyConfig

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NovelSpec and SafetyConfig UI")
        self.geometry("800x600")

        self.novel_spec = None
        self.safety_config = SafetyConfig()
	
        # Container frame for menu and main content
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(side="top", fill="both", expand=True)

        # Set up the menu
        self.menu_frame = ctk.CTkFrame(self.top_frame, width=200)
        self.menu_frame.pack(side="left", fill="y")

        self.novel_spec_button = ctk.CTkButton(self.menu_frame, text="Novel Spec", command=self.show_novel_spec)
        self.novel_spec_button.pack(pady=2)

        self.safety_spec_button = ctk.CTkButton(self.menu_frame, text="Safety Spec", command=self.show_safety_spec)
        self.safety_spec_button.pack(pady=2)

        # Content frame with scrollable
        self.scrollable_frame = ctk.CTkScrollableFrame(self.top_frame, width=600)
        self.scrollable_frame.pack(side="right", fill="both", expand=True)

        # Progress bar
        self.progress_var = ctk.StringVar()
        self.progress_frame = ctk.CTkFrame(self, height=30)
        self.progress_frame.pack(side="bottom", fill="x")

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, orientation="horizontal")
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        self.progress_label = ctk.CTkLabel(self.progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(side="right", padx=10)

        self.show_novel_spec()

    def show_novel_spec(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.novel_title_label = ctk.CTkLabel(self.scrollable_frame, text="Title", anchor="w")
        self.novel_title_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.novel_title_entry = ctk.CTkEntry(self.scrollable_frame, width=300)
        self.novel_title_entry.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        fields = [
            ("Total Chapters", "totalChapters"),
            ("Pages Per Chapter", "pagesPerChapter"),
            ("Words Per Page", "wordsPerPage"),
            ("Genre", "genre"),
            ("Target Audience", "targetAudience"),
            ("Main Character Name", "mainCharacterName"),
            ("Description", "description")
        ]

        self.entries = {}

        for idx, (label_text, attr) in enumerate(fields, start=1):
            label = ctk.CTkLabel(self.scrollable_frame, text=label_text, anchor="w")
            label.grid(row=idx, column=0, pady=10, padx=10, sticky="w")
            entry = ctk.CTkEntry(self.scrollable_frame, width=300)
            entry.grid(row=idx, column=1, pady=10, padx=10, sticky="ew")
            self.entries[attr] = entry

        self.key_events_button = ctk.CTkButton(self.scrollable_frame, text="Add Key Events", command=self.add_key_events)
        self.key_events_button.grid(row=len(fields) + 1, column=0, pady=10, padx=10, sticky="w")

        self.characters_table = ttk.Treeview(self.scrollable_frame, columns=("Name", "Role", "Age"), show="headings")
        self.characters_table.heading("Name", text="Name")
        self.characters_table.heading("Role", text="Role")
        self.characters_table.heading("Age", text="Age")
        self.characters_table.grid(row=len(fields) + 2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.add_character_button = ctk.CTkButton(self.scrollable_frame, text="Add Character", command=self.add_character)
        self.add_character_button.grid(row=len(fields) + 3, column=0, pady=10, padx=10, sticky="w")

        self.save_button = ctk.CTkButton(self.scrollable_frame, text="Save NovelSpec", command=self.save_novel_spec)
        self.save_button.grid(row=len(fields) + 4, column=0, columnspan=2, pady=10)

    def add_key_events(self):
        dialog = ctk.CTkInputDialog(text="Enter Key Events (comma-separated):", title="Add Key Events")
        key_events_data = dialog.get_input()
        if key_events_data:
            self.key_events = [event.strip() for event in key_events_data.split(",")]

    def add_character(self):
        dialog = ctk.CTkInputDialog(text="Enter Character Details (name,role,age):", title="Add Character")
        character_data = dialog.get_input()
        if character_data:
            try:
                name, role, age = character_data.split(",")
                character = Character(name=name, role=role, age=int(age))
                self.characters_table.insert("", "end", values=(name, role, age))
            except ValueError:
                messagebox.showerror("Error", "Invalid input format. Use: name,role,age")

    def save_novel_spec(self):
        title = self.novel_title_entry.get()
        characters = []
        for row in self.characters_table.get_children():
            values = self.characters_table.item(row, 'values')
            characters.append(Character(name=values[0], role=values[1], age=int(values[2])))

        key_events = getattr(self, 'key_events', [])

        self.novel_spec = NovelSpec(
            title=title,
            totalChapters=int(self.entries["totalChapters"].get() or 0),
            pagesPerChapter=int(self.entries["pagesPerChapter"].get() or 0),
            wordsPerPage=int(self.entries["wordsPerPage"].get() or 0),
            genre=self.entries["genre"].get(),
            targetAudience=self.entries["targetAudience"].get(),
            mainCharacterName=self.entries["mainCharacterName"].get(),
            characters=characters,
            description=self.entries["description"].get(),
            keyEvents=key_events
        )

        with open("novel_spec.yaml", "w") as file:
            yaml.dump(self.novel_spec.__dict__, file)
        messagebox.showinfo("Saved", "NovelSpec saved to novel_spec.yaml")

    def show_safety_spec(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.allow_adult_content = ctk.CTkCheckBox(self.scrollable_frame, text="Allow Adult Content", variable=ctk.BooleanVar(value=self.safety_config.allow_adult_content))
        self.allow_adult_content.grid(row=0, column=0, pady=10, padx=10)

        self.allow_explicit_content = ctk.CTkCheckBox(self.scrollable_frame, text="Allow Explicit Content", variable=ctk.BooleanVar(value=self.safety_config.allow_explicit_content))
        self.allow_explicit_content.grid(row=1, column=0, pady=10, padx=10)

        self.content_rating_label = ctk.CTkLabel(self.scrollable_frame, text="Content Rating")
        self.content_rating_label.grid(row=2, column=0, pady=10, padx=10)
        self.content_rating_entry = ctk.CTkEntry(self.scrollable_frame)
        self.content_rating_entry.insert(0, self.safety_config.content_rating)
        self.content_rating_entry.grid(row=2, column=1, pady=10, padx=10)

        self.save_safety_button = ctk.CTkButton(self.scrollable_frame, text="Save SafetyConfig", command=self.save_safety_config)
        self.save_safety_button.grid(row=3, column=0, columnspan=2, pady=10)

    def save_safety_config(self):
        self.safety_config.allow_adult_content = self.allow_adult_content.variable.get()
        self.safety_config.allow_explicit_content = self.allow_explicit_content.variable.get()
        self.safety_config.content_rating = self.content_rating_entry.get()

        with open("safety_config.yaml", "w") as file:
            yaml.dump(self.safety_config.__dict__, file)
        messagebox.showinfo("Saved", "SafetyConfig saved to safety_config.yaml")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
