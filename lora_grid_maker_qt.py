
import sys
import math
import re
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QRadioButton,
    QButtonGroup,
)


SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def natural_key(path: Path):
    parts = re.split(r"(\d+)", path.name.lower())
    return [int(p) if p.isdigit() else p for p in parts]


def collect_images(paths: List[Path]) -> List[Path]:
    out = []
    for p in paths:
        if p.is_dir():
            for child in p.rglob("*"):
                if child.suffix.lower() in SUPPORTED_EXTS:
                    out.append(child.resolve())
        elif p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            out.append(p.resolve())
    return sorted(set(out), key=natural_key)


def load_font(size: int):
    candidates = [
        "arial.ttf",
        "Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for f in candidates:
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            pass
    return ImageFont.load_default()


def make_grid(
    files: List[Path],
    output_path: Path,
    cols: int,
    first_step: int,
    step_interval: int,
    label_mode: str,
    padding: int,
    label_height: int,
    font_size: int,
    bg_rgba: Tuple[int, int, int, int] = (255, 255, 255, 255),
):
    if not files:
        raise ValueError("No supported image files were provided.")
    if cols < 1:
        raise ValueError("Columns must be at least 1.")

    images = []
    for f in files:
        im = Image.open(f)
        if im.mode not in ("RGBA", "RGB"):
            im = im.convert("RGBA")
        else:
            im = im.copy()
        images.append(im)

    cell_w = max(im.width for im in images)
    cell_h_image = max(im.height for im in images)
    label_area = label_height if label_mode != "none" else 0
    cell_h = cell_h_image + label_area
    rows = math.ceil(len(images) / cols)

    grid_w = cols * cell_w + (cols + 1) * padding
    grid_h = rows * cell_h + (rows + 1) * padding

    canvas = Image.new("RGBA", (grid_w, grid_h), bg_rgba)
    draw = ImageDraw.Draw(canvas)
    font = load_font(font_size)

    for i, (im, f) in enumerate(zip(images, files)):
        row = i // cols
        col = i % cols

        x0 = padding + col * (cell_w + padding)
        y0 = padding + row * (cell_h + padding)

        if label_mode != "none":
            if label_mode == "row_steps":
                label = f"{first_step + row * step_interval} steps"
            elif label_mode == "file_name":
                label = f.stem
            elif label_mode == "both":
                label = f"{first_step + row * step_interval} steps | {f.stem}"
            else:
                label = ""

            if label:
                draw.text((x0, y0), label, fill=(0, 0, 0, 255), font=font)

        img_x = x0 + (cell_w - im.width) // 2
        img_y = y0 + label_area + (cell_h_image - im.height) // 2

        if im.mode == "RGBA":
            canvas.alpha_composite(im, (img_x, img_y))
        else:
            canvas.paste(im, (img_x, img_y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", compress_level=0)


class DropTextEdit(QTextEdit):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.setAcceptDrops(True)
        self.setReadOnly(True)
        self.setPlaceholderText("Drop images or folders here.")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local:
                paths.append(Path(local))
        self.parent_app.add_paths(paths)
        event.acceptProposedAction()


class MainWindow(QWidget):
    def __init__(self, initial_paths=None):
        super().__init__()
        self.files: List[Path] = []
        self.setWindowTitle("LoRA Step Grid Maker")
        self.resize(820, 600)

        layout = QVBoxLayout(self)

        title = QLabel("LoRA Step Grid Maker")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(title)

        desc = QLabel(
            "Drag images or folders into the box below. Images are pasted at original pixel size. Output is PNG."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.drop_box = DropTextEdit(self)
        self.drop_box.setText("Drop images or folders here.\n\nSupported: PNG, JPG, JPEG, WEBP, BMP, TIFF")
        layout.addWidget(self.drop_box, stretch=1)

        btn_row = QHBoxLayout()
        self.select_images_btn = QPushButton("Select Images")
        self.select_folder_btn = QPushButton("Select Folder")
        self.clear_btn = QPushButton("Clear")
        self.select_images_btn.clicked.connect(self.select_images)
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.clear_btn.clicked.connect(self.clear_files)
        btn_row.addWidget(self.select_images_btn)
        btn_row.addWidget(self.select_folder_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        settings = QGroupBox("Grid settings")
        settings_layout = QVBoxLayout(settings)

        form_row = QHBoxLayout()

        form1 = QFormLayout()
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 999)
        self.cols_spin.setValue(4)
        self.first_step_spin = QSpinBox()
        self.first_step_spin.setRange(-999999999, 999999999)
        self.first_step_spin.setValue(0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(-999999999, 999999999)
        self.interval_spin.setValue(500)
        form1.addRow("Columns", self.cols_spin)
        form1.addRow("First row step", self.first_step_spin)
        form1.addRow("Step interval per row", self.interval_spin)

        form2 = QFormLayout()
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 10000)
        self.padding_spin.setValue(8)
        self.label_height_spin = QSpinBox()
        self.label_height_spin.setRange(0, 10000)
        self.label_height_spin.setValue(30)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 500)
        self.font_size_spin.setValue(16)
        form2.addRow("Padding px", self.padding_spin)
        form2.addRow("Label height px", self.label_height_spin)
        form2.addRow("Font size", self.font_size_spin)

        form_row.addLayout(form1)
        form_row.addSpacing(30)
        form_row.addLayout(form2)
        form_row.addStretch(1)
        settings_layout.addLayout(form_row)

        label_row = QHBoxLayout()
        label_row.addWidget(QLabel("Labels"))
        self.label_group = QButtonGroup(self)

        self.rb_row_steps = QRadioButton("Row steps")
        self.rb_file_name = QRadioButton("File name")
        self.rb_both = QRadioButton("Steps + file name")
        self.rb_none = QRadioButton("No labels")
        self.rb_row_steps.setChecked(True)

        for rb, mode in [
            (self.rb_row_steps, "row_steps"),
            (self.rb_file_name, "file_name"),
            (self.rb_both, "both"),
            (self.rb_none, "none"),
        ]:
            self.label_group.addButton(rb)
            rb.setProperty("mode", mode)
            label_row.addWidget(rb)

        label_row.addStretch(1)
        settings_layout.addLayout(label_row)

        layout.addWidget(settings)

        bottom = QHBoxLayout()
        self.status = QLabel("No images loaded.")
        self.generate_btn = QPushButton("Generate PNG Grid")
        self.generate_btn.setStyleSheet("font-weight: 600;")
        self.generate_btn.clicked.connect(self.generate)
        bottom.addWidget(self.status)
        bottom.addStretch(1)
        bottom.addWidget(self.generate_btn)
        layout.addLayout(bottom)

        if initial_paths:
            self.add_paths([Path(p) for p in initial_paths])

    def current_label_mode(self):
        checked = self.label_group.checkedButton()
        return checked.property("mode") if checked else "row_steps"

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select images",
            "",
            "Image files (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;All files (*.*)",
        )
        self.add_paths([Path(f) for f in files])

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder containing images")
        if folder:
            self.add_paths([Path(folder)])

    def clear_files(self):
        self.files = []
        self.refresh_file_list()

    def add_paths(self, paths: List[Path]):
        images = collect_images(paths)
        current = set(self.files)
        for f in images:
            if f not in current:
                self.files.append(f)
        self.files = sorted(self.files, key=natural_key)
        self.refresh_file_list()

    def refresh_file_list(self):
        if not self.files:
            self.drop_box.setText("Drop images or folders here.\n\nSupported: PNG, JPG, JPEG, WEBP, BMP, TIFF")
        else:
            lines = [f"{idx:03d}. {f}" for idx, f in enumerate(self.files, start=1)]
            self.drop_box.setText("\n".join(lines))
        self.status.setText(f"{len(self.files)} image(s) loaded.")

    def generate(self):
        try:
            if not self.files:
                raise ValueError("Please add images first.")

            out, _ = QFileDialog.getSaveFileName(
                self,
                "Save grid as PNG",
                "lora_grid.png",
                "PNG image (*.png)",
            )
            if not out:
                return
            if not out.lower().endswith(".png"):
                out += ".png"

            make_grid(
                files=self.files,
                output_path=Path(out),
                cols=self.cols_spin.value(),
                first_step=self.first_step_spin.value(),
                step_interval=self.interval_spin.value(),
                label_mode=self.current_label_mode(),
                padding=self.padding_spin.value(),
                label_height=self.label_height_spin.value(),
                font_size=self.font_size_spin.value(),
            )
            QMessageBox.information(self, "Done", f"Saved lossless PNG grid:\n{out}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def main():
    app = QApplication(sys.argv)
    window = MainWindow(initial_paths=sys.argv[1:])
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
