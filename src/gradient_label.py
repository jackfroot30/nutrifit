import sys
import random
from PyQt6.QtWidgets import QWidget, QLabel
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

class GradientBackgroundLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.blobs = [
            Blob(QColor(237, 237, 237), 0.003, 0.002), 
            Blob(QColor(227, 241, 255), -0.002, 0.004), 
            Blob(QColor(217, 236, 255), 0.004, -0.003),
            Blob(QColor(217, 236, 255, 140), -0.003, -0.001)
        ]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_blobs)
        self.timer.start(20)

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
        painter.setBrush(QColor("#fff0f5"))
        painter.drawRoundedRect(rect, radius, radius)
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