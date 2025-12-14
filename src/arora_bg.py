import sys
import random
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter, QRadialGradient, QColor, QBrush
from PyQt6.QtCore import QTimer, Qt, QPoint

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

class AuroraBackgroundLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMouseTracking(True)
        self.cursor_pos = None  

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.blobs = [           
            Blob(QColor(255, 105, 180, 180), 0.003, 0.002), 
            Blob(QColor(0, 200, 255, 160), -0.002, 0.004), 
            Blob(QColor(255, 212, 247), 0.004, -0.003),
            Blob(QColor(255, 200, 150, 140), -0.003, -0.001)
        ]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_blobs)
        self.timer.start(20)

    def mouseMoveEvent(self, event):
        self.cursor_pos = event.position().toPoint()
    
    def leaveEvent(self, event):
        self.cursor_pos = None

    def animate_blobs(self):
        for blob in self.blobs:
            blob.move()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        rect = self.rect()

        painter.setBrush(QColor("#fff0f5"))
        painter.drawEllipse(rect)

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
            painter.drawEllipse(rect)

        if self.cursor_pos:
            spotlight_gradient = QRadialGradient(
                float(self.cursor_pos.x()), 
                float(self.cursor_pos.y()), 
                w * 0.4
            )
            
            spotlight_gradient.setColorAt(0.0, QColor(255, 255, 255, 100))
            spotlight_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
            
            painter.setBrush(QBrush(spotlight_gradient))
            painter.drawEllipse(rect)