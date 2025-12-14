from PyQt6.QtWidgets import QMainWindow, QWidget, QListView, QFrame, QMessageBox
from PyQt6 import uic
import sqlite3
import sys
from sqlite3 import Error

# Imports
from ui_components import HoverButton
from main_window import MainWindow
from utils import resource_path,get_db_path

class Profile(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("Profile.ui"),self)
        self.active_profile_id = None
        view1 = QListView()
        view2 = QListView()
        view1.setFrameShape(QFrame.Shape.NoFrame)
        view2.setFrameShape(QFrame.Shape.NoFrame)
        profile_btn = self.profile_btn
        self.profile_btn = HoverButton(profile_btn.text(), self)
        self.profile_btn.setGeometry(profile_btn.geometry())
        self.profile_btn.setStyleSheet(profile_btn.styleSheet())      
        self.profile_btn.setFont(profile_btn.font())                  
        self.profile_btn.setSizePolicy(profile_btn.sizePolicy())      
        self.profile_btn.setCursor(profile_btn.cursor())        
        profile_btn.hide()
        self.profile_btn.clicked.connect(self.save_and_open_main)
        self.init_db()
        #self.save_db()
        self.line_name.returnPressed.connect(self.save_db)
        self.line_goal.returnPressed.connect(self.save_db)
        self.line_height.returnPressed.connect(self.save_db)
        self.line_age.returnPressed.connect(self.save_db)
        self.line_weight.returnPressed.connect(self.save_db)
        
        existing_profile_btn = self.existing_profile_btn
        self.existing_profile_btn = HoverButton(existing_profile_btn.text(), existing_profile_btn.parent())
        self.existing_profile_btn.setGeometry(existing_profile_btn.geometry())
        self.existing_profile_btn.setStyleSheet(existing_profile_btn.styleSheet())      
        self.existing_profile_btn.setFont(existing_profile_btn.font())                      
        self.existing_profile_btn.setSizePolicy(existing_profile_btn.sizePolicy())      
        self.existing_profile_btn.setCursor(existing_profile_btn.cursor())        
        existing_profile_btn.hide()
        self.existing_profile_btn.show()
        self.existing_profile_btn.clicked.connect(self.show_saved_profiles)
        #self.profile_btn.clicked.connect(self.save_db)

            
    def init_db(self):
        connection = sqlite3.connect(get_db_path("entries.db"))
        if connection:
            try:
                cursor = connection.cursor()
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
                connection.commit()
            except Error as e:
                print(e)
                sys.exit(1)
            finally:
                connection.close()

    def save_db(self):
        try:
            ipn = self.line_name.text().strip()
            ipa = self.line_age.text().strip()
            ipg = self.line_goal.text().strip()
            ipw = self.line_weight.text().strip()
            iph = self.line_height.text().strip()
            cal = self.cal_goal_line.text().strip() if self.cal_goal_line.text().strip() else 0
            prot = self.prot_goal_line.text().strip() if self.prot_goal_line.text().strip() else 0
            carb = self.carb_goal_line.text().strip() if self.carb_goal_line.text().strip() else 0
            fat = self.fat_goal_line.text().strip() if self.fat_goal_line.text().strip() else 0
            print(ipn, ipa, ipg, ipw, iph)          
            if not any([ipn, ipa, ipg, ipw, iph]):
                print("All fields empty, not inserting.")
                return False
            connection = sqlite3.connect(get_db_path("entries.db"))
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO entries (name, age, goal_weight, weight, height, cal_goal, prot_goal, carb_goal, fat_goal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (ipn, ipa, ipg, ipw, iph, cal, prot, carb, fat))
            self.active_profile_id = cursor.lastrowid
            connection.commit()
            connection.close()
            print('Inserted')
            return True
        except sqlite3.Error as e:
            print("Error in save_db", e)
            return False

    def show_saved_profiles(self):
        self.win = SavedProfiles()
        self.win.show() 
        self.hide()
    
    def save_and_open_main(self):
        success = self.save_db()
        if success and self.active_profile_id is not None:
            print(f"Opening{self.active_profile_id}")
            self.win = MainWindow(self.active_profile_id)
            self.win.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Error", "Please fill in the profile details first.")

class SavedProfiles(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("showProfile.ui"),self)
        self.load_saved_profiles()
        self.profile_changed()
        take_to_main_btn = self.take_to_main_btn
        self.take_to_main_btn = HoverButton(take_to_main_btn.text(), take_to_main_btn.parent())
        self.take_to_main_btn.setGeometry(take_to_main_btn.geometry())
        self.take_to_main_btn.setStyleSheet(take_to_main_btn.styleSheet())      
        self.take_to_main_btn.setFont(take_to_main_btn.font())                      
        self.take_to_main_btn.setSizePolicy(take_to_main_btn.sizePolicy())      
        self.take_to_main_btn.setCursor(take_to_main_btn.cursor())        
        take_to_main_btn.hide()
        self.take_to_main_btn.show()
        self.take_to_main_btn.clicked.connect(self.take_main)

    def load_saved_profiles(self):
        connection = sqlite3.connect(get_db_path("entries.db"))
        curr = connection.cursor()
        curr.execute("SELECT DISTINCT id, name FROM entries")
        profile = curr.fetchall()
        for pid,pname in profile:
            self.profile_selector.addItem(pname, pid)
        self.profile_selector.currentIndexChanged.connect(self.profile_changed)

    def profile_changed(self):
        selected_id = self.profile_selector.currentData() 
        print("Selected profile ID:", selected_id)
        self.profile_id = selected_id 
    
    def take_main(self):
        self.win = MainWindow(self.profile_id)
       #self.win.setParent(None)
        self.win.show()
        self.hide()