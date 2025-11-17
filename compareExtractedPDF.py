import json
import easygui
from deepdiff import DeepDiff
import pandas
import re

pandas.set_option('display.max_rows', None)


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def compare_dicts_deepdiff(dict1, dict2):
    diff = DeepDiff(dict1, dict2)
    df = pandas.DataFrame(diff.get("values_changed", []))
    df = df.T
    df['new_num_value'] = pandas.to_numeric(df['new_value'], errors='coerce')
    df['old_num_value'] = pandas.to_numeric(df['old_value'], errors='coerce')
    df['difference'] = df.apply(lambda row: row['new_num_value'] - row['old_num_value'] if isinstance(row['new_num_value'], (int, float)) else "No Math", axis=1)
    df.drop(['new_num_value', 'old_num_value'], axis=1, inplace=True)
    print(df)


def compare_uneven_dicts(dict1, dict2, old_file_name, new_file_name):
    #model or option is removed if it is present in dict1 but not in dict2
    removed_models = []
    removed_options = []
    #option is changed if the value is present in both dicts but different between dict1 and dict2
    changed_options = []
    #model or option is added if it is present in dict2 but not in dict1
    new_models = []
    new_options = []

    if len(dict1) > len(dict2):
        print(f"{old_file_name} has more keys than {new_file_name}")
    elif len(dict1) < len(dict2):
        print(f"{new_file_name} has more keys than {old_file_name}")

    #checking old against new
    for models in dict1:
        model_found_flag = False

        for each_model in dict2:
            if models["model"] == each_model["model"]:
                model_found_flag = True
                
                for options in models["options"]:
                    option_found_flag = False

                    for each_option in each_model["options"]:

                        if options["option_code"] == each_option["option_code"]:
                            option_found_flag = True

                            if options["invoice"] != each_option["invoice"] or options["msrp"] != each_option["msrp"]:
                                changed_option = {"model": models["model"],
                                                "year": models["year"],
                                                "option_code": options["option_code"],
                                                "old_invoice": options["invoice"],
                                                "new_invoice": each_option["invoice"],
                                                "old_msrp": options["msrp"],
                                                "new_msrp": each_option["msrp"]}
                                changed_options.append(changed_option)
                            break
                    if not option_found_flag:
                        removed_option = {"model": models["model"],
                                        "year": models["year"],
                                        "option_code": options["option_code"],
                                        "invoice": options["invoice"],
                                        "msrp": options["msrp"]}
                        removed_options.append(removed_option)
                break
        if not model_found_flag:
            removed_model = {"model": models["model"],
                            "year": models["year"]}
            removed_models.append(removed_model)
    #end old against new check

    #checking new against old
    for models in dict2:
        model_found_flag = False

        for each_model in dict1:
            if models["model"] == each_model["model"]:
                model_found_flag = True
                
                for options in models["options"]:
                    option_found_flag = False

                    for each_option in each_model["options"]:
                        if options["option_code"] == each_option["option_code"]:
                            #not comparing invoice or msrp because they were already compared
                            option_found_flag = True
                            break
                    if not option_found_flag:
                        new_option = {"model": models["model"],
                                    "year": models["year"],
                                    "option_code": options["option_code"],
                                    "invoice": options["invoice"],
                                    "msrp": options["msrp"]}
                        new_options.append(new_option)
                break
        if not model_found_flag:
            new_model = {"model": models["model"],
                        "year": models["year"]}
            new_models.append(new_model)
    #end new against old check
    print(f"New models: {json.dumps(new_models, indent=2)}")
    print(f"Removed models: {json.dumps(removed_models, indent=2)}")
    print(f"New options: {json.dumps(new_options, indent=2)}")
    print(f"Removed options: {json.dumps(removed_options, indent=2)}")
    print(f"Changed options: {json.dumps(changed_options, indent=2)}")



#start main
file_path_old = easygui.fileopenbox(title="Select the first JSON file", filetypes=["*.json"])
file_path_new = easygui.fileopenbox(title="Select the second JSON file", filetypes=["*.json"])

if file_path_old and file_path_new:
    old_file_name = re.split(r'[\\/]', file_path_old)[-1]
    new_file_name = re.split(r'[\\/]', file_path_new)[-1]
    old_dict = load_json(file_path_old)
    new_dict = load_json(file_path_new)

#compare_dicts_deepdiff(old_dict, new_dict)
compare_uneven_dicts(old_dict, new_dict, old_file_name, new_file_name)


#input("Press Enter to continue...")
#end main

