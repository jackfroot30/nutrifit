from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtProperty, QPropertyAnimation, QEasingCurve, QObject
from PyQt6.QtGui import QColor
import sys

class ColorLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self._color = QColor(255, 0, 0) # Start Red
        self.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {self._color.name()}")

    # 1. Define a 'getter'
    @pyqtProperty(QColor)
    def color(self):
        return self._color

    # 2. Define a 'setter' that updates the style
    @color.setter
    def color(self, value):
        self._color = value
        self.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {self._color.name()}")

class Window(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.label = ColorLabel("Color Morphing Text")
        layout.addWidget(self.label)
        
        # Animate the custom 'color' property
        self.anim = QPropertyAnimation(self.label, b"color")
        self.anim.setDuration(3000)
        self.anim.setStartValue(QColor(255, 0, 0))   # Red
        self.anim.setEndValue(QColor(0, 0, 255))     # Blue
        self.anim.setLoopCount(-1) # Loop forever
        self.anim.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())