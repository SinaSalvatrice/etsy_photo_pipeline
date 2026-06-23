from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


def find_project_root(start: Path) -> Path:
    """Find the project root so src imports work from different launch locations."""
    candidates = [start, Path.cwd()]

    env_root = os.environ.get("ETSY_PHOTO_PIPELINE_ROOT")
    if env_root:
        candidates.insert(0, Path(env_root))

    if getattr(sys, "frozen", False):
        candidates.extend(
            [
                Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)),
                Path(sys.executable).parent,
            ]
        )

    checked: list[Path] = []
    for candidate in candidates:
        current = candidate.resolve()
        for folder in (current, *current.parents):
            if folder in checked:
                continue
            checked.append(folder)

            has_configs = (folder / "configs").is_dir()
            has_src = (folder / "src").is_dir()
            if has_configs and (has_src or getattr(sys, "frozen", False)):
                return folder

    searched = "\n".join(f"- {folder}" for folder in checked)
    raise RuntimeError(
        "Project root not found.\n"
        "Start the app from the etsy_photo_pipeline folder or set ETSY_PHOTO_PIPELINE_ROOT.\n"
        "Expected folders in the project root: src/ and configs/.\n"
        f"Searched:\n{searched}"
    )


PROJECT_ROOT = find_project_root(Path(__file__).parent)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app_config import OUTPUT_DIR, PROJECT_ROOT as APP_PROJECT_ROOT, list_presets
from src.pipeline import run_pipeline


class PipelineWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)
    log = Signal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params = params

    def run(self) -> None:
        try:
            self.log.emit("Running Etsy photo pipeline...")
            out_dir = run_pipeline(**self.params)
            self.finished.emit(str(out_dir))
        except Exception:
            self.failed.emit(traceback.format_exc())


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Etsy Photo Pipeline")
        self.resize(760, 560)
        self.thread: QThread | None = None
        self.worker: PipelineWorker | None = None
        self.last_output: Path | None = None

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText(str(APP_PROJECT_ROOT / "input" / "your_product"))
        self.output_edit = QLineEdit(str(OUTPUT_DIR))
        self.background_edit = QLineEdit()
        self.template_edit = QLineEdit()
        self.background_edit.setPlaceholderText("Optional JPG/PNG background override")
        self.template_edit.setPlaceholderText("Optional template JSON override")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list_presets())
        self.canvas_combo = QComboBox()
        self.canvas_combo.addItems(["2000", "2500", "3000"])
        self.canvas_combo.setCurrentText("2500")
        self.use_rembg = QCheckBox("Use rembg background removal")
        self.use_rembg.setChecked(False)
        self.debug = QCheckBox("Export debug files")
        self.overwrite = QCheckBox("Overwrite output folder")
        self.zip_export = QCheckBox("Export ZIP")
        self.zip_export.setChecked(True)
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

        form = QFormLayout()
        form.addRow("Input product folder", self._folder_row(self.input_edit))
        form.addRow("Preset", self.preset_combo)
        form.addRow("Output base folder", self._folder_row(self.output_edit))
        form.addRow("Background override", self._file_row(self.background_edit))
        form.addRow("Template JSON override", self._file_row(self.template_edit))
        form.addRow("Canvas size", self.canvas_combo)
        form.addRow("Options", self._options_row())

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.start_pipeline)
        self.open_button = QPushButton("Open output folder")
        self.open_button.clicked.connect(self.open_output_folder)
        self.open_button.setEnabled(False)

        buttons = QHBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.open_button)

        layout = QVBoxLayout()
        intro = QLabel("Select a product folder, choose a preset, and export a reproducible Etsy image set.")
        layout.addWidget(intro)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(QLabel("Status"))
        layout.addWidget(self.log_box)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def append_status(self, message: str) -> None:
        self.log_box.appendPlainText(message)

    def current_folder_hint(self, edit: QLineEdit) -> str:
        value = edit.text().strip()
        if value:
            path = Path(value)
            if path.exists():
                return str(path)
        return str(APP_PROJECT_ROOT)

    def _folder_row(self, edit: QLineEdit) -> QWidget:
        button = QPushButton("Browse")
        button.clicked.connect(lambda: self.pick_folder(edit))
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit)
        layout.addWidget(button)
        return row

    def _file_row(self, edit: QLineEdit) -> QWidget:
        button = QPushButton("Browse")
        button.clicked.connect(lambda: self.pick_file(edit))
        clear = QPushButton("Clear")
        clear.clicked.connect(edit.clear)
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit)
        layout.addWidget(button)
        layout.addWidget(clear)
        return row

    def _options_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.use_rembg)
        layout.addWidget(self.debug)
        layout.addWidget(self.overwrite)
        layout.addWidget(self.zip_export)
        return row

    def pick_folder(self, edit: QLineEdit) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select folder", self.current_folder_hint(edit))
        if folder:
            edit.setText(folder)

    def pick_file(self, edit: QLineEdit) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select file",
            self.current_folder_hint(edit),
            "Images and JSON (*.png *.jpg *.jpeg *.webp *.json);;All files (*.*)",
        )
        if file_name:
            edit.setText(file_name)

    def validate_optional_path(self, raw_path: str, field_name: str) -> Path | None:
        value = raw_path.strip()
        if not value:
            return None
        path = Path(value)
        if not path.exists():
            raise FileNotFoundError(f"{field_name} not found: {path}")
        return path

    def start_pipeline(self) -> None:
        input_dir = Path(self.input_edit.text().strip())
        if not input_dir.exists():
            QMessageBox.warning(self, "Missing input", "Select an existing input product folder first.")
            return
        preset = self.preset_combo.currentText().strip()
        if not preset:
            QMessageBox.warning(self, "Missing preset", "No preset was found in configs/.")
            return

        try:
            background_override = self.validate_optional_path(self.background_edit.text(), "Background override")
            template_override = self.validate_optional_path(self.template_edit.text(), "Template override")
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Missing file", str(exc))
            self.append_status(str(exc))
            return

        params = {
            "input_dir": input_dir,
            "preset_name": preset,
            "output_dir": Path(self.output_edit.text().strip()) if self.output_edit.text().strip() else None,
            "background_override": background_override,
            "template_override": template_override,
            "canvas_size": int(self.canvas_combo.currentText()),
            "use_rembg": self.use_rembg.isChecked(),
            "debug": self.debug.isChecked(),
            "overwrite": self.overwrite.isChecked(),
            "export_zip": self.zip_export.isChecked(),
        }

        self.last_output = None
        self.run_button.setEnabled(False)
        self.open_button.setEnabled(False)
        self.append_status("Starting pipeline...")
        self.append_status(f"Input: {input_dir}")
        self.append_status(f"Preset: {preset}")
        self.append_status(f"Output base: {params['output_dir'] or OUTPUT_DIR}")

        self.thread = QThread()
        self.worker = PipelineWorker(params)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.log_box.appendPlainText)
        self.worker.finished.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_finished(self, output: str) -> None:
        self.last_output = Path(output)
        self.append_status(f"Success: {output}")
        self.run_button.setEnabled(True)
        self.open_button.setEnabled(True)
        QMessageBox.information(self, "Pipeline complete", f"Output folder created:\n{output}")

    def on_failed(self, error: str) -> None:
        self.append_status(error)
        QMessageBox.critical(self, "Pipeline failed", error[-2000:])
        self.run_button.setEnabled(True)
        self.open_button.setEnabled(False)

    def open_output_folder(self) -> None:
        if self.last_output and self.last_output.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_output)))


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
