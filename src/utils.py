import os 
import sys 

def resource_path(realtive_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath('.')
    return os.path.join(base_path,realtive_path)

def get_db_path(db_filename):
    user_dir = os.path.expanduser('~/Jackfruit/nutrifit_app')
    if not user_dir:
        os.makedirs(user_dir)
    return os.path.join(user_dir, db_filename)
