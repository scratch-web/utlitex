# Utlitex

Utlitex is a collection of utilities designed to make working with Roblox and Vortex Studio a little easier. It combines several commonly used tools into a single desktop application with a simple interface, drag-and-drop support, and built-in output previews.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

### Luau Converter

Converts a `model.json` file into Luau code that can be pasted directly into Roblox Studio.

* Drag-and-drop file support
* File browser support
* Syntax-highlighted output
* Built-in output preview

---

### Vortex Converter

Converts Roblox `.rbxmx` models into the JSON format used by Vortex Studio.

> **Note**
> This converter is still experimental and may not produce perfect results in every situation.

**Features**

* `.rbxmx` model import
* JSON output preview
* Drag-and-drop support

---

### Custom Cursor

Lets you replace your Windows cursor using your own image.

* Uses `cursor.png`
* Automatically creates a `.cur` file when needed
* Start or stop the cursor replacement at any time
* Restore the default cursor with a single click

---

## Installation

1. Download the latest release.
2. Extract the archive.
3. Keep the included `bin` folder in the same directory as the executable.
4. Launch the application.

## Requirements

* Windows 10 or Windows 11
* Python 3.x (only required when running from source)

Install the required dependency:

```bash
python -m pip install tkinterdnd2
```

## Credits

* **Programming:** @nieotica
* **Default Cursor:** @friendlysmiles (Discord)

## License

This project is licensed under the MIT License.
