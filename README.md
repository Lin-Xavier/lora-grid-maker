# LoRA Grid Maker

LoRA Grid Maker is a small Windows GUI tool for comparing image samples generated during LoRA training. It creates a lossless PNG grid from multiple training sample images, with optional row labels such as `0 steps`, `500 steps`, `1000 steps`, and so on.

## Features

- Drag and drop images or folders
- Set the number of columns before generating the grid
- Add row labels based on training steps
- Optionally label by file name
- Paste images at original pixel size
- No resizing, cropping, or resampling
- Export as PNG

## Lossless behaviour

The program does not resize, crop, or resample source images. Each image is pasted onto a larger PNG canvas at its original pixel size. PNG compression is lossless.

If the source images are JPEG files, their existing JPEG compression artefacts remain, but the grid generation step does not introduce a new JPEG compression pass.

## Download

Download the latest Windows EXE from the Releases page.
