# Photo Decade Sorter

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
### Option 2: There is no Option 2
