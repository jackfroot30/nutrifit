import sqlite3
conn = sqlite3.connect("recipes.db")
curr = conn.cursor()
curr.execute("SELECT * FROM recipe_ingredients")
rows = curr.fetchall()
conn.close()
print(rows)
