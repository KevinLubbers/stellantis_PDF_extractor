import pymupdf
import re
import easygui
import json
from datetime import datetime
from database import Database
from insert_into_pcs import Menu

#many model_dicts are stored in this list
model_list = []
#each model_dict has a list of options
model_dict = {}
#each option dict is stored in this list
list_of_options = []
#each option has its own dict
options_dict = {}

#Regex Patterns - old ones are for future testing / quick lookup

#model_pattern = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z]{4}\d{2}")
model_pattern = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z0-9]{6}\n")
dfrt_pattern = re.compile(r"DESTINATION CHARGE\n\d{1,3},?\d{1,3}|DESTINATIONCHARGE\n\d{1,3},?\d{1,3}")
engine_trans_with_price = re.compile(r"\([A-Z][A-Z]?\d?[A-Z]?\d?\)\n\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}")
engine_trans_no_price = re.compile(r"\([A-Z0-9]{3,}\)\nN\/C\nN\/C")
#expertimenting with last OR statement for 2024 TRX, not matching Y7TR
option_no_price = re.compile(r"N\/C\nN\/C\n[A-Z0-9]{4}\n|N\/C\nN\/C\n[A-Z0-9]{3}\n")
option_with_price = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z][A-Z0-9]{2,3}?\n")
option_no_price_with_package = re.compile(r"N\/C\nN\/C\n(?:P\n)+[A-Z0-9]{4}\n|N\/C\nN\/C\n(?:P\n)+[A-Z0-9]{3}\n")
option_with_price_with_package = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n(?:P\n)+[A-Z][A-Z0-9]{2,3}?\n")
#option_with_price = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z][A-Z0-9]{2,3}?\n")
#option_no_price = re.compile(r"N\/C\nN\/C\n[A-Z][A-Z]?\d?[A-Z]?\d?")
#option_with_price = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z0-9]{3,4}?\n")

#start functions
def check_for_exact_duplicate(last_entry, new_entry):
    if last_entry["option_code"] == new_entry["option_code"] and last_entry["invoice"] == new_entry["invoice"] and last_entry["msrp"] == new_entry["msrp"]:
        return True
    else:
        return False
#do I need to check for exact duplicates 2 levels up? Currently we only go 1 level up and we found 1 duplicate that happened on a single alternate.
#if we checked 2 levels up we could have prevented the duplicate, but do we go three levels up then? where does it stop?

def handle_model(text):
    global model_list
    global model_dict
    global list_of_options
    global options_dict
    if model_dict:
        model_dict["options"] = list_of_options
        model_list.append(model_dict)
        model_dict = {}
        list_of_options = []
    split_text = text.replace(",", "").split("\n")
    split_text[0] = int(split_text[0])
    split_text[1] = int(split_text[1])
    if split_text[0] > split_text[1]:
        msrp = split_text[0]
        invoice = split_text[1]
    else:
        msrp = split_text[1]
        invoice = split_text[0]

    model_dict["model"] = split_text[2]
    model_dict["year"] = "2027"
    options_dict = {"option_code": "*MDL",
                    "invoice": invoice,
                    "msrp": msrp}
    list_of_options.append(options_dict)

def handle_dfrt(text):
    global list_of_options
    global options_dict
    split_text = text.replace(",", "").split("\n")
    split_text[1] = int(split_text[1])
    msrp = split_text[1]
    invoice = split_text[1]
    options_dict = {"option_code": "DFRT",
                    "invoice": invoice,
                    "msrp": msrp}
    list_of_options.append(options_dict)

def handle_engine_trans_with_price(text):
    global list_of_options
    global options_dict
    split_text = text.replace(",", "").split("\n")
    opt = split_text[0].replace("(", "").replace(")", "")
    split_text[1] = int(split_text[1])
    split_text[2] = int(split_text[2])
    if split_text[2] > split_text[1]:
        msrp = split_text[2]
        invoice = split_text[1]
    else:
        msrp = split_text[1]
        invoice = split_text[2]

    options_dict = {"option_code": opt,
                    "invoice": invoice,
                    "msrp": msrp}
    if not check_for_exact_duplicate(list_of_options[-1], options_dict) and not check_for_exact_duplicate(list_of_options[-2], options_dict):
        list_of_options.append(options_dict)

def handle_engine_trans_no_price(text):
    global list_of_options
    global options_dict
    split_text = text.split("\n")
    opt = split_text[0].replace("(", "").replace(")", "")
    options_dict = {"option_code": opt,
                    "invoice": 0,
                    "msrp": 0}
    if not check_for_exact_duplicate(list_of_options[-1], options_dict) and not check_for_exact_duplicate(list_of_options[-2], options_dict):
        list_of_options.append(options_dict)

def handle_option_no_price(text):
    global list_of_options
    global options_dict
    split_text = text.split("\n")
    opt = split_text[2]
    options_dict = {"option_code": opt,
                    "invoice": 0,
                    "msrp": 0}
    if not check_for_exact_duplicate(list_of_options[-1], options_dict) and not check_for_exact_duplicate(list_of_options[-2], options_dict):
        list_of_options.append(options_dict)

def handle_option_with_price(text):
    global list_of_options
    global options_dict
    split_text = text.replace(",", "").split("\n")
    opt = split_text[2]
    split_text[0] = int(split_text[0])
    split_text[1] = int(split_text[1])
    if split_text[1] > split_text[0]:
        msrp = split_text[1]
        invoice = split_text[0]
    else:
        msrp = split_text[0]
        invoice = split_text[1]

    options_dict = {"option_code": opt,
                    "invoice": invoice,
                    "msrp": msrp}
    if not check_for_exact_duplicate(list_of_options[-1], options_dict) and not check_for_exact_duplicate(list_of_options[-2], options_dict):
        list_of_options.append(options_dict)

def handle_option_no_price_with_package(text):
    global list_of_options
    global options_dict
    split_text = text.replace("P\n", "").split("\n")
    opt = split_text[2]
    options_dict = {"option_code": opt,
                    "invoice": 0,
                    "msrp": 0}
    if not check_for_exact_duplicate(list_of_options[-1], options_dict) and not check_for_exact_duplicate(list_of_options[-2], options_dict):
        list_of_options.append(options_dict)

def handle_option_with_price_with_package(text):
    global list_of_options
    global options_dict
    split_text = text.replace("P\n", "").replace(",", "").split("\n")
    opt = split_text[2]
    split_text[0] = int(split_text[0])
    split_text[1] = int(split_text[1])
    if split_text[1] > split_text[0]:
        msrp = split_text[1]
        invoice = split_text[0]
    else:
        msrp = split_text[0]
        invoice = split_text[1]

    options_dict = {"option_code": opt,
                    "invoice": invoice,
                    "msrp": msrp}
    if not check_for_exact_duplicate(list_of_options[-1], options_dict) and not check_for_exact_duplicate(list_of_options[-2], options_dict):
        list_of_options.append(options_dict)

regexChecker = {
    model_pattern: handle_model,
    dfrt_pattern: handle_dfrt,
    engine_trans_with_price: handle_engine_trans_with_price,
    engine_trans_no_price: handle_engine_trans_no_price,
    option_no_price: handle_option_no_price,
    option_with_price: handle_option_with_price,
    option_no_price_with_package: handle_option_no_price_with_package,
    option_with_price_with_package: handle_option_with_price_with_package
}

def handleRow(text):
    for pattern, handler in regexChecker.items():
        if re.search(pattern, text):
            handler(text)
#end functions


#start main
def main():
    file_path = easygui.fileopenbox(title="Select the Stellantis OG to Extract", filetypes=["*.pdf"])
    whole_text = ""
    with pymupdf.open(file_path) as pdf:
        # Loop through each page
        for page_number in range(pdf.page_count):
            page = pdf.load_page(page_number)
            
            # Extract text from the page
            page_text = page.get_text("text")
            whole_text += page_text

        #pattern = r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z]{4}\d{2}|DESTINATION CHARGE\n\d{1,3},?\d{1,3}|\([A-Z][A-Z]?\d?[A-Z]?\d?\)\n\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}|\([A-Z0-9]{3,}\)\nN\/C\nN\/C|N\/C\nN\/C\n[A-Z][A-Z]?\d?[A-Z]?\d?|\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z0-9]{3,}\n"
        #Massive Regex for first pull of data out of text. We get granular later
        pattern = re.compile(f"{model_pattern.pattern}|{dfrt_pattern.pattern}|{engine_trans_with_price.pattern}|{engine_trans_no_price.pattern}|{option_no_price.pattern}|{option_with_price.pattern}|{option_no_price_with_package.pattern}|{option_with_price_with_package.pattern}")
        matches = re.findall(pattern, whole_text)


        #loop through matches from big regex, calls functions based off pattern matched 
        for m in matches:
            options_dict = {}
            handleRow(m)
            

    #adding last model to model_list    
    model_dict["options"] = list_of_options
    model_list.append(model_dict)    
    #print(model_list)

    try:

        db = Database("stellantis_og.db")
        db.create_model_table()
        db.create_options_table()
        divisions = db.get_divisions()
        division_lookup = {name: id for id, name in divisions}
        
        
        choice = 0
        year = 2027
        division_id = 10
        division_name = "JEP"
        effective_date = datetime.now().strftime("%m/%d/%Y")
        while choice != 3:
            choice = easygui.indexbox(
                msg=(f"Year Selected: {year}\nDivision Selected: {division_name}\nEffective Date Selected: {effective_date}\n\nWhat would you like to do next?"),
                title="Select an option",
                choices=("Set Year, Division, and OG Effective Date", "Save JSON data to SQLite Database", "Insert SQLite Data into PCS Database", "Extract Another Order Guide", "Exit")
            )
            match choice:
                case 0:
                    # Set Year, Division, and Effective Date
                    options_choice = easygui.choicebox("Select an action:", "Stellantis OG Extractor", choices=["Set Year", "Set Division", "Set Effective Date"])
                    match options_choice:
                        case "Set Year":
                            year = easygui.enterbox("Enter the year:", default=year)
                        case "Set Division":
                            division_name = easygui.choicebox("Select the division:", "Stellantis OG Extractor", choices=list(division_lookup.keys()))
                            division_id = division_lookup[division_name]
                        case "Set Effective Date":
                            effective_date = easygui.enterbox("Enter the effective date of this Order Guide:\n\nMM/DD/YYYY Format", default=effective_date)
                case 1:
                    # Save to SQLite Database
                    for each_model in model_list:
                        last_row = db.get_or_create_model(division_id=division_id,model_code=each_model["model"],year=year)
                        if db.order_guide_exists(effective_date, last_row):
                            continue
                        else:
                            for each_option in each_model["options"]:
                                db.save_option({"model_id": last_row, "option_code": each_option["option_code"], "invoice": each_option["invoice"], "msrp": each_option["msrp"], "effective_date": effective_date})
                case 2:
                    #Insert SQLite Data into PCS Database
                    menu_choice = Menu()
                case 3:
                    #Extract Another Order Guide
                    return
                case 4:
                    # Exit
                    print("Goodbye!")
                    exit()

    except Exception as e:
        print(f"Error: {e}")
    #end main

while True:
    main()