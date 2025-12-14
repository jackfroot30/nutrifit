import sys
import os 
from PyQt6.QtWidgets import QApplication
from start_screen import StartScreen

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = StartScreen()
    sys.exit(app.exec())

