# v0.4 - with settings loader
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import shutil
from pathlib import Path
import configparser

# Canvas dimensions
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        return None
    config.read(CONFIG_FILE)
    if 'Mappings' not in config:
        return None
    mapping = dict(config['Mappings'])
    if len(mapping) != 10 or not all(k in mapping for k in map(str, range(10))):
        return None
    return mapping

def save_config(mapping):
    config = configparser.ConfigParser()
    config['Mappings'] = mapping
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

def open_settings_window(root, on_save_callback):
    window = tk.Toplevel(root)
    window.title("Initial Setup: Key-Date Mappings")

    instructions = tk.Label(window, text="Enter a label for each key (0–9):")
    instructions.grid(row=0, column=0, columnspan=2, pady=(10, 0))

    entries = {}
    for i in range(10):
        key = str(i)
        tk.Label(window, text=f"Key {key}:").grid(row=i+1, column=0, sticky="e", padx=5, pady=2)
        entry = tk.Entry(window, width=25)
        entry.grid(row=i+1, column=1, padx=5, pady=2)
        entries[key] = entry

    def on_save():
        mapping = {k: e.get().strip() for k, e in entries.items()}
        if not all(mapping.values()):
            messagebox.showerror("Missing Value", "All keys must have a label.")
            return
        save_config(mapping)
        window.destroy()
        on_save_callback(mapping)

    save_btn = tk.Button(window, text="Save and Start", command=on_save)
    save_btn.grid(row=11, column=0, columnspan=2, pady=10)

class PhotoSorter:
    def __init__(self, root, decade_map):
        self.root = root
        self.root.title("Photo Decade Sorter")
        
        # Add a traditional menu bar (File, Settings)
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Folder", command=self.open_new_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Configuration", command=self.open_settings)
        settings_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        self.root.config(menu=menubar)

        # Use the date map
        self.decade_map = decade_map

        # Select project folder
        self.project_dir = Path(filedialog.askdirectory(title="Select Project Folder Containing Unsorted Photos"))
        if not self.project_dir or not self.project_dir.exists():
            raise Exception("No valid project folder selected. Exiting.")

        # Set up source and destination directories
        self.source_dir = self.project_dir  # Unsorted photos are in the root
        self.base_dest_dir = self.project_dir  # Date folders are in the same root

        # Create date folders if they don’t exist
        for folder in self.decade_map.values():
            (self.base_dest_dir / folder).mkdir(exist_ok=True)

        # Get list of image files (only JPG in root)
        self.image_files = [f for f in self.source_dir.iterdir()
                            if f.suffix.lower() in ('.jpg', '.jpeg') and f.is_file()]
        self.current_index = 0
        self.last_moved = None  # To store last moved file info for undo

        # Set up GUI
        # Left-side instructions showing number-to-date mapping
        decade_text = "\n".join([f"{key}: {value}" for key, value in self.decade_map.items()])
        self.decade_instructions = tk.Label(root,
                                            text=decade_text,
                                            justify="left",
                                            font=("Arial", 12))
        self.decade_instructions.pack(side="left", padx=10, pady=10)  # Left side with padding

        # Canvas in the middle
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack(side="left")  # Canvas next to left instructions

        # Right-side instructions for controls
        self.instructions = tk.Label(root,
                                     text="Use 0-9 to sort\n← to undo/previous\n→ for next",
                                     justify="left",
                                     font=("Arial", 12))
        self.instructions.pack(side="right", padx=10, pady=10)  # Right side with padding

        # Bind keys
        self.root.bind('<Left>', self.previous_or_undo)
        self.root.bind('<Right>', self.next_image)
        for key in self.decade_map:
            self.root.bind(key, self.move_image)

        # Show first image if available
        if self.image_files:
            self.show_image()
        else:
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                                    text="No JPG images found in project folder!", font=("Arial", 20))

    def show_image(self):
        if not self.image_files or self.current_index < 0 or self.current_index >= len(self.image_files):
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2,
                                    text="No more images to sort!", font=("Arial", 20))
            return

        image_path = self.image_files[self.current_index]
        img = Image.open(image_path)

        # Resize image to fit canvas while maintaining aspect ratio
        img.thumbnail((CANVAS_WIDTH, CANVAS_HEIGHT))
        self.photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, image=self.photo)
        self.canvas.create_text(CANVAS_WIDTH // 2, 20,
                                text=f"Image {self.current_index + 1}/{len(self.image_files)}: {image_path.name}",
                                font=("Arial", 12))

    def move_image(self, event):
        if not self.image_files or self.current_index >= len(self.image_files):
            return

        key = event.keysym
        if key not in self.decade_map:
            return

        source_path = self.image_files[self.current_index]
        dest_folder = self.base_dest_dir / self.decade_map[key]

        # Handle duplicate filenames
        dest_path = dest_folder / source_path.name
        base_name = source_path.stem  # Filename without extension
        extension = source_path.suffix  # Extension (e.g., .jpg)
        counter = 1

        while dest_path.exists():
            new_name = f"{base_name}-{counter}{extension}"
            dest_path = dest_folder / new_name
            counter += 1

        # Move the file
        shutil.move(source_path, dest_path)

        # Store move info for potential undo
        self.last_moved = (source_path, dest_path)

        # Remove from list and update display
        del self.image_files[self.current_index]
        if self.current_index >= len(self.image_files):
            self.current_index = len(self.image_files) - 1

        self.show_image()

    def previous_or_undo(self, event):
        if self.last_moved:
            # Undo last move
            source_path, dest_path = self.last_moved
            shutil.move(dest_path, source_path)
            self.image_files.insert(self.current_index, source_path)
            self.last_moved = None
            self.show_image()
        elif self.current_index > 0:
            # Go to previous image
            self.current_index -= 1
            self.show_image()

    def next_image(self, event):
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_image()
    def open_new_folder(self):
        new_dir = Path(filedialog.askdirectory(title="Select New Project Folder"))
        if new_dir and new_dir.exists():
            self.project_dir = new_dir
            self.source_dir = self.project_dir
            self.base_dest_dir = self.project_dir

            # Rebuild date folders
            for folder in self.decade_map.values():
                (self.base_dest_dir / folder).mkdir(exist_ok=True)

            # Reload images
            self.image_files = [f for f in self.source_dir.iterdir()
                                if f.suffix.lower() in ('.jpg', '.jpeg') and f.is_file()]
            self.current_index = 0
            self.last_moved = None
            self.show_image()

    def open_settings(self):
        def apply_and_reload(mapping):
            self.decade_map = mapping

            # Rebuild folders
            for folder in self.decade_map.values():
                (self.base_dest_dir / folder).mkdir(exist_ok=True)

            # Rebind keys
            for key in map(str, range(10)):
                self.root.bind(key, lambda e, k=key: self.move_image(e))

            # Update label text
            decade_text = "\n".join([f"{key}: {value}" for key, value in self.decade_map.items()])
            self.decade_instructions.config(text=decade_text)

        open_settings_window(self.root, apply_and_reload)

    def show_about(self):
        messagebox.showinfo("About", "Photo Decade Sorter\nVersion 0.4\nBuilt with ❤️ using Python + Tkinter.")


def main():
    root = tk.Tk()
    root.withdraw()  # Hide root until ready

    def launch_app(mapping):
        root.deiconify()
        PhotoSorter(root, mapping)

    mapping = load_config()
    if not mapping:
        open_settings_window(root, on_save_callback=launch_app)
    else:
        launch_app(mapping)

    root.mainloop()


if __name__ == "__main__":
    main()
