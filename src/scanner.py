from PyQt6.QtWidgets import QMainWindow, QLabel, QListWidgetItem
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QTimer
from PyQt6 import uic
import cv2
import google.generativeai as genai
from PIL import Image
import re
import numpy as np
from utils import resource_path,get_db_path


class Scanner(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("Scanner.ui"), self)
        self.window = QMainWindow()
        genai.configure(api_key="  ")
        self.model = genai.GenerativeModel("gemini-2.5-pro")
        self.video_label = QLabel(self.cam_frame)
        self.video_label.setGeometry(0, 0, self.cam_frame.width(), self.cam_frame.height())
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.last_request_time = 0
        self.search_btn.clicked.connect(self.freeze_and_scan)

    def freeze_and_scan(self):
        self.timer.stop()
        if self.last_frame is not None:
            self.recognize_object(self.last_frame)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            img_qt = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img_qt)
            self.video_label.setPixmap(pixmap.scaled(self.video_label.width(), self.video_label.height()))

    def recognize_object(self, frame):
        try:
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            import io
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format="JPEG")
            img_bytes.seek(0)
            response = self.model.generate_content(
                [
                    "Identify the food item and list only macros (calories, protein, carbs, fats) if possible. in the format: The item is: item_name \n Calories: \n Protein: \n Carbs: \n Fats:",
                    {"mime_type": "image/jpeg", "data": img_bytes.read()},
                ]
            )
            print("Gemini:", response.text)
            cleaned = self.clean_markdown(response.text)
            self.listWidget.addItem(cleaned)
        
        except Exception as e:
            print("Gemini Error:", e)

    def clean_markdown(self, text):
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text) 
        text = re.sub(r"[*#`>-]", "", text)          
        return text.strip()

    def closeEvent(self, event):
        self.cap.release()