# v0.3
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import shutil
from pathlib import Path

# Adjust these dates to your desired set of dates to bin.
# Adjusting these will change the folders created for your photo binning pleasure.
date1 = '1940-1969'
date2 = "1970's"
date3 = "1980's"
date4 = '1990-1994'
date5 = '1995'
date6 = '1996'
date7 = '1997'
date8 = '1998'
date9 = '1999'
date0 = '2000'

# You can use these to adjust the keys mapped to your binning but I recomment to leave them as they are.
DATE_MAP = {
    '1': date1,
    '2': date2,
    '3': date3,
    '4': date4,
    '5': date5,
    '6': date6,
    '7': date7,
    '8': date8,
    '9': date9,
    '0': date0
}

# Canvas dimensions
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

class PhotoSorter:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Decade Sorter")
        
        # Use the date map
        self.decade_map = DATE_MAP
        
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
        
        # Add settings button
        self.settings_button = tk.Button(root, text="Settings", command=self.open_settings_window)
        self.settings_button.pack(side="bottom", pady=10)
    
    def open_settings_window(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Edit Key-Date Mappings")
        
        entries = {}  # To store entry widgets for later

        row = 0
        for key, value in self.decade_map.items():
            tk.Label(settings_win, text=f"Key {key}:").grid(row=row, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(settings_win, width=20)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=5, pady=2)
            entries[key] = entry
            row += 1

        def save_and_close():
            # Update mapping
            self.decade_map = {k: e.get().strip() for k, e in entries.items()}
            self.update_key_bindings()
            self.update_mapping_label()
            settings_win.destroy()

        tk.Button(settings_win, text="Save", command=save_and_close).grid(row=row, column=0, columnspan=2, pady=10)
    def update_key_bindings(self):
        # Unbind all digit keys first
        for i in range(10):
            self.root.unbind(str(i))
        # Rebind according to new map
        for key in self.decade_map:
            self.root.bind(key, self.move_image)
            
    def update_mapping_label(self):
        decade_text = "\n".join([f"{key}: {value}" for key, value in self.decade_map.items()])
        self.decade_instructions.config(text=decade_text)


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
        
        if self.image_files:
            self.show_image()
        else:
            self.show_image()  # Show "no more images" message
    
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

def main():
    root = tk.Tk()
    app = PhotoSorter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
