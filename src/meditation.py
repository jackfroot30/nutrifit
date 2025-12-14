"""
breathing_final_ready.py
Patched single-file breathing meditation app (PyQt5)

Fixes included:
- Uses QRectF for drawEllipse calls so floats work (avoids TypeError).
- Non-blocking bell using QSoundEffect when available; fallback to QApplication.beep().
- Safe handling when disabling the separator item in QComboBox.
- Restore previous combo selection if Add Preset dialog cancelled.
- Clearer diameter variable names in paintEvent to avoid confusion.
- Dark theme spinbox/combo styling fixed (no white boxes on dark bg).
- Presets saved as lists for explicit JSON compatibility.
"""

import sys
import json
import math
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSpinBox, QFormLayout, QComboBox, QMessageBox, QDialog,
    QDialogButtonBox, QLineEdit, QGridLayout, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QUrl, QRectF
from PyQt5.QtGui import QPainter, QColor, QConicalGradient, QBrush

# Attempt to import QSoundEffect for non-blocking sound playback
try:
    from PyQt5.QtMultimedia import QSoundEffect  # type: ignore
    _HAS_QSOUNDEFFECT = True
except Exception:
    _HAS_QSOUNDEFFECT = False

PRESETS_FILE = "presets.json"
ADD_PRESET_ID = "➕ Add New Preset…"
SEPARATOR_ID = "──────────────"

# ---------------------------
# Utility: easing function
# ---------------------------
def ease_in_out_cos(t: float) -> float:
    """Smooth cosine easing (0..1 -> 0..1)."""
    t = max(0.0, min(1.0, t))
    return 0.5 * (1 - math.cos(math.pi * t))


# ---------------------------
# Breathing Ball widget
# ---------------------------
class BreathingBallWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.factor = 0.0   # main normalized factor 0..1
        self.glow = 0.0     # glow intensity 0..1
        self.primary_color = QColor(200, 170, 255)
        self.alt_color = QColor(120, 220, 255)
        self.setMinimumSize(360, 360)
        # ensure good scaling margins
        self.margin_ratio = 0.12

    def set_factor(self, f: float):
        self.factor = max(0.0, min(1.0, f))
        self.update()

    def set_glow(self, g: float):
        self.glow = max(0.0, min(1.0, g))
        self.update()

    def set_colors(self, primary: QColor, alt: QColor):
        self.primary_color = primary
        self.alt_color = alt
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        # background conical gradient that subtly shifts with factor
        t = self.factor
        start_col = QColor(
            int(self.primary_color.red() * (1 - t) + self.alt_color.red() * t),
            int(self.primary_color.green() * (1 - t) + self.alt_color.green() * t),
            int(self.primary_color.blue() * (1 - t) + self.alt_color.blue() * t),
        )
        grad = QConicalGradient(cx, cy, 0)
        grad.setColorAt(0.0, start_col)
        grad.setColorAt(1.0, QColor(10, 8, 35))
        p.fillRect(self.rect(), grad)

        # size & margin
        usable = min(w, h) * (1.0 - self.margin_ratio * 2)
        # base_diameter is explicitly a diameter (not radius) to match drawEllipse args
        base_diameter = (0.30 * usable) + (0.70 * usable * self.factor)  # maps smoothly 0..1
        # slight micro motion during hold: tiny sinusoidal movement for life
        micro = 1.0 + 0.02 * math.sin(self.factor * math.pi * 6)

        diameter = base_diameter * micro

        # glow (diameter)
        glow_diameter = diameter * (1.0 + 0.4 * self.glow)
        glow_color = QColor(self.primary_color)
        glow_alpha = int(40 + 160 * self.glow)
        glow_color.setAlpha(glow_alpha)
        p.setBrush(QBrush(glow_color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(cx - glow_diameter / 2, cy - glow_diameter / 2, glow_diameter, glow_diameter))

        # main ball: softer inner shading
        main_color = QColor(
            int(self.primary_color.red() * (0.6 + 0.4 * self.factor)),
            int(self.primary_color.green() * (0.6 + 0.4 * self.factor)),
            int(self.primary_color.blue() * (0.6 + 0.4 * self.factor)),
            230
        )
        p.setBrush(QBrush(main_color))
        p.drawEllipse(QRectF(cx - diameter / 2, cy - diameter / 2, diameter, diameter))

        # subtle highlight (smaller ellipse on top-left region)
        highlight = QColor(255, 255, 255, int(30 + 90 * self.factor))
        p.setBrush(QBrush(highlight))
        p.drawEllipse(QRectF(cx - diameter / 6, cy - diameter / 2.8, diameter / 3, diameter / 3))


# ---------------------------
# Preset dialog
# ---------------------------
class NewPresetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Preset")
        self.setModal(True)

        self.name_edit = QLineEdit()
        self.inh_spin = QSpinBox(); self.inh_spin.setRange(1, 300); self.inh_spin.setValue(4)
        self.hold_spin = QSpinBox(); self.hold_spin.setRange(0, 300); self.hold_spin.setValue(4)
        self.ex_spin = QSpinBox(); self.ex_spin.setRange(1, 300); self.ex_spin.setValue(4)

        layout = QGridLayout(self)
        layout.addWidget(QLabel("Preset name:"), 0, 0)
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(QLabel("Inhale (s):"), 1, 0)
        layout.addWidget(self.inh_spin, 1, 1)
        layout.addWidget(QLabel("Hold (s):"), 2, 0)
        layout.addWidget(self.hold_spin, 2, 1)
        layout.addWidget(QLabel("Exhale (s):"), 3, 0)
        layout.addWidget(self.ex_spin, 3, 1)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns, 4, 0, 1, 2)

    def values(self):
        return self.name_edit.text().strip(), int(self.inh_spin.value()), int(self.hold_spin.value()), int(self.ex_spin.value())


# ---------------------------
# Main App
# ---------------------------
class BreathingFinalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Breathing Meditation — Final (Ready)")
        self.setMinimumSize(920, 640)

        # breathing defaults
        self.inhale = 4
        self.hold = 4
        self.exhale = 4

        # animation state
        self.elapsed_ms = 0
        self.tick_ms = 20  # 50Hz smooth
        self.running = False
        self.session_countdown_ms = 0

        # load presets
        self.presets = self._load_presets()

        # widgets
        self.ball = BreathingBallWidget()
        self.cue_label = QLabel("Ready")
        self.cue_label.setAlignment(Qt.AlignCenter)
        self.cue_label.setStyleSheet("font-size:30px; font-weight:600;")

        # controls
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.reset_btn = QPushButton("Reset")
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.reset_btn.clicked.connect(self.reset)

        self.in_spin = QSpinBox(); self.in_spin.setRange(1, 300); self.in_spin.setValue(self.inhale)
        self.hold_spin = QSpinBox(); self.hold_spin.setRange(0, 300); self.hold_spin.setValue(self.hold)
        self.ex_spin = QSpinBox(); self.ex_spin.setRange(1, 300); self.ex_spin.setValue(self.exhale)

        # session countdown
        self.session_spin = QSpinBox(); self.session_spin.setRange(0, 240); self.session_spin.setValue(5)
        self.session_check = QCheckBox("Enable session countdown (auto-stop)")
        self.session_check.setChecked(True)

        # preset combo
        self.preset_combo = QComboBox()
        self._populate_preset_combo()
        self.preset_combo.currentIndexChanged.connect(self.preset_selected)

        # theme toggle
        self.theme_toggle = QPushButton("Toggle Light Theme")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.toggled.connect(self.toggle_theme)
        # saved theme state
        self._is_light = False

        # layout
        form = QFormLayout()
        form.addRow("Inhale (s):", self.in_spin)
        form.addRow("Hold (s):", self.hold_spin)
        form.addRow("Exhale (s):", self.ex_spin)
        form.addRow("Session (min):", self.session_spin)

        left = QVBoxLayout()
        left.addWidget(QLabel("<b>Preset</b>"))
        left.addWidget(self.preset_combo)
        left.addSpacing(8)
        left.addLayout(form)
        left.addSpacing(6)
        left.addWidget(self.cue_label)
        left.addSpacing(6)
        left.addWidget(self.session_check)
        left.addWidget(self.theme_toggle)
        left.addStretch()
        btnrow = QHBoxLayout()
        btnrow.addWidget(self.start_btn)
        btnrow.addWidget(self.stop_btn)
        btnrow.addWidget(self.reset_btn)
        left.addLayout(btnrow)

        right = QVBoxLayout()
        right.addWidget(self.ball)

        main = QHBoxLayout(self)
        main.addLayout(left, 1)
        main.addLayout(right, 2)

        # timer
        self.timer = QTimer(self)
        self.timer.setInterval(self.tick_ms)
        self.timer.timeout.connect(self._tick)

        # theme apply
        self._apply_theme()

        # sound / phase state
        self._last_phase = None

        # QSoundEffect (if available)
        self._bell_effect = None
        if _HAS_QSOUNDEFFECT:
            try:
                self._bell_effect = QSoundEffect(self)
                # don't set source by default; user can add a local wav and set its path here.
                # e.g. self._bell_effect.setSource(QUrl.fromLocalFile("soft_bell.wav"))
                self._bell_effect.setVolume(0.25)
            except Exception:
                self._bell_effect = None

        # ensure combos render text color correctly on start
        self._update_combo_style()

    # -------------------------
    # presets persistence
    # -------------------------
    def _default_presets(self):
        return {
            "Box breathing (4-4-4)": (4, 4, 4),
            "Relaxing (4-7-8)": (4, 7, 8),
            "Quick calm (3-3-3)": (3, 3, 3),
            "Long slow (6-6-6)": (6, 6, 6),
            "Wim Hof (burst placeholder)": (30, 0, 30)
        }

    def _load_presets(self):
        p = Path(PRESETS_FILE)
        if p.exists():
            try:
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    # validate and convert to tuples
                    validated = {}
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) >= 3:
                            validated[k] = tuple(int(x) for x in v[:3])
                    # include defaults if missing
                    for k, v in self._default_presets().items():
                        if k not in validated:
                            validated[k] = v
                    return validated
            except Exception:
                pass
        return self._default_presets()

    def _save_presets(self):
        try:
            # convert tuples -> lists explicitly for JSON
            serializable = {k: list(v) for k, v in self.presets.items()}
            with open(PRESETS_FILE, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        except Exception as e:
            print("Failed saving presets:", e)

    def _populate_preset_combo(self):
        # preserve current text selection if present
        cur_text = self.preset_combo.currentText() if self.preset_combo.count() > 0 else None
        self.preset_combo.clear()
        for name in self.presets.keys():
            self.preset_combo.addItem(name)
        # separator visual (disabled)
        self.preset_combo.addItem(SEPARATOR_ID)
        idx = self.preset_combo.count() - 1
        item = self.preset_combo.model().item(idx)
        if item is not None:
            item.setEnabled(False)
        # add new preset item
        self.preset_combo.addItem(ADD_PRESET_ID)
        # restore selection if possible
        if cur_text:
            idx = self.preset_combo.findText(cur_text)
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)
            else:
                self.preset_combo.setCurrentIndex(0)
        else:
            if self.preset_combo.count() > 0:
                self.preset_combo.setCurrentIndex(0)

    def preset_selected(self, idx):
        if idx < 0:
            return
        text = self.preset_combo.currentText()
        if text == ADD_PRESET_ID:
            # open dialog and restore previous index if cancelled
            old_idx = idx
            dlg = NewPresetDialog(self)
            if dlg.exec_() == QDialog.Accepted:
                name, inh, hold, exh = dlg.values()
                if not name:
                    QMessageBox.warning(self, "Add Preset", "Name cannot be empty.")
                else:
                    # add
                    self.presets[name] = (inh, hold, exh)
                    self._save_presets()
                    self._populate_preset_combo()
                    # select the new one
                    idx = self.preset_combo.findText(name)
                    if idx >= 0:
                        self.preset_combo.setCurrentIndex(idx)
            else:
                # restore previous selection if canceled
                if old_idx >= 0 and old_idx < self.preset_combo.count():
                    self.preset_combo.setCurrentIndex(old_idx)
                else:
                    if self.preset_combo.count() > 0:
                        self.preset_combo.setCurrentIndex(0)
            return

        if text == SEPARATOR_ID:
            # ignore selection of separator
            # set to first real item if possible
            if self.preset_combo.count() > 0:
                self.preset_combo.setCurrentIndex(0)
            return

        if text in self.presets:
            inh, hold, exh = self.presets[text]
            self.in_spin.setValue(inh)
            self.hold_spin.setValue(hold)
            self.ex_spin.setValue(exh)
            self.cue_label.setText(f"Preset: {text}")

    # -------------------------
    # theme / styles
    # -------------------------
    def toggle_theme(self, checked: bool):
        # button is toggled on for light theme
        self._is_light = checked
        self.theme_toggle.setText("Toggle Dark Theme" if checked else "Toggle Light Theme")
        self._apply_theme()
        self._update_combo_style()

    def _apply_theme(self):
        if self._is_light:
            self.setStyleSheet("""
                QWidget { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ffffff, stop:1 #f4f7ff); }
                QLabel { color: #111; }
                QPushButton { background-color: #6f2cff; color: white; padding:8px; border-radius:6px; }
                QSpinBox, QComboBox { background: white; color: #111; padding:4px; }
                QCheckBox { color: #111; }
            """)
            self.ball.set_colors(QColor(180, 220, 255), QColor(255, 240, 220))
        else:
            # darker spinbox/combo background so they don't become glaring white boxes
            self.setStyleSheet("""
                QWidget { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0f0724, stop:1 #1a0630); }
                QLabel { color: #fff; }
                QPushButton { background-color: #6f2cff; color: white; padding:8px; border-radius:6px; }
                QSpinBox, QComboBox { background: #2a2a3a; color: #fff; padding:4px; border-radius:4px; }
                QCheckBox { color: #fff; }
            """)
            self.ball.set_colors(QColor(200, 170, 255), QColor(120, 220, 255))

    def _update_combo_style(self):
        # make sure the popup list uses readable color in both themes
        if self._is_light:
            self.preset_combo.setStyleSheet("QComboBox QAbstractItemView { color: #111; background: #ffffff; }")
        else:
            # dark theme: white text in the dropdown
            self.preset_combo.setStyleSheet("QComboBox QAbstractItemView { color: #fff; background: #2a2a3a; }")

    # -------------------------
    # start / stop / reset
    # -------------------------
    def start(self):
        # read values but do NOT reset elapsed_ms (to preserve continuity on resume)
        self.inhale = int(self.in_spin.value())
        self.hold = int(self.hold_spin.value())
        self.exhale = int(self.ex_spin.value())

        # initialize session countdown only if enabled and >0 AND not already counting
        if self.session_check.isChecked() and int(self.session_spin.value()) > 0 and self.session_countdown_ms == 0:
            self.session_countdown_ms = int(self.session_spin.value()) * 60 * 1000

        self.running = True
        if not self.timer.isActive():
            self.timer.start()
        self.cue_label.setText("Starting...")
        self._last_phase = None

    def stop(self):
        self.running = False
        # Stop the QTimer to save CPU and pause animations
        if self.timer.isActive():
            self.timer.stop()
        self.cue_label.setText("Paused")

    def reset(self):
        self.running = False
        if self.timer.isActive():
            self.timer.stop()
        self.elapsed_ms = 0
        self.session_countdown_ms = 0
        self.ball.set_factor(0.0)
        self.ball.set_glow(0.0)
        self.cue_label.setText("Ready")
        self._last_phase = None

    # -------------------------
    # sound cue (soft bell)
    # -------------------------
    def _soft_bell(self):
        try:
            # Prefer QSoundEffect if available and a source set
            if self._bell_effect is not None and not self._bell_effect.source().isEmpty():
                self._bell_effect.play()
            else:
                # Quick non-blocking fallback
                QApplication.beep()
        except Exception:
            try:
                QApplication.beep()
            except Exception:
                pass

    # -------------------------
    # session completion UI
    # -------------------------
    def _complete_session(self):
        # show a pleasant completion dialog (non-example text)
        self._soft_bell()
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Session Complete")
        dlg.setText("Session finished")
        dlg.setInformativeText("You completed your meditation session. Take a moment to breathe and reflect.")
        dlg.setIcon(QMessageBox.Information)
        dlg.exec_()
        # reset afterward
        self.reset()

    # -------------------------
    # main tick
    # -------------------------
    def _tick(self):
        # Running flag controls behavior. We still use QTimer for continuous redraws.
        # If timer isn't active (paused), we don't get ticks.
        if not self.running:
            return

        self.elapsed_ms += self.tick_ms

        # session countdown
        if self.session_countdown_ms > 0:
            self.session_countdown_ms -= self.tick_ms
            if self.session_countdown_ms <= 0:
                # session end
                self.session_countdown_ms = 0
                self.running = False
                if self.timer.isActive():
                    self.timer.stop()
                self._complete_session()
                return

        total_ms = (self.inhale + self.hold + self.exhale) * 1000
        if total_ms <= 0:
            return

        t = self.elapsed_ms % total_ms

        # determine phase and local progress
        if t < self.inhale * 1000:
            phase = "inhale"
            raw_local = t / (self.inhale * 1000)
            local = ease_in_out_cos(raw_local)
        elif t < (self.inhale + self.hold) * 1000:
            phase = "hold"
            # keep at 1.0 but apply tiny micro motion to avoid snapping
            local = 1.0
            # micro-oscillation to appear alive
            micro = 0.002 * math.sin(math.radians(self.elapsed_ms / 10.0))
            local = max(0.0, min(1.0, local + micro))
        else:
            phase = "exhale"
            raw_local = (t - (self.inhale + self.hold) * 1000) / (self.exhale * 1000)
            # exhale should be smooth reversed
            local = 1.0 - ease_in_out_cos(raw_local)

        # update cue label
        if phase == "inhale":
            self.cue_label.setText("Breathe in")
        elif phase == "hold":
            self.cue_label.setText("Hold")
        else:
            self.cue_label.setText("Breathe out")

        # phase transition sound
        if phase != self._last_phase:
            self._soft_bell()
            self._last_phase = phase

        # glow intensity: stronger during inhale/exhale, soft at hold
        glow_base = 0.9 if phase in ("inhale", "exhale") else 0.28
        # scale by local smoothness for extra life
        glow = (0.6 + 0.4 * local) * glow_base
        self.ball.set_glow(glow)

        # update ball factor (handles visual color shifting and size)
        self.ball.set_factor(local)

    # -------------------------
    # Run
    # -------------------------
def main():
    app = QApplication(sys.argv)
    w = BreathingFinalApp()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()