from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpinBox, QPushButton
from PyQt6.QtCore import pyqtSignal

class IngredientAdd(QWidget):
    change = pyqtSignal()
    removed = pyqtSignal(QWidget)
    def __init__(self, name, macros, parent=None):
        super().__init__(parent)
        self.name = name 
        self.macros = macros
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,5,0,5)
        self.name_lbl = QLabel(name)
        self.qty = QSpinBox()
        self.qty.setMinimum(1)
        self.qty.setMaximum(20)
        self.qty.valueChanged.connect(self.change.emit)
        self.unit_lbl = QLabel("x 100g")
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(self.name_lbl)
        self.name_lbl.setMinimumSize(520,20)
        self.name_lbl.setMaximumHeight(40)
        layout.addStretch()
        layout.addWidget(self.qty)
        self.qty.setMaximumHeight(40)
        layout.addWidget(self.unit_lbl)
        self.unit_lbl.setMaximumHeight(40)
        layout.addWidget(self.remove_btn)


class WorkoutAdd(QWidget):
    change = pyqtSignal()
    removed = pyqtSignal(QWidget)
    def __init__(self, exercise_name, parent=None):
        super().__init__(parent)
        self.exercise_name = exercise_name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        common_style = """
            color:#1d1d1d; 
            font:400 15px 'Epilogue';
        """
        spin_style = """
            color:#1d1d1d;
            font:400 15px 'Epilogue';
            background-color:#f0f0f0;
            border: 1px solid #ccc;
            border-radius: 4px;
        """
        self.lbl = QLabel(exercise_name)
        self.lbl.setStyleSheet(common_style)
        self.lbl.setMaximumHeight(25)
        layout.addWidget(self.lbl)
        self.sets_input = QSpinBox()
        self.sets_input.setMinimum(1)
        self.sets_input.setMaximum(20)
        self.sets_input.valueChanged.connect(self.change.emit)
        self.sets_input.setMaximumHeight(25)
        self.sets_input.setStyleSheet(spin_style)
        layout.addWidget(self.sets_input)
        self.sets_lbl = QLabel("sets")
        self.sets_lbl.setStyleSheet(common_style)
        self.sets_lbl.setMaximumHeight(25)
        layout.addWidget(self.sets_lbl)
        self.reps_input = QSpinBox()
        self.reps_input.setMinimum(1)
        self.reps_input.setMaximum(50)
        self.reps_input.valueChanged.connect(self.change.emit)
        self.reps_input.setMaximumHeight(25)
        self.reps_input.setStyleSheet(spin_style)
        layout.addWidget(self.reps_input)
        self.reps_lbl = QLabel("reps")
        self.reps_lbl.setStyleSheet(common_style)
        self.reps_lbl.setMaximumHeight(25)
        layout.addWidget(self.reps_lbl)
        self.weight_input = QSpinBox()
        self.weight_input.setMinimum(0)
        self.weight_input.setMaximum(500)
        self.weight_input.valueChanged.connect(self.change.emit)
        self.weight_input.setMaximumHeight(25)
        self.weight_input.setStyleSheet(spin_style)
        layout.addWidget(self.weight_input)
        self.weight_lbl = QLabel("weight")
        self.weight_lbl.setStyleSheet(common_style)
        self.weight_lbl.setMaximumHeight(25)
        layout.addWidget(self.weight_lbl)
        self.kg_lbl = QLabel("kg")
        self.kg_lbl.setStyleSheet(common_style)
        self.kg_lbl.setMaximumHeight(25)
        layout.addWidget(self.kg_lbl)
        self.rem_btn = QPushButton("Remove")
        self.rem_btn.clicked.connect(lambda: self.removed.emit(self))
        self.rem_btn.setStyleSheet(common_style)
        self.rem_btn.setMaximumHeight(25)
        layout.addWidget(self.rem_btn)