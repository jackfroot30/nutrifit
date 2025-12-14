from PyQt6.QtWidgets import QWidget, QApplication, QListWidgetItem
from PyQt6 import uic
from PyQt6.QtCore import Qt, QDate
import sqlite3
import sys 
from utils import resource_path,get_db_path

class RecipeLoad(QWidget):
    def __init__(self, profile_id):
        super().__init__()
        uic.loadUi(resource_path("existing_recipes.ui"),self)
        self.profile_id = profile_id
        self.load_the_recipes()
        
    def load_the_recipes(self):
        conn = sqlite3.connect(get_db_path("recipes.db"))
        curr = conn.cursor()
        curr.execute("""SELECT DISTINCT recipe_name, ingredient FROM recipe_ingredients 
                     WHERE profile_id=? ORDER BY recipe_name""", (self.profile_id,))
        rows = curr.fetchall()
        conn.close()

        recipes_dict = {}
        for recipe_name, ingredients in rows:
            if recipe_name not in recipes_dict:
                recipes_dict[recipe_name] = []
            recipes_dict[recipe_name].append(ingredients)

        self.display_recipes.clear()

        for recipe_name, ingredient_list in recipes_dict.items():
            ingredient_str = ", ".join(ingredient_list)
            display_text = f"{recipe_name}:\n{ingredient_str}"
            item = QListWidgetItem(display_text)
            self.display_recipes.addItem(item)


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = RecipeLoad()
    sys.exit(app.exec())
