import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

class expressionEditor:
    def __init__(self, root, directory):
        self.root = root
        self.directory = directory
        self.files = [f for f in os.listdir(directory) if f.lower().endswith(".json")]
        self.index = 0
        self.image_label = None
        self.entry = None
        self.current_json_path = None
        self.current_image_path = None
        self.thumbnails = {}  # Cache for thumbnails
        self.sidebar_buttons = []  # Store sidebar button references

        if not self.files:
            messagebox.showerror("Error", "No JSON files found in this directory.")
            root.destroy()
            return

        self.setup_ui()
        self.load_thumbnails()
        self.load_file()

    def setup_ui(self):
        # Create main frame with sidebar and content
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar for thumbnails
        sidebar_frame = tk.Frame(main_frame, width=150, bg='lightgray')
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        sidebar_frame.pack_propagate(False)  # Maintain fixed width

        # Scrollable frame for thumbnails
        canvas = tk.Canvas(sidebar_frame, bg='lightgray')
        scrollbar = ttk.Scrollbar(sidebar_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='lightgray')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Main content area
        content_frame = tk.Frame(main_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        # Image display
        self.image_label = tk.Label(content_frame)
        self.image_label.pack(padx=10, pady=10)

        # Entry field
        self.entry_label = tk.Label(content_frame, text="expression:")
        self.entry_label.pack()

        self.entry = tk.Entry(content_frame, width=50)
        self.entry.pack(padx=10, pady=5)

        # Navigation buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)

        self.prev_button = tk.Button(button_frame, text="Previous", command=self.previous_file)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.save_next_button = tk.Button(button_frame, text="Save + Next", command=self.save_and_next)
        self.save_next_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="Save", command=self.save_current)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Bind mouse wheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

    def load_thumbnails(self):
        """Load and create thumbnail buttons for all files"""
        for i, json_filename in enumerate(self.files):
            # Find corresponding image
            basename, _ = os.path.splitext(json_filename)
            image_path = None
            for ext in [".png", ".jpg", ".jpeg"]:
                candidate = os.path.join(self.directory, basename + ext)
                if os.path.exists(candidate):
                    image_path = candidate
                    break

            # Create thumbnail
            if image_path:
                try:
                    img = Image.open(image_path)
                    img.thumbnail((120, 120))  # Small thumbnail for sidebar
                    thumbnail = ImageTk.PhotoImage(img)
                    self.thumbnails[i] = thumbnail
                except Exception as e:
                    print(f"Error loading thumbnail for {json_filename}: {e}")
                    self.thumbnails[i] = None
            else:
                self.thumbnails[i] = None

            # Create button frame
            button_frame = tk.Frame(self.scrollable_frame, bg='lightgray')
            button_frame.pack(pady=2, padx=2, fill=tk.X)

            # Create clickable thumbnail button
            if self.thumbnails[i]:
                thumb_button = tk.Button(
                    button_frame,
                    image=self.thumbnails[i],
                    command=lambda idx=i: self.jump_to_file(idx),
                    relief=tk.RAISED,
                    borderwidth=2
                )
            else:
                thumb_button = tk.Button(
                    button_frame,
                    text="No Image",
                    command=lambda idx=i: self.jump_to_file(idx),
                    relief=tk.RAISED,
                    borderwidth=2,
                    width=15,
                    height=3
                )

            thumb_button.pack()

            # Add filename label
            filename_label = tk.Label(
                button_frame,
                text=basename[:15] + "..." if len(basename) > 15 else basename,
                bg='lightgray',
                font=('Arial', 8)
            )
            filename_label.pack()

            self.sidebar_buttons.append(thumb_button)

    def update_sidebar_selection(self):
        """Update the visual selection in the sidebar"""
        for i, button in enumerate(self.sidebar_buttons):
            if i == self.index:
                button.config(relief=tk.SUNKEN, borderwidth=3)
            else:
                button.config(relief=tk.RAISED, borderwidth=2)

    def jump_to_file(self, index):
        """Jump to a specific file by index"""
        if 0 <= index < len(self.files):
            self.save_current()  # Save current changes before jumping
            self.index = index
            self.load_file()

    def load_file(self):
        if self.index >= len(self.files):
            messagebox.showinfo("Done", "All files processed!")
            self.root.destroy()
            return

        json_filename = self.files[self.index]
        self.current_json_path = os.path.join(self.directory, json_filename)

        # Assume image has same name but different extension
        basename, _ = os.path.splitext(json_filename)
        for ext in [".png", ".jpg", ".jpeg"]:
            candidate = os.path.join(self.directory, basename + ext)
            if os.path.exists(candidate):
                self.current_image_path = candidate
                break
        else:
            self.current_image_path = None

        # Load JSON (handle UTF-8 BOM)
        with open(self.current_json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        # Fill entry
        expression_value = data.get("expression", "")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, expression_value)

        # Show image if found
        if self.current_image_path:
            img = Image.open(self.current_image_path)
            img.thumbnail((600, 600))  # resize to fit
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_img, text="")
        else:
            self.image_label.config(image="", text="[No image found]")

        # Update navigation button states
        self.prev_button.config(state=tk.NORMAL if self.index > 0 else tk.DISABLED)
        self.save_next_button.config(state=tk.NORMAL if self.index < len(self.files) - 1 else tk.DISABLED)

        # Update sidebar selection
        self.update_sidebar_selection()

        self.root.title(f"Editing {json_filename} ({self.index+1}/{len(self.files)})")

    def save_current(self):
        """Save current file without navigating"""
        if self.current_json_path:
            with open(self.current_json_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)

            data["expression"] = self.entry.get()

            with open(self.current_json_path, "w", encoding="utf-8-sig") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def save_and_next(self):
        """Save current file and move to next"""
        self.save_current()
        if self.index < len(self.files) - 1:
            self.index += 1
            self.load_file()
        else:
            messagebox.showinfo("Done", "All files processed!")

    def previous_file(self):
        """Move to previous file"""
        if self.index > 0:
            self.save_current()  # Save current changes before moving
            self.index -= 1
            self.load_file()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x800")
    root.title("expression JSON Editor")

    directory = os.getcwd()  # current folder
    app = expressionEditor(root, directory)

    root.mainloop()