<p align="center">
  <img src="https://raw.githubusercontent.com/mcfixstuff/Easy-Photo-Binner/main/logo.png" alt="Easy Photo Binner Logo" width="25%"/>
</p>
# Easy Photo Binner

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

Photo Decade Sorter is a simple Python-based tool that helps you organize your JPG photos into folders based on their decade or year. The program displays each photo from a selected folder, allowing you to assign it to a decade or specific year using number keys (0-9). It features an intuitive interface with keyboard controls and handles duplicate filenames automatically.

## Features

- Sort JPG photos into customizable decade/year folders.
- Keyboard controls:
  - Numbers `0-9`: Assign a photo to a specific folder.
  - Left arrow (`←`): Undo the last move or go to the previous photo.
  - Right arrow (`→`): Skip to the next photo without sorting.
- Automatically appends `-1`, `-2`, etc., to filenames if duplicates exist in the destination folder.
- Displays instructions and date mappings in the GUI for easy reference.

## Prerequisites

- **Windows, macOS, or Linux** (tested on Windows).
- **Python 3.x** (if running from source).
- **Pillow** library for image handling.

## Installation

### Option 1: Running from Source (Developers/Users with Python)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mcfixstuff/Easy-Photo-Binner.git
   cd Easy-Photo-Binner
   main.py
### Option 2: There is no Option 2

## Instruction Manual

### How to Use Easy Photo Binner

1. **Prepare Your Photos**:
   - Place all unsorted JPG photos in a single folder (the "root folder"). For example:
   - MyPhotos/
├── photo1.jpg
├── photo2.jpg
├── photo3.jpg

- **Important**: The program only scans the root folder for `.jpg` and `.jpeg` files. It **does not** look inside subfolders, so ensure all photos you want to sort are directly in the root folder, not nested in subdirectories.

2. **Launch the Program**:
- Run `python main.py` from the command line after navigating to the `Easy-Photo-Binner` directory.
- A file dialog will appear. Navigate to and select your root folder (e.g., `MyPhotos`). Click "Open" or "OK" to confirm.

3. **Understanding Folder Creation**:
- The program automatically creates folders in the root folder based on the dates assigned to numbers 0-9 (e.g., `1940-1969`, `1970's`, etc.).
- If a folder doesn’t exist when you assign a photo to it (e.g., by pressing `1` for `1940-1969`), it will be created instantly. For example:
- Before: `MyPhotos/` contains only photos.
- After pressing `1`: `MyPhotos/1940-1969/` is created, and the photo is moved there.

4. **Sorting Photos**:
- **Interface Layout**:
- **Left**: Shows which number (0-9) corresponds to which date (e.g., "1: 1940-1969").
- **Middle**: Displays the current photo with its filename and count (e.g., "Image 1/5: photo1.jpg").
- **Right**: Lists controls (`0-9 to sort`, `← to undo/previous`, `→ for next`).
- **Controls**:
- Press a number (`0-9`) to move the current photo to the corresponding folder.
- Press `←` to undo the last move (returns the photo to the root folder) or go to the previous photo if no move was made.
- Press `→` to skip to the next photo without sorting it (leaves it in the root folder).

5. **Handling Duplicates**:
- If a photo’s filename already exists in the destination folder (e.g., `1970's/photo1.jpg`), it will be renamed with a suffix like `photo1-1.jpg`, `photo1-2.jpg`, etc.

6. **Finishing Up**:
- When all photos are sorted or skipped, the program displays "No more images to sort!" You can close the window to exit.

### Example Workflow

- **Start**: `MyPhotos/` contains `photo1.jpg`, `photo2.jpg`, `photo3.jpg`.
- Select `MyPhotos/` in the file dialog.
- Press `2` for `photo1.jpg` → `MyPhotos/1970's/photo1.jpg` is created.
- Press `9` for `photo2.jpg` → `MyPhotos/1999/photo2.jpg` is created.
- Press `→` for `photo3.jpg` → Stays in `MyPhotos/photo3.jpg`.
