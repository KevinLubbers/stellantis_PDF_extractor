import time
import pcslib
import easygui
from database import Database
    
class Menu:
    def __init__(self):
        self.db = Database("stellantis_og.db")
        self.model_lookup = {f"{model_code} ({year})": model_id for model_id, model_code, year in self.db.get_menu_models()}
        self.model_choice = easygui.multchoicebox("Select an OEM Model Code:", "Stellantis OG Extractor", choices=list(self.model_lookup.keys()))
        for each_model in self.model_choice:
            self.date_choice = easygui.multchoicebox(f"Select the date of your Order Guide:\nModel selected: {each_model}", "Stellantis OG Extractor", choices=self.db.get_dates_for_model(self.model_lookup[each_model]) + ["Default Date"])
            #get data from DB with SQL
            Insert(each_model, self.date_choice, self.db.get_options_from_model_and_date(self.model_lookup[each_model], self.date_choice))


class Insert:
    def __init__(self, model_code, year, model_options_list):
        self.model_code = model_code
        self.model_options_list = model_options_list
        pcslib.focus_pcs()
        #order of select_model(model_year, model_code)
        pcslib.select_model(year, model_code)
        time.sleep(2)
        #loop through all options
        for each_option in model_options_list:
            #order of select_option(option, name, category, invoice, msrp)
            pcslib.select_option()
            pcslib.option_back_reset()
        #back out of options screen
        pcslib.back()
        #reverse tab back to model search box
        pcslib.back_reset()