# LoRA Grid Maker (Portable)

LoRA Grid Maker is a small Windows GUI tool for comparing image samples generated during LoRA training. It creates a lossless PNG grid from multiple training sample images, with optional row labels such as `0 steps`, `500 steps`, `1000 steps`, and so on.


This version avoids tkinter entirely and instead uses PySide6/Qt. PyInstaller bundles the Qt runtime into the final EXE, so the target computer does not need Python or tkinter.

## Features

- Drag and drop images or folders

- Set the number of columns before generating the grid

- Add row labels based on training steps

- Optionally label by file name

- Paste images at original pixel size

- No resizing, cropping, or resampling

- Export as PNG

## Lossless

The program does not resize, crop, or resample source images. Each image is pasted onto a larger PNG canvas at its original pixel size. PNG compression is lossless.

If the source images are JPEG files, their existing JPEG compression artefacts remain, but the grid generation step does not introduce a new JPEG compression pass.


## Install
### Build from source

This project can be built without installing Python system-wide. The build script downloads the official Windows embeddable Python into a local portable_python folder, installs dependencies there, and freezes the app into a single EXE.
1. Extract the whole ZIP.
2. Double click:

```bat
build_portable_qt_no_python_install.bat
```

3. The final file will be:

```text
dist\LoRA_Grid_Maker.exe
```

You can copy only that EXE to another Windows computer.

Requirements for building:
* Windows 10 or later
* Internet access during the first build

Source dependencies:
* Pillow
* PySide6
* PyInstaller

### Download EXE
Alternatively download the latest Windows EXE from the Releases page.
