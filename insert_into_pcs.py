import time
import pcslib
import easygui
import tkinter as tk
from database import Database
    
class ModelMenu:
    def __init__(self):
        self.db = Database("stellantis_og.db")
        self.model_lookup = {f"{model_code} ({year})": model_id for model_id, model_code, year in self.db.get_menu_models()}
        self.model_choice = easygui.multchoicebox("Select an OEM Model Code:", "Stellantis OG Extractor", choices=list(self.model_lookup.keys()))
        for each_model in self.model_choice:
            self.date_choice = easygui.choicebox(f"Select the date of your Order Guide:\nModel selected: {each_model}", "Stellantis OG Extractor", choices=self.db.get_dates_for_model(self.model_lookup[each_model]) + ["Default Date"])
            #get data from DB with SQL
            #option_list = self.db.get_options_from_model_and_date(self.model_lookup[each_model], self.date_choice)
            om = OptionsMenu("test", "test")
            self.option_choice = easygui.multchoicebox(f"Select the options for {each_model}\nDate selected: {self.date_choice}", "Stellantis OG Extractor", choices=self.db.get_options_from_model_and_date(self.model_lookup[each_model], self.date_choice))
            #Insert(each_model, self.date_choice, self.db.get_options_from_model_and_date(self.model_lookup[each_model], self.date_choice))

class OptionsMenu:
    def __init__(self, order_guide_option_list, pcs_option_list):
        root = tk.Tk()
        root.title("Order Guide Options vs. PCS Options")
        root.geometry("600x400")

        # Create a frame to hold our two lists
        frame = tk.Frame(root)
        frame.pack(padx=20, pady=20)

        # Create the first list
        list1 = tk.Listbox(frame, width=30, height=15)
        list1.grid(row=0, column=0, padx=10)

        # Create the second list
        list2 = tk.Listbox(frame, width=30, height=15)
        list2.grid(row=0, column=1, padx=10)

        # Add some items
        list1.insert(tk.END, "Apple")
        list1.insert(tk.END, "Banana")
        list1.insert(tk.END, "Orange")

        list2.insert(tk.END, "Car")
        list2.insert(tk.END, "Bus")
        list2.insert(tk.END, "Train")

        # Start the GUI
        root.mainloop()


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