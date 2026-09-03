import time
import pcslib
import easygui
import tkinter as tk
from tkinter import ttk
from database import Database
    
class ModelMenu:
    def __init__(self):
        self.db = Database("stellantis_og.db")
        self.model_lookup = {f"{model_code} ({year})": model_id for model_id, model_code, year in self.db.get_menu_models()}
        self.model_choice = easygui.multchoicebox("Select an OEM Model Code:", "Stellantis OG Extractor", choices=list(self.model_lookup.keys()))
        for each_model in self.model_choice:
            self.date_choice = easygui.choicebox(f"Select the date of your Order Guide:\nModel selected: {each_model}", "Stellantis OG Extractor", choices=self.db.get_dates_for_model(self.model_lookup[each_model]) + ["Default Date"])
            #get data from DB with SQL
            model_code = each_model.split(" (")[0]
            year = each_model.split(" (")[1].split(")")[0]
            option_list = self.db.get_options_from_model_and_date(self.model_lookup[each_model], self.date_choice)
            Insert(model_code, year, option_list)

class CompareMenu:
    def __init__(self, order_guide_option_list, pcs_option_list):
        root = tk.Tk()
        root.title("Order Guide Options vs. PCS Options")
        root.geometry("700x450")

        style = ttk.Style(root)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            rowheight=30,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#2F5597",
            foreground="white",
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#4472C4")],
            foreground=[("selected", "white")]
        )

        frame = ttk.Frame(root)
        frame.pack(padx=20, pady=20)

        # -------------------------
        # Left frame
        # -------------------------
        left_frame = ttk.Frame(frame)
        left_frame.grid(row=0, column=0, padx=10)

        left_label = ttk.Label(left_frame, text="Order Guide Options")
        left_label.pack()

        list1 = ttk.Treeview(
            left_frame,
            columns=("option_code", "invoice", "msrp"),
            show="headings",
            height=15
        )

        list1.heading("option_code", text="Option Code")
        list1.heading("invoice", text="Invoice")
        list1.heading("msrp", text="MSRP")

        list1.column("option_code", width=120)
        list1.column("invoice", width=100)
        list1.column("msrp", width=100)

        list1.pack(pady=5)


        # -------------------------
        # Right frame
        # -------------------------
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=0, column=1, padx=10)

        right_label = ttk.Label(right_frame, text="PCS Options")
        right_label.pack()

        list2 = ttk.Treeview(
            right_frame,
            columns=("option_code", "option_name"),
            show="headings",
            height=15
        )

        list2.heading("option_code", text="Option Code")
        list2.heading("option_name", text="Option Name")

        list2.column("option_code", width=120)
        list2.column("option_name", width=100)

        list2.pack(pady=5)


        # -------------------------
        # Add rows
        # -------------------------

        for each_option in order_guide_option_list:
            list1.insert("", "end", values=(each_option[0], each_option[1], each_option[2]))

        for each_option in pcs_option_list:
            list2.insert("", "end", values=(each_option[0], each_option[1]))

        # Start the GUI
        root.mainloop()

class AddOptionMenu:
    def __init__(self):
        categories = ["EXT", "INT", "IND", "GROUP", "ENG", "TRANS", "RADIO", "WHEEL", "TIRES", "EXTFTR", "EXTFT1", "ROOF", "DECOR"]
        self.option_name = easygui.enterbox("Option Missing from PCS\nAdd Option Name", "Stellantis OG Extractor")
        self.category_choice = easygui.choicebox("Option Missing from PCS\nAdd Option Category", "Stellantis OG Extractor", choices=categories)

class Insert:
    def __init__(self, model_code, year, model_options_list):
        pcslib.focus_pcs()
        #order of select_model (model_code, year)
        pcslib.select_model(model_code, year)
        time.sleep(2)
        pcs_options_list = pcslib.get_all_options()
        #loop through all options
        for each_option in model_options_list:
            #order of select_option(option, invoice, msrp)
            option_is_present_flag = pcslib.stellantis_select_option(each_option[0], each_option[1], each_option[2])
            if option_is_present_flag == False:
                menu = AddOptionMenu()
                #order of add_option(option_code, option_name, category, invoice, msrp)
                pcslib.add_option(each_option[0], menu.option_name, menu.category_choice, each_option[1], each_option[2])
            pcslib.option_back_reset()
        choice = CompareMenu(model_options_list, pcs_options_list)
        #back out of options screen
        pcslib.back()
        #reverse tab back to model search box
        pcslib.back_reset()