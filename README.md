# LoRA Step Grid Maker, Qt portable build

This version avoids tkinter entirely.

The earlier tkinter build may fail with:

```text
ModuleNotFoundError: No module named 'tkinter'
```

because Python's Windows embeddable distribution normally does not include Tcl/Tk.

This package instead uses PySide6/Qt. PyInstaller bundles the Qt runtime into the final EXE, so the target computer does not need Python or tkinter.

## Build

1. Extract the whole ZIP.
2. Double click:

```bat
build_portable_qt_no_python_install.bat
```

The final file will be:

```text
dist\LoRA_Grid_Maker.exe
```

You can copy only that EXE to another Windows computer.

## Notes

The first build needs internet access because it downloads portable Python and Python packages.

The generated EXE may be relatively large because it contains:
- Python runtime
- PySide6/Qt GUI runtime
- Pillow
- the app code

## Lossless behaviour

The program does not resize, crop, or resample source images. It pastes each image onto a larger PNG canvas at original pixel size. PNG compression is lossless.

If the source images are JPEG, their existing JPEG artefacts remain, but the grid generation step does not add another JPEG compression pass.
