import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import shutil
from pathlib import Path

class PhotoSorter:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Decade Sorter")
        
        # Dictionary mapping keys to destination folders
        self.decade_map = {
            '1': '1940-1969',
            '2': "1970's",
            '3': "1980's",
            '4': '1990-1994',
            '5': '1995',
            '6': '1996',
            '7': '1997',
            '8': '1998',
            '9': '1999',
            '0': '2000'
        }
        
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
        # Left-side instructions showing number-to-decade mapping
        decade_text = "\n".join([f"{key}: {value}" for key, value in self.decade_map.items()])
        self.decade_instructions = tk.Label(root, 
                                          text=decade_text,
                                          justify="left",
                                          font=("Arial", 12))
        self.decade_instructions.pack(side="left", padx=10, pady=10)  # Left side with padding
        
        # Canvas in the middle
        self.canvas = tk.Canvas(root, width=800, height=600)
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
            self.canvas.create_text(400, 300, text="No JPG images found in project folder!", font=("Arial", 20))
    
    def show_image(self):
        if not self.image_files or self.current_index < 0 or self.current_index >= len(self.image_files):
            self.canvas.create_text(400, 300, text="No more images to sort!", font=("Arial", 20))
            return
            
        image_path = self.image_files[self.current_index]
        img = Image.open(image_path)
        
        # Resize image to fit canvas while maintaining aspect ratio
        img.thumbnail((800, 600))
        self.photo = ImageTk.PhotoImage(img)
        
        self.canvas.delete("all")
        self.canvas.create_image(400, 300, image=self.photo)
        self.canvas.create_text(400, 20, text=f"Image {self.current_index + 1}/{len(self.image_files)}: {image_path.name}",
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
