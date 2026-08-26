import os
import sqlite3
import time
import pcslib
import easygui
from database import Database
    
class Menu:
    def __init__(self):
        self.db = Database("stellantis_og.db")
        self.model_lookup = {f"{model_code} ({year})": model_id for model_id, model_code, year in self.db.get_menu_models()}
        self.model_choice = easygui.choicebox("Select an OEM Model Code:", "Stellantis OG Extractor", choices=list(self.model_lookup.keys()))
        self.date_choice = easygui.choicebox("Select the date of your Order Guide:", "Stellantis OG Extractor", choices=self.db.get_dates_for_model(self.model_lookup[self.model_choice]))