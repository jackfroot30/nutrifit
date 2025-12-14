from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6 import uic
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve

from ui_components import HoverButton
from auth import Profile
from stopwatch import Stopwatch
from utils import resource_path, get_db_path


class StartScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("HomeScreen.ui"),self)
        #self.lbl1.animate_text("Nutrifit Tracker", speed=60)
        start_btn = self.start_btn
        self.start_btn = HoverButton(start_btn.text(), start_btn.parent())
        self.start_btn.setGeometry(start_btn.geometry())
        self.start_btn.setStyleSheet(start_btn.styleSheet())      
        self.start_btn.setFont(start_btn.font())                  
        self.start_btn.setSizePolicy(start_btn.sizePolicy())      
        self.start_btn.setCursor(start_btn.cursor())        
        start_btn.hide()
        self.start_btn.show()
        self.start_btn.clicked.connect(self.profile_info)
        self.food_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_f.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recipe_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.workout_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.meditation_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scrollArea.setWidgetResizable(True)
        self.page_contents.setMinimumHeight(1000)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.layout = QVBoxLayout(self.page_contents)
        self.meditation_link_btn.clicked.connect(self.show_meditation_page)
        #self.open = MainWindow()
        #self.food_scan_button.clicked.connect(self.open.open_Scanner)
        self.show()

    def show_meditation_page(self):
        self.window = Stopwatch()
        self.window.show()

    def profile_info(self):
        self.win = Profile()
        self.win.show()
        self.hide()