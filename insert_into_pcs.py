import os
import sqlite3
import time
import pcslib
import easygui
from database import Database
    
class Menu:
    def __init__(self):
        self.db = Database("stellantis_og.db")
        self.model_lookup = {name: id for id, name in self.db.get_menu_models()}
        self.choice = easygui.choicebox("Select an option:", "Stellantis OG Extractor", choices=list(self.model_lookup.keys()))