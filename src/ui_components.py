from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation

class HoverButton(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)
        self.base_geometry = None

    def enterEvent(self, event):
        if self.base_geometry is None:
            self.base_geometry = self.geometry()

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(50)
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(self.base_geometry.adjusted(-2, -2, 2, 2))  
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(150)
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(self.base_geometry)
        self.anim.start()
        super().leaveEvent(event)