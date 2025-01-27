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
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

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

        fields = [
            ("Title", "title"),
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
            entry = ctk.CTkEntry(self.scrollable_frame)
            entry.grid(row=idx, column=1, pady=10, padx=10, sticky="ew")
            self.entries[attr] = entry

        self.key_events_button = ctk.CTkButton(self.scrollable_frame, text="Add Key Events", command=self.add_key_events)
        self.key_events_button.grid(row=len(fields) + 1, column=0, pady=10, padx=10, sticky="w")

        self.characters_table = ttk.Treeview(self.scrollable_frame, columns=("Name", "Role", "Age"), show="headings")
        self.characters_table.heading("Name", text="Name")
        self.characters_table.heading("Role", text="Role")
        self.characters_table.heading("Age", text="Age")
        self.characters_table.grid(row=len(fields) + 2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.add_character_button = ctk.CTkButton(self.scrollable_frame, text="Add Character", command=self.add_character_popup)
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

    def add_character_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Character")
        popup.geometry("400x600")
        # Enable Esc key to close popup
        popup.bind("<Escape>", lambda event: popup.destroy())
        
        # Layout Grid Configuration
        popup.columnconfigure(1, weight=1)

        # Character Basic Info
        name_label = ctk.CTkLabel(popup, text="Name", anchor="w", width=200)
        name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_entry = ctk.CTkEntry(popup)
        name_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)

        role_label = ctk.CTkLabel(popup, text="Role", anchor="w")
        role_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        role_entry = ctk.CTkEntry(popup)
        role_entry.grid(row=1, column=1, sticky="we", padx=5, pady=5)

        age_label = ctk.CTkLabel(popup, text="Age", anchor="w")
        age_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        age_entry = ctk.CTkEntry(popup)
        age_entry.grid(row=2, column=1, sticky="we", padx=5, pady=5)

        # Traits Section
        traits_label = ctk.CTkLabel(popup, text="Traits (trait: description)", anchor="w")
        traits_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        traits_text = ctk.CTkTextbox(popup, height=60)
        traits_text.grid(row=3, column=1, columnspan=2, sticky="we", padx=5, pady=5)

        # Arc Section
        arc_label = ctk.CTkLabel(popup, text="Character Arc")
        arc_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        starting_point_label = ctk.CTkLabel(popup, text="Starting Point", anchor="w")
        starting_point_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        starting_point_entry = ctk.CTkEntry(popup)
        starting_point_entry.grid(row=5, column=1, sticky="we", padx=5, pady=5)

        mid_point_label = ctk.CTkLabel(popup, text="Mid Point", anchor="w")
        mid_point_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)
        mid_point_entry = ctk.CTkEntry(popup)
        mid_point_entry.grid(row=6, column=1, sticky="we", padx=5, pady=5)

        ending_point_label = ctk.CTkLabel(popup, text="Ending Point", anchor="w")
        ending_point_label.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        ending_point_entry = ctk.CTkEntry(popup)
        ending_point_entry.grid(row=7, column=1, sticky="we", padx=5, pady=5)

        major_events_label = ctk.CTkLabel(popup, text="Major Events (comma-separated)", anchor="w")
        major_events_label.grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        major_events_entry = ctk.CTkEntry(popup)
        major_events_entry.grid(row=8, column=1, columnspan=2, sticky="we", padx=5, pady=5)

        # Relationships Section
        relationships_label = ctk.CTkLabel(popup, text="Relationships", anchor="w")
        relationships_label.grid(row=9, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        relationship_text = ctk.CTkTextbox(popup, height=60)
        relationship_text.grid(row=9, column=1, columnspan=2, sticky="we", padx=5, pady=5)

        # Save Button
        save_button = ctk.CTkButton(popup, text="Save", command=lambda: self.save_character(
            name_entry.get(), role_entry.get(), age_entry.get(),
            traits_text.get("1.0", "end-1c"),
            starting_point_entry.get(), mid_point_entry.get(), ending_point_entry.get(), major_events_entry.get(),
            relationship_text.get("1.0", "end-1c"),
            popup
        ))
        save_button.grid(row=10, column=0, columnspan=2, pady=10)

    def save_novel_spec(self):
        title = self.entries["title"].get()
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

        with open("novel_spec.yml", "w") as file:
            yaml.dump(self.novel_spec.__dict__, file)
        messagebox.showinfo("Saved", "NovelSpec saved to novel_spec.yml")

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
