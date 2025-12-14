import sys
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QRadialGradient, QColor, QBrush
from PyQt6.QtCore import QTimer, Qt

class Blob:
    def __init__(self, color, x_speed, y_speed):
        self.x = random.random()
        self.y = random.random()
        self.dx = x_speed
        self.dy = y_speed
        self.color = color

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= 1: self.dx *= -1
        if self.y <= 0 or self.y >= 1: self.dy *= -1

class AuroraBackgroundScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.is_active = True 

        self.blobs = [
            Blob(QColor(255, 105, 180, 180), 0.003, 0.002), 
            Blob(QColor(0, 200, 255, 160), -0.002, 0.004), 
            Blob(QColor(255, 212, 247), 0.004, -0.003),
            Blob(QColor(255, 200, 150, 140), -0.003, -0.001)
        ]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_blobs)
        self.timer.start(20)

    def set_active(self, active):
        self.is_active = active
        if active:
            self.timer.start(20) 
        else:
            self.timer.stop()   
        self.update()            

    def animate_blobs(self):
        for blob in self.blobs:
            blob.move()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        rect = self.rect()
        radius = 10.0  

        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(rect, radius, radius)

        if self.is_active:
            w = self.width()
            h = self.height()
            for blob in self.blobs:
                center_x = blob.x * w
                center_y = blob.y * h
                grad_radius = w * 0.6  
                gradient = QRadialGradient(center_x, center_y, grad_radius)
                gradient.setColorAt(0.0, blob.color)
                transparent = QColor(blob.color)
                transparent.setAlpha(0)
                gradient.setColorAt(1.0, transparent)
                painter.setBrush(QBrush(gradient))
                painter.drawRoundedRect(rect, radius, radius)