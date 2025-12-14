import sys
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QWidget, QGraphicsOpacityEffect)
from PyQt6.QtCore import (QTimer, QTime, Qt, QPropertyAnimation, QEvent, QRect, 
                          QEasingCurve, QSequentialAnimationGroup, QPauseAnimation)
from ui_components import HoverButton
from utils import resource_path,get_db_path

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("meditation.ui"), self)
    

        self.time = QTime(0,0,1,0)
        self.cycle_counter = QTime(0,0,1,0)
        self.breath_control_time = QTime(0,0,0,0)
        
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        
        self.cycle_counter_timer = QTimer(self)
        self.cycle_counter_timer.setInterval(12000)
        
        self.breath_control_timer = QTimer(self)
        self.breath_control_timer.setInterval(4000)

        self.anim_group = None # Initialize safely

        # Opacity settings
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(.7)
        self.circle_label.setGraphicsEffect(self.opacity_effect)

        self.cycles = 0 

        self.timer.timeout.connect(self.update_display)
        self.cycle_counter_timer.timeout.connect(self.update_display_1)
        self.breath_control_timer.timeout.connect(self.update_display4)
        

        self.ready_go_done.setHidden(True)
        self.circle_label.setHidden(True)
        self.timer_in_circle.setHidden(True)
        self.reset_btn.setHidden(True)
        self.pause_btn.setHidden(True)
        self.back_btn.setHidden(True)
        self.resume_btn.setHidden(True)
        self.cycle_counter_label.setHidden(True)
        
        self.ready_btn.clicked.connect(self.start_sesh)
        self.pause_btn.clicked.connect(self.stop)
        self.reset_btn.clicked.connect(self.comp_reset)
        self.back_btn.clicked.connect(self.comp_reset)
        self.resume_btn.clicked.connect(self.resu) 
        self.back_btn.clicked.connect(self.hide)

        self.is_timer_stopped = True
    
    def start_sesh(self):
        self.ready_btn.setHidden(True)
        self.ready_go_done.setHidden(False)
        
        self.ready_go_done.setText("Ready?") 
        
 
        QTimer.singleShot(1000, lambda: self.ready_go_done.setText("Go!"))
        QTimer.singleShot(2000, lambda: self.ready_go_done.setText("Breathe in"))
        QTimer.singleShot(2000, self.start) 

    def start(self):
        self.start1()

    def start1(self):
        self.is_timer_stopped = False
        self.circle_label.setHidden(False)
        self.timer_in_circle.setHidden(False)
        self.cycle_counter_label.setHidden(False)
        self.pause_btn.setHidden(False)
        self.reset_btn.setHidden(False)
        self.back_btn.setHidden(False)

        self.time = QTime(0, 0, 1, 0)
        self.breath_control_time = QTime(0, 0, 0, 0)
        self.timer_in_circle.setText(self.format_time(self.time))
        self.cycles = 0

        self.timer.start()    
        self.breath_control_timer.start()

        loops = int(self.spinBox_2.value()) * 5
        self.circ_anim(loop_count=loops, ms=4000)
        
    def stop(self):
        self.timer.stop()
        self.breath_control_timer.stop()
        self.cycle_counter_timer.stop()
        self.is_timer_stopped = True
        if self.anim_group is not None:
            self.anim_group.pause()
        
        self.resume_btn.setHidden(False)
        self.resume_btn.setText("Resume")
        self.pause_btn.setHidden(True)

    def reset(self):
        self.timer.stop()
        self.time = QTime(0, 0, 1, 0)
        self.timer_in_circle.setText(self.format_time(self.time))
        self.is_timer_stopped = True
    
    def align_circle_to_text(self):
        timer_geometry = self.timer_in_circle.geometry()
        center_x = timer_geometry.center().x()
        center_y = timer_geometry.center().y()
        
        circle_size = 50
        radius = circle_size // 2
        
        self.circle_label.setGeometry(
            center_x - radius, 
            center_y - radius, 
            circle_size, 
            circle_size
        )

    def comp_reset(self):
            self.reset()
            self.breath_control_timer.stop()
            self.cycle_counter_timer.stop()
            self.breath_control_time = QTime(0,0,0,0)
            self.cycle_counter = QTime(0,0,1,0)
            self.timer_in_circle.setText("1")
            self.cycle_counter_label.setText("Number of Cycles completed: 00")
            self.ready_go_done.setText("Ready?")
            self.resume_btn.setText("Start")
            
            self.align_circle_to_text() 

            self.circle_label.setStyleSheet("""
                    background-color: qradialgradient(
                                        spread:pad, 
                                        cx:0.5, 
                                        cy:0.5,
                                        radius:0.8, 
                                        fx:0.5, 
                                        fy:0.5, 
                                        stop:0 #FFD5D5, 
                                        stop:0.26 #FFB5B5, 
                                        stop:1 #FFD5F6); 
                    border:0px; 
                    border-radius: 25px;
                """)
            
            if self.anim_group is not None:
                self.anim_group.stop()
                
            self.is_timer_stopped = True

    def resu(self):
        if self.resume_btn.text() == "Resume":
            self.timer.start()
            self.breath_control_timer.start()
            self.cycle_counter_timer.start()
            self.is_timer_stopped = False
            
            self.resume_btn.setHidden(True)
            self.pause_btn.setHidden(False)

            if self.anim_group is not None:
                self.anim_group.resume()

        elif self.resume_btn.text() == "Start":
            self.resume_btn.setText("Resume")
            self.circle_label.setGeometry(410,410,50,50)
            if self.is_timer_stopped:
                self.start_sesh()

    def format_time(self, time):
        seconds = time.second()
        return f"{seconds:01}"
    
    def format_cycle_counter(self, time):
        seconds = time.second() // 12
        return f"Number of Cycles Completed: {seconds:02}"

    def update_display(self):
        self.time = self.time.addMSecs(10)
        self.timer_in_circle.setText(self.format_time(self.time))
    
    def update_display_1(self):
        self.cycle_counter = self.cycle_counter.addMSecs(12000)
        self.cycle_counter_label.setText(self.format_cycle_counter(self.cycle_counter))
        self.cycles += 1
        if self.cycles == (self.spinBox_2.value() * 5):
           self.stop()

    def update_display4(self):
        self.breath_control_time = self.breath_control_time.addMSecs(4000)
        s = int(self.format_time(self.breath_control_time)) // 4
        if s % 3 == 0:
            self.ready_go_done.setText("Breathe In")
        elif s % 3 == 1:
            self.ready_go_done.setText("Hold your Breath")
        elif s % 3 == 2:
            self.ready_go_done.setText("Breathe Out")
    
    def eventFilter(self, source, event):
        if source is self.circle_label and event.type() == QEvent.Type.Resize:
            w = self.circle_label.width()
            h = self.circle_label.height()
            side = min(w, h)

            self.circle_label.setStyleSheet(f"""
                background-color: qradialgradient(
                                       spread:pad, 
                                       cx:0.5, 
                                       cy:0.5,
                                       radius:0.8, 
                                       fx:0.5, 
                                       fy:0.5, 
                                       stop:0 #FFD5D5, 
                                       stop:0.26 #FFB5B5, 
                                       stop:1 #FFD5F6); 
                border:0px; 
                border-radius: {side//2}px;
            """)
        return super().eventFilter(source, event)

    def circ_anim(self, loop_count=1, ms=4000):
        if self.anim_group is not None:
            try:
                self.anim_group.stop()
            except Exception:
                pass
        center_point = self.timer_in_circle.geometry().center()
        cx = center_point.x()
        cy = center_point.y()
        
        start_side = 50 
        end_side = 300 
        start_rect = QRect(cx - start_side//2, cy - start_side//2, start_side, start_side)
        end_rect = QRect(cx - end_side//2, cy - end_side//2, end_side, end_side)
        

        anim_expand = QPropertyAnimation(self.circle_label, b"geometry")
        anim_expand.setDuration(ms)
        anim_expand.setStartValue(start_rect)
        anim_expand.setEndValue(end_rect)
        anim_expand.setEasingCurve(QEasingCurve.Type.InOutQuad)

        pause = QPauseAnimation(ms)

        anim_contract = QPropertyAnimation(self.circle_label, b"geometry")
        anim_contract.setDuration(ms)
        anim_contract.setStartValue(end_rect)
        anim_contract.setEndValue(start_rect)
        anim_contract.setEasingCurve(QEasingCurve.Type.InOutQuad)

        anim_expand.valueChanged.connect(self.update_circle_radius)
        anim_contract.valueChanged.connect(self.update_circle_radius)

        self.anim_group = QSequentialAnimationGroup(self)
        self.anim_group.addAnimation(anim_expand)
        self.anim_group.addAnimation(pause)
        self.anim_group.addAnimation(anim_contract)

        self.anim_group.setLoopCount(loop_count)
        if hasattr(self.anim_group, "currentLoopChanged"):
            self.anim_group.currentLoopChanged.connect(self.on_loop_changed)
        self.anim_group.finished.connect(self.on_anim_finished)
        self.anim_group.start()

        return self.anim_group

    def update_circle_radius(self, _value):
        w = self.circle_label.width()
        h = self.circle_label.height()
        side = min(w, h)
        self.circle_label.setStyleSheet(
            f"background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, "
            f"radius:0.8, fx:0.5, fy:0.5, stop:0 #FFD5D5, stop:0.26 #FFB5B5, stop:1 #FFD5F6); "
            f"border:0px; border-radius: {side//2}px;"
        )

    def on_loop_changed(self, loop_index):
        current_cycle = loop_index
        self.cycle_counter_label.setText(f"Number of Cycles Completed: {current_cycle:02}")

    def on_anim_finished(self):
        self.stop()
        self.cycle_counter_label.setText(f"Number of Cycles completed: {self.spinBox_2.value()*5:02}")
        self.ready_go_done.setText("Done")

    def hide(self):
        self.pause_btn.hide()
        self.resume_btn.hide()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    stopwatch = Stopwatch()
    stopwatch.show()
    sys.exit(app.exec())