from PyQt6.QtWidgets import QMainWindow, QCompleter, QVBoxLayout, QButtonGroup, QLabel, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import Qt, QDate
import pandas as pd
import sqlite3
import os
from datetime import date

from ui_components import HoverButton
from widgets import IngredientAdd, WorkoutAdd
from scanner import Scanner
from workout_display import DisplayWorkout
from existing_recipes import RecipeLoad
from stopwatch import Stopwatch
from utils import resource_path,get_db_path


class MainWindow(QMainWindow):
    def __init__(self, profile_id):
        super().__init__()
        uic.loadUi(resource_path("Main.ui"), self)
        self.setGeometry(300,0,890,1000)
        self.df = pd.read_csv(resource_path("cleaned_indian_food_nutrition.csv"))
        ingredients = self.df['Ingredient']
        self.active_profile_id = profile_id

        self.daily_cal_goal = 0 
        self.daily_prot_goal = 0
        self.daily_carb_goal = 0 
        self.daily_fat_goal = 0

        self.completer = QCompleter(set(ingredients))
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.meditation_btn.clicked.connect(self.open_meditation)
        popup = self.completer.popup()
        popup.setMinimumWidth(400)
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        popup.setStyleSheet("""
                            QListView{
                            background-color:white;
                            border:1px solid #C0C0C0;
                            border-radius:10px;
                            color:#000000;
                            font: 300 13pt "Epilogue";
                            padding-left:5px;
                            min-height:40px;
                        }
                        QListView::item
                        {
                        background-color: #ebebeb;
                        font:200 10px "Epilogue";
                        border:none;
                        padding:5px;
                        min-height:30px;
                        }
                        QListView::item:hover {
                        background-color: #C0C0C0;
                        color: black;
                }
        """)
        self.nav_buttons = QButtonGroup(self)
        self.nav_buttons.addButton(self.dashboard_btn,0)
        self.nav_buttons.addButton(self.recipe_btn, 1)
        self.nav_buttons.addButton(self.exercise_btn, 2)
        self.nav_buttons.addButton(self.profile_btn, 4)
        self.nav_buttons.addButton(self.meditation_btn)
        self.nav_buttons.idClicked.connect(self.tabWidget.setCurrentIndex)
        self.dashboard_btn.setChecked(True)
        #self.meditation_btn.setChecked(False)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().hide()
        self.today = QDate.currentDate()
        self.date_text = self.today.toString("dddd, MMMM d, yyyy")
        self.day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prog_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if hasattr(self, "day_lbl"):
            self.day_lbl.setText(self.date_text)
        self.cal_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prot_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.carbs_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fats_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rows = []
        self.total_cal = 0
        self.total_prot = 0
        self.total_carbs = 0
        self.total_fat = 0
        #self.update_totals()
        self.cal_counter.setText(f"{self.total_cal:.0f} kcal")
        self.prot_counter.setText(f"{self.total_prot:.1f} g")
        self.carbs_counter.setText(f"{self.total_carbs:.1f} g")
        self.fats_counter.setText(f"{self.total_fat:.1f} g")
        self.scrollArea.setWidgetResizable(True)
        self.scroll_contents.setMinimumHeight(1400)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scan_btn = self.scan_btn
        self.scan_btn = HoverButton(scan_btn.text(), scan_btn.parent())
        self.scan_btn.setGeometry(scan_btn.geometry())
        self.scan_btn.setStyleSheet(scan_btn.styleSheet())      
        self.scan_btn.setFont(scan_btn.font())                      
        self.scan_btn.setSizePolicy(scan_btn.sizePolicy())      
        self.scan_btn.setCursor(scan_btn.cursor())        
        scan_btn.hide()
        self.scan_btn.show()
        self.scan_btn.clicked.connect(self.open_Scanner)
        if hasattr(self, 'search_bar'):
            self.search_bar.setCompleter(self.completer)
        self.ingredients_layout = QVBoxLayout()
        self.ingr_add.setLayout(self.ingredients_layout)
        self.ingredients_layout.setContentsMargins(10,10,10,10)
        self.ingredients_layout.setSpacing(10)
        self.search_bar.returnPressed.connect(self.fetch_data)
        save_recipe_btn = self.save_recipe_btn
        self.save_recipe_btn = HoverButton(save_recipe_btn.text(), save_recipe_btn.parent())
        self.save_recipe_btn.setGeometry(save_recipe_btn.geometry())
        self.save_recipe_btn.setStyleSheet(save_recipe_btn.styleSheet())      
        self.save_recipe_btn.setFont(save_recipe_btn.font())                      
        self.save_recipe_btn.setSizePolicy(save_recipe_btn.sizePolicy())      
        self.save_recipe_btn.setCursor(save_recipe_btn.cursor())        
        save_recipe_btn.hide()
        self.save_recipe_btn.show()
        self.save_recipe_btn.clicked.connect(self.save_recipe)
        #self.new_recipe_btn.clicked.connect()
        recipe_t = self.recipe_t
        self.recipe_t = HoverButton(recipe_t.text(), recipe_t.parent())
        self.recipe_t.setGeometry(recipe_t.geometry())
        self.recipe_t.setStyleSheet(recipe_t.styleSheet())      
        self.recipe_t.setFont(recipe_t.font())                      
        self.recipe_t.setSizePolicy(recipe_t.sizePolicy())      
        self.recipe_t.setCursor(recipe_t.cursor())        
        recipe_t.hide()
        self.recipe_t.show()
        #self.show_recipe_btn.clicked.connect(self.show_recipes)
        self.load_profile()
        self.recipe_t.clicked.connect(self.show_recipes)
        self.exercise_rows = []
        self.workout_db()
        self.muscle_groups = {"Chest": [
    "• Bench Press",
    "• Incline Dumbbell Press",
    "• Decline Bench Press",
    "• Cable Flys",
    "• Dumbbell Flys",
    "• Chest Dips",
    "• Pec Deck Machine",
    "• Push-Ups",
    "• Squeeze Press",
    "• Landmine Chest Press",
    "• Guillotine Press",
    "• Wide Grip Push-Ups",
    "• Single Arm Cable Press",
    "• Plate Press"
],

"Back": [
    "• Deadlift",
    "• Lat Pulldown",
    "• Seated Row",
    "• Pull-Ups",
    "• Bent Over Row",
    "• T-Bar Row",
    "• Single Arm Dumbbell Row",
    "• Back Extensions",
    "• Face Pulls",
    "• Rack Pulls",
    "• Chest Supported Row",
    "• Wide Grip Pull-Ups",
    "• Meadows Row",
    "• Good Mornings",
    "• Inverted Rows"
],

"Shoulder": [
    "• Shoulder Press",
    "• Arnold Press",
    "• Lateral Raise",
    "• Front Raise",
    "• Rear Delt Fly",
    "• Upright Row",
    "• Shrugs",
    "• Seated Dumbbell Press",
    "• Barbell Overhead Press",
    "• One Arm Cable Lateral Raise",
    "• Machine Shoulder Press",
    "• Reverse Pec Deck",
    "• Cable Face Pull",
    "• Plate Front Raise",
    "• Cuban Press"
],

"Biceps": [
    "• Barbell Curl",
    "• Hammer Curl",
    "• Preacher Curl",
    "• Concentration Curl",
    "• Cable Curl",
    "• EZ Bar Curl",
    "• Incline Dumbbell Curl",
    "• Spider Curl",
    "• Reverse Curl",
    "• High Cable Curl",
    "• Drag Curl",
    "• Zottman Curl",
    "• Alternating Dumbbell Curl",
    "• Machine Bicep Curl",
    "• Cable Hammer Curl (Rope)"
],

"Triceps": [
    "• Tricep Pushdown",
    "• Skull Crushers",
    "• Dips",
    "• Overhead Tricep Extensions",
    "• Tricep Rope Extensions",
    "• Close Grip Bench Press",
    "• Diamond Push-Ups",
    "• Kickbacks",
    "• Rope Pushdowns",
    "• French Press",
    "• V-Bar Pushdown",
    "• Tate Press",
    "• Floor Press",
    "• JM Press",
    "• Cable Overhead Rope Extension"
],

"Legs": [
    "• Squat",
    "• Leg Press",
    "• Leg Extensions",
    "• Calf Raises",
    "• Lunges",
    "• Deadlift",
    "• Romanian Deadlift",
    "• Hamstring Curls",
    "• Goblet Squat",
    "• Hip Thrust",
    "• Bulgarian Split Squat",
    "• Step-Ups",
    "• Hack Squat",
    "• Sumo Squat",
    "• Glute Bridges",
    "• Box Squats",
    "• Sled Push",
    "• Walking Lunges",
    "• Jefferson Squat"
]

        }
        self.muscle_combo.addItems([
            "Chest",
            "Back",
            "Legs",
            "Shoulder",
            "Biceps",
            "Triceps",
            "Legs"
        ])
        if self.workouts_container.layout() is None:
            self.workouts_layout = QVBoxLayout(self.workouts_container)
            self.workouts_layout.setContentsMargins(10, 10, 10, 10)
            self.workouts_layout.setSpacing(10)
        else:
            self.workouts_layout = self.workouts_container.layout()
        self.workouts_scroll.setWidgetResizable(True)
        self.scrollAreaWidgetContents.setMinimumHeight(1160)
        self.workouts_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.muscle_combo.currentTextChanged.connect(self.load_exercises_for_muscle)
 
        add_exercise_button = self.add_exercise_button
        self.add_exercise_button = HoverButton(add_exercise_button.text(), add_exercise_button.parent())
        self.add_exercise_button.setGeometry(add_exercise_button.geometry())
        self.add_exercise_button.setStyleSheet(add_exercise_button.styleSheet())      
        self.add_exercise_button.setFont(add_exercise_button.font())                      
        self.add_exercise_button.setSizePolicy(add_exercise_button.sizePolicy())      
        self.add_exercise_button.setCursor(add_exercise_button.cursor())        
        add_exercise_button.hide()
        self.add_exercise_button.show()
        self.add_exercise_button.clicked.connect(self.add_selected_exercise)
 
        save_workout_button = self.save_workout_button
        self.save_workout_button = HoverButton(save_workout_button.text(), save_workout_button.parent())
        self.save_workout_button.setGeometry(save_workout_button.geometry())
        self.save_workout_button.setStyleSheet(save_workout_button.styleSheet())      
        self.save_workout_button.setFont(save_workout_button.font())                      
        self.save_workout_button.setSizePolicy(save_workout_button.sizePolicy())      
        self.save_workout_button.setCursor(save_workout_button.cursor())        
        save_workout_button.hide()
        self.save_workout_button.show()
        self.save_workout_button.clicked.connect(self.save_workout)

        self.meals_layout = self.scroll_contents.layout()


        view_workouts_button = self.view_workouts_button
        self.view_workouts_button = HoverButton(view_workouts_button.text(), view_workouts_button.parent())
        self.view_workouts_button.setGeometry(view_workouts_button.geometry())
        self.view_workouts_button.setStyleSheet(view_workouts_button.styleSheet())      
        self.view_workouts_button.setFont(view_workouts_button.font())                      
        self.view_workouts_button.setSizePolicy(view_workouts_button.sizePolicy())      
        self.view_workouts_button.setCursor(view_workouts_button.cursor())        
        view_workouts_button.hide()
        self.view_workouts_button.show()
        self.view_workouts_button.clicked.connect(self.display_workout)
        
        self.init_recipe_db()
        self.workout_db()
        
        self.load_profile()
        self.load_todays_workouts()
        self.load_today_meals()
        #self.update_totals()
        self.load_profile_items()
                
        delete_profile_btn = self.delete_profile_btn
        self.delete_profile_btn = HoverButton(delete_profile_btn.text(), delete_profile_btn.parent())
        self.delete_profile_btn.setGeometry(delete_profile_btn.geometry())
        self.delete_profile_btn.setStyleSheet(delete_profile_btn.styleSheet())      
        self.delete_profile_btn.setFont(delete_profile_btn.font())                      
        self.delete_profile_btn.setSizePolicy(delete_profile_btn.sizePolicy())      
        self.delete_profile_btn.setCursor(delete_profile_btn.cursor())        
        delete_profile_btn.hide()
        self.delete_profile_btn.show()
        self.delete_profile_btn.clicked.connect(self.delete_profile)
    
    def open_meditation(self):
        self.window = Stopwatch()
        self.window.show()

    def init_recipe_db(self):
        """Initializes the recipe database table."""
        conn = sqlite3.connect(get_db_path("recipes.db"))
        curr = conn.cursor()
        curr.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                recipe_name TEXT,
                ingredient TEXT,
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                date TEXT DEFAULT (DATE('now'))
           )
        """)
        conn.commit()
        conn.close()
        conn = sqlite3.connect(get_db_path("entries.db"))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS entries(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                age INTEGER,
                                weight INTEGER,
                                goal_weight INTEGER,
                                height INTEGER,
                                cal_goal INTEGER,
                                prot_goal INTEGER,
                                carb_goal INTEGER,
                                fat_goal INTEGER)
                           """)
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

    def counters(self):
        self.rows = []
        self.calories = 0
        self.protein = 0
        self.carbs = 0 
        self.fats = 0
        
    def fetch_data(self):
        name = self.search_bar.text().strip().lower()
        if name == "":
            return
        self.df["Ingredient_clean"] = (
            self.df["Ingredient"]
            .str.replace('"', '', regex=False)
            .str.strip()
            .str.lower()
        )
        data = self.df[self.df["Ingredient_clean"].str.contains(name, regex=False)]
        if data.empty:
            print("Ingredient not found")
            return
        row = data.iloc[0]
        macros = {
            "cal": float(row["Calories"]),
            "prot": float(row["Protein"]),
            "carbs": float(row["Carbs"]),
            "fat": float(row["Fat"])
        }
        self.add_ingr(row["Ingredient"].replace('"', '').strip(), macros)
        self.search_bar.clear()


    def add_ingr(self, ingredient_name, macros):
        row = IngredientAdd(ingredient_name, macros)
        row.setStyleSheet("""
            QWidget {
                background-color: #f9f6ff;
                border-radius: 12px;
                font: 14px 'Epilogue';
                color: #1D1D1D;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #d7d7d7; 
                border-radius: 8px;
                padding: 6px 10px;
                color: #1D1D1D;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
            QSpinBox {
                border: 1px solid #d7d7d7;
                border-radius: 8px;
                padding: 4px;
                color: #1D1D1D;
                background-color: white; /* Ensure background is white */
            }
            
            /* THIS HIDES THE WEIRD ARROWS */
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                border: none;
                background: transparent;
            }
        """)
        row.change.connect(self.update_totals)
        row.removed.connect(self.remove_row)
        self.rows.append(row)
        self.ingredients_layout.addWidget(row)
        self.update_totals()
    
    def save_recipe(self):
        recipe_name = self.recipe_name_input.text().strip()
        if recipe_name == "":
            QMessageBox.warning(self, "Error", "Enter recipe name")
            return
        for row in self.rows:
            macros = row.macros
            qty = row.qty.value()
            self.save_to_db(recipe_name, row.name,{
                "cal": float(macros["cal"])*qty,
                "prot": float(macros["prot"])*qty,
                "carbs": float(macros["carbs"])*qty,
                "fat": float(macros["fat"])*qty
            })
        self.load_today_meals()
        print("Recipe saved")
    
    def remove_row(self, row):
        self.ingredients_layout.removeWidget(row)
        self.rows.remove(row)
        row.deleteLater()
        self.update_totals()

    def update_totals(self):
        self.total_cal = self.total_prot = self.total_carbs = self.total_fat = 0
        for row in self.rows:
            qty = row.qty.value()
            macros = row.macros
            self.total_cal += round(float(macros["cal"]) * qty,2)
            self.total_prot += round(float(macros["prot"]) * qty,2)
            self.total_carbs += round(float(macros["carbs"]) * qty,2)
            self.total_fat += round(float(macros["fat"]) * qty,2)
        self.cal_counter.setText(f"{self.total_cal} kcal")
        self.prot_counter.setText(f"{self.total_prot} g")
        self.carbs_counter.setText(f"{self.total_carbs} g")
        self.fats_counter.setText(f"{self.total_fat} g")

        rem_cal = max(0, self.daily_cal_goal - self.total_cal)
        rem_prot = max(0, self.daily_prot_goal - self.total_prot)
        rem_carb = max(0, self.daily_carb_goal - self.total_carbs)
        rem_fat = max(0, self.daily_fat_goal - self.total_fat)

        if hasattr(self, 'left_cal'):
            self.left_cal.setText(f"CALORIES LEFT: {rem_cal:.0f}")
        if hasattr(self, 'left_prot'):
            self.left_prot.setText(f"PROTIEN LEFT: {rem_prot:.1f}g")
        if hasattr(self, 'left_carb'):
            self.left_carb.setText(f"CARBS LEFT: {rem_carb:.1f}g")
        if hasattr(self, 'left_fat'):
            self.left_fat.setText(f"FATS LEFT: {rem_fat:.1f}g")

    def save_to_db(self,recipe_name,name,macros):
        conn = sqlite3.connect(get_db_path("recipes.db"))
        curr = conn.cursor()
        curr.execute("""
            INSERT INTO recipe_ingredients
                      (recipe_name, ingredient, calories, protein, carbs, fat, date, profile_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (recipe_name,
             name,
             macros["cal"], macros["prot"], macros["carbs"], macros["fat"], date.today().isoformat(), self.active_profile_id)
             )
        conn.commit()
        conn.close()

    def load_recipe(self, recipe_name):
        conn = sqlite3.connect(get_db_path("recipes.db"))
        curr = conn.cursor()
        curr.execute("SELECT ingredient, calories, protein, carbs, fat FROM recipe_ingredients WHERE recipe_name=?", (recipe_name,))
        rows = curr.fetchall()
        conn.close()
        return rows 
    
    def load_today_meals(self):
        layout = self.meal_log
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                layout.removeItem(item)
        conn = sqlite3.connect(get_db_path("recipes.db"))
        curr = conn.cursor()
        today = date.today().isoformat()
        curr.execute("""
            SELECT DISTINCT recipe_name 
            FROM recipe_ingredients 
            WHERE date = ? AND profile_id = ?
        """, (today, self.active_profile_id))
        recipes = curr.fetchall()
        if not recipes:
            placeholder = QLabel("No recipes logged today")
            placeholder.setStyleSheet("font-size: 18px; padding: 6px; color: gray;")
            layout.addWidget(placeholder)
        else:
            for recipe in recipes:
                name = recipe[0]
                label = QLabel(name)
                label.setStyleSheet("""
                    QWidget{
                font: 400 20px "Epilogue";
                color:#1d1d1d;
                border-radius:10px;
                background-color:rgb(242, 242, 242);
                border:1px solid #c0c0c0
                }
                """)
                layout.addWidget(label)
        curr.execute("""
            SELECT SUM(calories), SUM(protein), SUM(carbs), SUM(fat)
            FROM recipe_ingredients
            WHERE date = ? AND profile_id = ?
        """, (today, self.active_profile_id))
        row = curr.fetchone()
        conn.close()
        cal_sum = row[0] if row[0] is not None else 0
        prot_sum = row[1] if row[1] is not None else 0
        carb_sum = row[2] if row[2] is not None else 0
        fat_sum = row[3] if row[3] is not None else 0
        self.total_cal = cal_sum
        self.total_prot = prot_sum
        self.total_carbs = carb_sum
        self.total_fat = fat_sum
        self.cal_counter.setText(f"{self.total_cal:.0f} kcal")
        self.prot_counter.setText(f"{self.total_prot:.1f} g")
        self.carbs_counter.setText(f"{self.total_carbs:.1f} g")
        self.fats_counter.setText(f"{self.total_fat:.1f} g")
        rem_cal = max(0, self.daily_cal_goal - self.total_cal)
        rem_prot = max(0, self.daily_prot_goal - self.total_prot)
        rem_carb = max(0, self.daily_carb_goal - self.total_carbs)
        rem_fat = max(0, self.daily_fat_goal - self.total_fat)
        if hasattr(self, 'left_cal'):
            self.left_cal.setText(f"CALORIES LEFT: {rem_cal:.0f}")
        if hasattr(self, 'left_prot'):
            self.left_prot.setText(f"PROTIEN LEFT: {rem_prot:.1f}g")
        if hasattr(self, 'left_carb'):
            self.left_carb.setText(f"CARBS LEFT: {rem_carb:.1f}g")
        if hasattr(self, 'left_fat'):
            self.left_fat.setText(f"FATS LEFT: {rem_fat:.1f}g")

    def workout_db(self):
        print("USING DB:", os.path.abspath("workout_data.db"))
        conn = sqlite3.connect(get_db_path("workout_data.db"))
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            workout_name TEXT,
            exercise_name TEXT,
            sets INTEGER,    
            reps INTEGER,
            weight REAL,
            cal_goal INTEGER,
            prot_goal INTEGER,
            fat_goal INTEGER,
            carb_goal INTEGER,
            date TEXT
        )
    """)
        conn.commit()
        conn.close()

    def load_todays_workouts(self):
        layout = self.workouts_layout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            else:
                layout.removeItem(item)
        conn = sqlite3.connect(get_db_path("workout_data.db"))
        curr = conn.cursor()
        today = date.today().isoformat()
        curr.execute("SELECT DISTINCT workout_name FROM workouts WHERE date=? AND profile_id=? ", (today,self.active_profile_id))
        workouts = curr.fetchall()
        conn.close()
        if not workouts:
            placeholder = QLabel("No workouts logged in today")
            placeholder.setStyleSheet("font:400 18px 'Epilogue'; padding:6px; color:#1d1d1d")
            layout.addWidget(placeholder)
            return
        for w in workouts:
            label = QLabel(w[0])    
            label.setStyleSheet("""
            font: 400 20px "Epilogue";
            color:#1d1d1d;
            border-radius:10px;
            background-color:rgb(242, 242, 242);
            border:1px solid #c0c0c0;
            padding: 6px;
        """)
            layout.addWidget(label)

    def load_profile(self):
        try:
            connection = sqlite3.connect(get_db_path("entries.db"))
            if connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT name, age, goal_weight, weight, height,
                                cal_goal, prot_goal, carb_goal, fat_goal
                                FROM entries where id=?""", 
                                (self.active_profile_id,))
                row = cursor.fetchone()
                if not row:
                    print("No profile found, returning without inserting.")
                    return
                connection.close()
                if row:
                    name, age, goal_weight, weight, height, c_goal, p_goal, cb_goal, f_goal = row
                    self.name_lbl.setText(f"{name}")
                    self.age_lbl.setText(f"{age}")
                    self.goal_lbl.setText(f"{goal_weight}")
                    self.weight_lbl.setText(f"{weight}")
                    self.height_lbl.setText(f"{height}")

                    self.daily_cal_goal = c_goal if c_goal else 0 
                    self.daily_prot_goal = p_goal if p_goal else 0 
                    self.daily_carb_goal = cb_goal if cb_goal else 0 
                    self. daily_fat_goal = f_goal if f_goal else 0
            else:
                print("problem w connection")
        except sqlite3.Error as e:
            print("DB Error is:", e)
        finally:
            connection.close()
        
    def load_exercises_for_muscle(self, muscle):
        self.exercise_list.clear()
        for exercise in self.muscle_groups.get(muscle, []):
            self.exercise_list.addItem(exercise)
    
    def add_selected_exercise(self):
        selected = self.exercise_list.currentItem()
        if not selected:
            return
        exercise_name = selected.text()
        row = WorkoutAdd(exercise_name)
       # row.change.connect(self.update_workout_totals)
        row.removed.connect(self.remove_workout_row)
        self.exercise_rows.append(row)
        self.workouts_layout.addWidget(row)
        #self.update_workout_totals()
    
    def remove_workout_row(self, row):
        self.workouts_layout.removeWidget(row)
        self.exercise_rows.remove(row)
        row.deleteLater()

    def save_workout(self):
        workout_group = self.workout_group_input.text().strip()
        if workout_group == "":
            QMessageBox.warning(self, "Error", "Enter workout group name")
            return
        connection = sqlite3.connect(get_db_path("workout_data.db"))
        cursor = connection.cursor()
        for row in self.exercise_rows:
            sets_val = row.sets_input.value()
            reps_val = row.reps_input.value()
            weight_val = row.weight_input.value()
            cursor.execute("""
                INSERT INTO workouts (workout_name, exercise_name, sets, reps, weight, date, profile_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (workout_group, row.exercise_name, sets_val, reps_val , weight_val, date.today().isoformat(), self.active_profile_id))

        connection.commit()
        connection.close()
        QMessageBox.information(self, "Saved", "Workout saved!")
        self.load_todays_workouts()

    def open_Scanner(self):
        self.window = Scanner()
        self.window.show()
        self.hide()

    def display_workout(self):
        self.work_diplay = DisplayWorkout(self.active_profile_id)
        self.work_diplay.show()
    
    def show_recipes(self):
        self.window = RecipeLoad(self.active_profile_id)
        self.window.show()
    
    def load_profile_items(self):
        conn = sqlite3.connect(get_db_path("entries.db"))
        curr = conn.cursor()
        curr.execute("""SELECT DISTINCT name, age, weight, goal_weight, height 
                     FROM entries WHERE id=?""",(self.active_profile_id,))
        rows = curr.fetchone()

        if rows:
            name, age, weight, goal_weight, height = rows
            self.name_lbl.setText(str(name))
            self.age_lbl.setText(str(age))
            self.height_lbl.setText(str(height))
            self.weight_lbl.setText(str(weight))            
            self.goal_lbl.setText(str(goal_weight))
    
    def delete_profile(self):
        reply = QMessageBox.question(self, "Delete Profile?", f"Are you sure you want to delete profile: {self.name_lbl.text()}?\n this cannot be undone",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(get_db_path("entries.db"))
                curr = conn.cursor()
                curr.execute("DELETE FROM entries WHERE id=?",(self.active_profile_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Deleted", "Profile removed successfully.")
                
                from auth import Profile 

                self.window = Profile()
                self.window.show()
                self.close()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Could not delete profile: {e}")
                print (e)


