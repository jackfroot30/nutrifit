from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
import sqlite3
from utils import resource_path,get_db_path


class DisplayWorkout(QWidget):
    def __init__(self, profile_id):
        super().__init__()
        uic.loadUi(resource_path("workouts.ui"), self)
        self.profile_id = profile_id
        self.load_workout_in_new_window()
        self.workout_name_list.currentIndexChanged.connect(self.load_names_of_exercises)
        self.load_names_of_exercises()
        self.goback_btn.clicked.connect(self.hide)

    def load_workout_in_new_window(self):
        conn = sqlite3.connect(get_db_path("workout_data.db"))
        curr1 = conn.cursor()
        curr1.execute("SELECT DISTINCT workout_name FROM workouts WHERE profile_id=?", (self.profile_id,))
        workout= curr1.fetchall()
        conn.close()
        self.workout_name_list.clear()
        if not workout:
            self.workout_name_list.addItem("No workouts found")
            self.workout_name_list.setEnabled(False)
        else:
            self.workout_name_list.setEnabled(True)
            for (name,) in workout:
                self.workout_name_list.addItem(name)

    def load_names_of_exercises(self):
        name = self.workout_name_list.currentText()
        if not name or name == "workouts not found":
            self.workout_disp_widget.clear()
            return
        conn = sqlite3.connect(get_db_path("workout_data.db"))
        curr2 = conn.cursor()
        print(name)
        curr2.execute("""
            SELECT exercise_name, sets, reps, weight, date 
            FROM workouts 
            WHERE workout_name=? AND profile_id=?
            ORDER BY date DESC
        """, (name, self.profile_id))
        data = curr2.fetchall()
        conn.close()
        self.workout_disp_widget.clear()
        for exercise, sets, reps, weight, date_str in data:
            display_text = f"{date_str} | {exercise}: {sets} sets x {reps} reps ({weight} kg)"
            self.workout_disp_widget.addItem(display_text)