from __future__ import annotations

import sys
import traceback
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app_config import list_presets
from src.pipeline import run_pipeline


KV = r'''
RootWidget:
    orientation: "vertical"
    padding: "12dp"
    spacing: "8dp"

    Label:
        text: "Etsy Photo Pipeline - Android/Pydroid style mode"
        size_hint_y: None
        height: "36dp"

    TextInput:
        id: input_dir
        hint_text: "Input folder path, e.g. input/pendant_001"
        multiline: False
        text: root.input_path

    TextInput:
        id: output_dir
        hint_text: "Output folder path, e.g. output"
        multiline: False
        text: root.output_path

    Spinner:
        id: preset
        text: root.default_preset
        values: root.presets
        size_hint_y: None
        height: "44dp"

    Spinner:
        id: canvas
        text: "2500"
        values: ["2000", "2500"]
        size_hint_y: None
        height: "44dp"

    CheckBox:
        id: debug
        size_hint_y: None
        height: "32dp"
    Label:
        text: "Debug output"
        size_hint_y: None
        height: "24dp"

    Button:
        text: "Run pipeline"
        size_hint_y: None
        height: "48dp"
        on_release: root.run_pipeline_from_ui(input_dir.text, output_dir.text, preset.text, canvas.text, debug.active)

    TextInput:
        id: status
        text: root.status
        readonly: True
        multiline: True
'''


class RootWidget(BoxLayout):
    status = StringProperty("Transparent PNG inputs are recommended. rembg/OpenCV are disabled on Android.\n")
    input_path = StringProperty("input/pendant_001")
    output_path = StringProperty("output")
    _presets = tuple(list_presets())
    presets = _presets
    default_preset = _presets[0] if _presets else "jewelry_dark_pendant"

    def run_pipeline_from_ui(self, input_dir: str, output_dir: str, preset: str, canvas: str, debug: bool) -> None:
        self.status += "\nRunning...\n"
        try:
            out = run_pipeline(
                input_dir=Path(input_dir),
                preset_name=preset,
                output_dir=Path(output_dir),
                canvas_size=int(canvas),
                use_rembg=False,
                debug=debug,
                overwrite=False,
                export_zip=True,
            )
            self.status += f"Done: {out}\n"
        except Exception:
            self.status += traceback.format_exc() + "\n"


class EtsyPhotoPipelineApp(App):
    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    EtsyPhotoPipelineApp().run()
