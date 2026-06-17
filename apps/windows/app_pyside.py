from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app_config import list_presets
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
        self.output_edit = QLineEdit(str(PROJECT_ROOT / "output"))
        self.background_edit = QLineEdit()
        self.template_edit = QLineEdit()
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
        folder = QFileDialog.getExistingDirectory(self, "Select folder", str(PROJECT_ROOT))
        if folder:
            edit.setText(folder)

    def pick_file(self, edit: QLineEdit) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select file",
            str(PROJECT_ROOT),
            "Images and JSON (*.png *.jpg *.jpeg *.webp *.json);;All files (*.*)",
        )
        if file_name:
            edit.setText(file_name)

    def start_pipeline(self) -> None:
        input_dir = Path(self.input_edit.text().strip())
        if not input_dir.exists():
            QMessageBox.warning(self, "Missing input", "Select an existing input product folder first.")
            return
        preset = self.preset_combo.currentText().strip()
        if not preset:
            QMessageBox.warning(self, "Missing preset", "No preset was found in configs/.")
            return

        params = {
            "input_dir": input_dir,
            "preset_name": preset,
            "output_dir": Path(self.output_edit.text().strip()) if self.output_edit.text().strip() else None,
            "background_override": Path(self.background_edit.text().strip()) if self.background_edit.text().strip() else None,
            "template_override": Path(self.template_edit.text().strip()) if self.template_edit.text().strip() else None,
            "canvas_size": int(self.canvas_combo.currentText()),
            "use_rembg": self.use_rembg.isChecked(),
            "debug": self.debug.isChecked(),
            "overwrite": self.overwrite.isChecked(),
            "export_zip": self.zip_export.isChecked(),
        }

        self.run_button.setEnabled(False)
        self.open_button.setEnabled(False)
        self.log_box.appendPlainText("Starting...\n")

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
        self.log_box.appendPlainText(f"Done: {output}\n")
        self.run_button.setEnabled(True)
        self.open_button.setEnabled(True)

    def on_failed(self, error: str) -> None:
        self.log_box.appendPlainText(error)
        QMessageBox.critical(self, "Pipeline failed", error[-2000:])
        self.run_button.setEnabled(True)

    def open_output_folder(self) -> None:
        if self.last_output and self.last_output.exists():
            os.startfile(self.last_output)  # Windows only


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
