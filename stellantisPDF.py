import pymupdf
import re
import easygui
import json

#many model_dicts are stored in this list
model_list = []
#each model_dict has a list of options
model_dict = {}
#each option dict is stored in this list
list_of_options = []
#each option has its own dict
options_dict = {}


#model_pattern = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z]{4}\d{2}")
model_pattern = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z0-9]{6}\n")
dfrt_pattern = re.compile(r"DESTINATION CHARGE\n\d{1,3},?\d{1,3}|DESTINATIONCHARGE\n\d{1,3},?\d{1,3}")
engine_trans_with_price = re.compile(r"\([A-Z][A-Z]?\d?[A-Z]?\d?\)\n\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}")
engine_trans_no_price = re.compile(r"\([A-Z0-9]{3,}\)\nN\/C\nN\/C")
#expertimenting with last OR statement for 2024 TRX, not matching Y7TR
option_no_price = re.compile(r"N\/C\nN\/C\n[A-Z0-9]{4}\n|N\/C\nN\/C\n[A-Z0-9]{3}\n")
#option_no_price = re.compile(r"N\/C\nN\/C\n[A-Z][A-Z]?\d?[A-Z]?\d?")
#option_with_price = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z0-9]{3,4}?\n")
option_with_price = re.compile(r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z][A-Z0-9]{2,3}?\n")

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
    model_dict["year"] = "2026"
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
    list_of_options.append(options_dict)

def handle_engine_trans_no_price(text):
    global list_of_options
    global options_dict
    split_text = text.split("\n")
    opt = split_text[0].replace("(", "").replace(")", "")
    options_dict = {"option_code": opt,
                    "invoice": 0,
                    "msrp": 0}
    list_of_options.append(options_dict)

def handle_option_no_price(text):
    global list_of_options
    global options_dict
    split_text = text.split("\n")
    opt = split_text[2]
    options_dict = {"option_code": opt,
                    "invoice": 0,
                    "msrp": 0}
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
    list_of_options.append(options_dict)

regexChecker = {
    model_pattern: handle_model,
    dfrt_pattern: handle_dfrt,
    engine_trans_with_price: handle_engine_trans_with_price,
    engine_trans_no_price: handle_engine_trans_no_price,
    option_no_price: handle_option_no_price,
    option_with_price: handle_option_with_price
}

def handleRow(text):
    for pattern, handler in regexChecker.items():
        if re.search(pattern, text):
            handler(text)

file_path = easygui.fileopenbox(title="Select the Stellantis OG to Extract", filetypes=["*.pdf"])
#hard coded file_path = "wrangler2026.pdf"
whole_text = ""
with pymupdf.open(file_path) as pdf:
    # Loop through each page
    #for page_number in range(1, 12):
    for page_number in range(pdf.page_count):
        page = pdf.load_page(page_number)
        
        # Extract tables from the page
        page_text = page.get_text("text")
        whole_text += page_text

    #pattern = r"\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z]{4}\d{2}|DESTINATION CHARGE\n\d{1,3},?\d{1,3}|\([A-Z][A-Z]?\d?[A-Z]?\d?\)\n\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}|\([A-Z0-9]{3,}\)\nN\/C\nN\/C|N\/C\nN\/C\n[A-Z][A-Z]?\d?[A-Z]?\d?|\d{1,3},?\d{1,3}\n\d{1,3},?\d{1,3}\n[A-Z0-9]{3,}\n"
    pattern = re.compile(f"{model_pattern.pattern}|{dfrt_pattern.pattern}|{engine_trans_with_price.pattern}|{engine_trans_no_price.pattern}|{option_no_price.pattern}|{option_with_price.pattern}")
    matches = re.findall(pattern, whole_text)

    #print(repr(whole_text))
    #print(whole_text)

    
    for m in matches:
        options_dict = {}
        handleRow(m)
        

    
model_dict["options"] = list_of_options
model_list.append(model_dict)    
#print(model_list)

try:
    with open("output.json", "w") as outfile:
        #json.dump(model_list, outfile)
        outfile.write(whole_text)
        print("JSON dumped")
except Exception as e:
    print(f"Error: {e}")
