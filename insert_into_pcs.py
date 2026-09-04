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
        self.root = tk.Tk()
        self.root.title("Order Guide Options vs. PCS Options")
        self.root.geometry("900x900")
        self.root.attributes("-topmost", True)

        style = ttk.Style(self.root)
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

        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # =========================================================
        # TOP: Main Lists
        # =========================================================

        # -------------------------
        # Left frame - Order Guide
        # -------------------------
        left_frame = ttk.Frame(frame)
        left_frame.grid(row=0, column=0, padx=10, sticky="n")

        left_label = ttk.Label(
            left_frame,
            text="Order Guide Options"
        )
        left_label.pack()

        self.list1 = ttk.Treeview(
            left_frame,
            columns=("option_code", "invoice", "msrp"),
            show="headings",
            height=12
        )

        self.list1.heading("option_code", text="Option Code")
        self.list1.heading("invoice", text="Invoice")
        self.list1.heading("msrp", text="MSRP")

        self.list1.column("option_code", width=120)
        self.list1.column("invoice", width=100)
        self.list1.column("msrp", width=100)

        self.list1.pack(pady=5)


        # -------------------------
        # Right frame - PCS
        # -------------------------
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=0, column=1, padx=10, sticky="n")

        right_label = ttk.Label(
            right_frame,
            text="PCS Options"
        )
        right_label.pack()

        list2 = ttk.Treeview(
            right_frame,
            columns=("option_code", "option_name"),
            show="headings",
            height=12
        )

        list2.heading("option_code", text="Option Code")
        list2.heading("option_name", text="Option Name")

        list2.column("option_code", width=160)
        list2.column("option_name", width=160)

        list2.pack(pady=5)


        # =========================================================
        # Difference highlighting
        # =========================================================

        self.list1.tag_configure(
            "different",
            background="lightgreen"
        )

        list2.tag_configure(
            "different",
            background="lightcoral"
        )


        # =========================================================
        # Add rows to main lists
        # =========================================================

        list1_options = {
            option[0] for option in order_guide_option_list
        }

        list2_options = {
            option[0] for option in pcs_option_list
        }

        only_in_list1 = list1_options - list2_options
        only_in_list2 = list2_options - list1_options

        for each_option in order_guide_option_list:
            if each_option[0] in only_in_list1:
                self.list1.insert(
                    "",
                    "end",
                    values=(
                        each_option[0],
                        each_option[1],
                        each_option[2]
                    ),
                    tags=("different",)
                )
            else:
                self.list1.insert(
                    "",
                    "end",
                    values=(
                        each_option[0],
                        each_option[1],
                        each_option[2]
                    )
                )

        for each_option in pcs_option_list:
            if each_option[0] in only_in_list2:
                list2.insert(
                    "",
                    "end",
                    values=(
                        each_option[0],
                        each_option[1]
                    ),
                    tags=("different",)
                )
            else:
                list2.insert(
                    "",
                    "end",
                    values=(
                        each_option[0],
                        each_option[1]
                    )
                )


        # =========================================================
        # BUTTONS
        # =========================================================

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=15
        )

        # -------------------------
        # Remove from List 1
        # -------------------------
        def remove_selected():
            selected = self.list1.selection()

            if not selected:
                return

            for item_id in selected:
                values = self.list1.item(item_id, "values")

                # Add to "Removed" list
                removed_list.insert(
                    "",
                    "end",
                    values=values
                )

                # Remove from main list
                self.list1.delete(item_id)


        remove_button = ttk.Button(
            button_frame,
            text="Remove Selected",
            command=remove_selected
        )
        remove_button.grid(row=0, column=0, padx=10)


        # -------------------------
        # Mark for Delete
        # -------------------------
        def mark_for_delete():
            selected = list2.selection()

            if not selected:
                return

            for item_id in selected:
                values = list2.item(item_id, "values")

                # Add to delete list
                self.delete_list.insert(
                    "",
                    "end",
                    values=values
                )

        delete_button = ttk.Button(
            button_frame,
            text="Mark for Delete",
            command=mark_for_delete
        )
        delete_button.grid(row=0, column=1, padx=10)


        done_button = ttk.Button(
            button_frame,
            text="Done",
            command=self.finish
        )
        done_button.grid(row=0, column=2, padx=10)
        # =========================================================
        # BOTTOM: Smaller Lists
        # =========================================================

        bottom_frame = ttk.Frame(frame)
        bottom_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            pady=10,
            sticky="ew"
        )


        # -------------------------
        # Removed List
        # -------------------------
        removed_frame = ttk.Frame(bottom_frame)
        removed_frame.grid(
            row=0,
            column=0,
            padx=10
        )

        removed_label = ttk.Label(
            removed_frame,
            text="Removed from Order Guide"
        )
        removed_label.pack()

        removed_list = ttk.Treeview(
            removed_frame,
            columns=("option_code", "invoice", "msrp"),
            show="headings",
            height=5
        )

        removed_list.heading(
            "option_code",
            text="Option Code"
        )
        removed_list.heading(
            "invoice",
            text="Invoice"
        )
        removed_list.heading(
            "msrp",
            text="MSRP"
        )

        removed_list.column("option_code", width=120)
        removed_list.column("invoice", width=100)
        removed_list.column("msrp", width=100)

        removed_list.pack()


        # -------------------------
        # Delete List
        # -------------------------
        delete_frame = ttk.Frame(bottom_frame)
        delete_frame.grid(
            row=0,
            column=1,
            padx=10
        )

        delete_label = ttk.Label(
            delete_frame,
            text="Delete from PCS"
        )
        delete_label.pack()

        self.delete_list = ttk.Treeview(
            delete_frame,
            columns=("option_code", "option_name"),
            show="headings",
            height=5
        )

        self.delete_list.heading(
            "option_code",
            text="Option Code"
        )
        self.delete_list.heading(
            "option_name",
            text="Option Name"
        )

        self.delete_list.column("option_code", width=150)
        self.delete_list.column("option_name", width=150)

        self.delete_list.pack()

        self.root.wait_window()

    def finish(self):
        self.list1 = [
            self.list1.item(item, "values")
            for item in self.list1.get_children()
        ]

        self.deletion_list = [
            self.delete_list.item(item, "values")
            for item in self.delete_list.get_children()
        ]

        self.root.destroy()

class AddOptionMenu:
    def __init__(self):
        categories = ["EXT", "INT", "IND", "GROUP", "ENG", "TRANS", "RADIO", "WHEEL", "TIRES", "EXTFTR", "EXTFT1", "ROOF", "DECOR"]
        self.option_name = easygui.enterbox("Option Missing from PCS\nAdd Option Name", "Stellantis OG Extractor")
        self.category_choice = easygui.choicebox("Option Missing from PCS\nAdd Option Category", "Stellantis OG Extractor", choices=categories)

class Insert:
    def __init__(self, model_code, year, model_options_list):
        pcslib.focus_pcs()
        pcslib.select_model(model_code, year)
        time.sleep(2)
        
        pcs_options_list = pcslib.get_all_options()

        compare_menu = CompareMenu(model_options_list, pcs_options_list)
        trimmed_model_options_list = compare_menu.list1
        list_to_delete = compare_menu.delete_list

        print(trimmed_model_options_list)
        print(list_to_delete)

        #Delete list in PCS Database
        for each_option in list_to_delete:
            pcslib.stellantis_select_and_delete_option(each_option[0])

        last_option = ""
        #loop through all options - from newly trimmed list
        for each_option in trimmed_model_options_list:
            differential_pricing_flag = False
            if last_option == each_option[0]:
                differential_pricing_flag = True
            #order of select_option(option, invoice, msrp)
            option_is_present_flag = pcslib.stellantis_select_option(each_option[0], each_option[1], each_option[2], differential_pricing_flag)
            if option_is_present_flag == False:
                menu = AddOptionMenu()
                #order of add_option(option_code, option_name, category, invoice, msrp)
                pcslib.add_option(each_option[0], menu.option_name, menu.category_choice, each_option[1], each_option[2])
            pcslib.option_back_reset()
            last_option = each_option[0]
        #back out of options screen
        pcslib.back()
        #reverse tab back to model search box
        pcslib.back_reset()