import pandas as pd
from pandas import DataFrame


def get_start_keywords_row_index(df_col: DataFrame):
    """ get the first start_keyword position counted by index in df_col """
    first_start_keyword_idx = df_col[df_col == "Start: Keywords"].index[0]
    return first_start_keyword_idx


def extract_column(start_key_pos: int, df_col: DataFrame, classname: str):
    """ output list of instances names, keywords, mapping of instances - keywords """
    set_instances = set()
    set_keywords = set()
    ingredient_instance_keyword = {}
    for col_num, item in df_col.iloc[: start_key_pos].iteritems():
        if item == "":
            break
        item = item.lower()
        set_instances.add(item)
    recording_key = False
    instance_prefix = "instance: "
    current_instance = None
    for col_num, item in df_col.iloc[start_key_pos:].iteritems():
        if item == "":
            continue
        if item == "Start: Keywords":
            recording_key = True
            continue
        if item == "End: Keywords":
            current_instance = None
            recording_key = False
            continue
        item = item.lower()
        if recording_key:
            if instance_prefix in item:
                instance_name = item.split(instance_prefix)[-1]
                set_instances.add(instance_name)
                current_instance = classname + ":" + instance_name
                ingredient_instance_keyword[current_instance] = []
                continue
            if current_instance is not None:
                set_keywords.add(item)
                ingredient_instance_keyword[current_instance].append(item)
            else:
                print(f"SEVERE PROBLEM: KEYWORD {item} is not belonging to any Instance. Do re-check Sheet file please.")
    return set_instances, set_keywords, ingredient_instance_keyword


def read_cls_inst(filename: str):
    df = pd.read_excel(filename, headers=None, sheet_name="Classes-Instances-Keywords")
    df = df.fillna(value="")
    orginal_classes_names = [classname for classname in df.columns]
    classes_names = [classname.lower() for classname in df.columns]

    mapping_classname_instance = {}

    """ I didnt understand what this stores"""
    all_keys = set(classes_names)
    all_ingredient_instance = {}

    start_key_pos = get_start_keywords_row_index(df[orginal_classes_names[0]])
    for classname in orginal_classes_names:
        set_instances, set_keywords, ingredient_instance_keyword = extract_column(start_key_pos, df[classname], classname.lower())
        mapping_classname_instance[classname.lower()] = set_instances
        """I didn't understand below three lines"""
        all_keys = all_keys.union(set_instances)
        all_keys = all_keys.union(set_keywords)
        all_ingredient_instance.update(ingredient_instance_keyword)
    return all_keys, all_ingredient_instance, orginal_classes_names, mapping_classname_instance


def read_text_content(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def is_instance_in(classname: str, instance_name: str, all_ingredient_instance: dict, is_in_text_file: dict):
    """ check if instance is in the text file by checking its name or its ingredients """
    if instance_name not in is_in_text_file.keys():
        return False
    if is_in_text_file[instance_name]:
        return True
    combined_key = classname + ":" + instance_name
    if combined_key not in all_ingredient_instance.keys():
        return False
    for keyword in all_ingredient_instance[combined_key]:
        if not is_in_text_file[keyword]:
            return False
    return True


def check_all(classname: str, all_ingredient_instance: dict, is_in_text_file: dict, mapping_classname_instance: dict):
    if is_in_text_file[classname]:
        return True, 'all'
    for instance in mapping_classname_instance[classname]:
        if is_instance_in(classname, instance, all_ingredient_instance, is_in_text_file):
            return True, instance.lower()
    return False, ''


def read_requirement_file(filepath: str):
    df = pd.read_excel(filepath, sheet_name="Security Requirements")
    df = df.fillna(value="")
    return df


def append_row(output_file, row):
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(row + "\n")


def main():
    keywords_file = 'D:\Dropbox\Security_Requirements_Repository_Makale\Sample Repository\Sample_Repository_V10_Simplified.xlsx'
    output_csv = 'Output.csv'
    text_file = 'D:\\Dropbox\\Security_Requirements_Repository_Makale\\Sample Repository\\2012-Svetinovic-AAAI.txt'
    print("I opened txt file")
    all_keys, all_ingredient_instance, orginal_classes_names, mapping_classname_instance = read_cls_inst(keywords_file)
    is_in_text_file = {}
    text_content = read_text_content(text_file).lower()
    for key in all_keys:
        is_in_text_file[key] = f" {key} " in text_content or f"/n{key}" or f"/n{key}" or f"/n{key}/n" or f" {key}" in text_content or f"{key} " in text_content
    is_in_text_file["all"] = False
    df_requirements = read_requirement_file(keywords_file)

    with open(output_csv, "w", encoding="utf-8") as f:
        f.write("Classname,Instancename,RequirementText\n")

    for idx, row in df_requirements.iterrows():
        for classname in orginal_classes_names:
            cell_val = row[classname].lower()
            if cell_val == "":
                continue
            if cell_val == "all":
                exist, matching_instance = check_all(classname.lower(), all_ingredient_instance, is_in_text_file, mapping_classname_instance)
                if exist:
                    append_row(output_csv, f"{classname},{matching_instance},{row['Security Requirements']}")
            else:
                required_instances = cell_val.split(",")
                for required_instance in required_instances:
                    if is_instance_in(classname.lower(), required_instance.strip(), all_ingredient_instance, is_in_text_file):
                        append_row(output_csv, f"{classname},{required_instance},{row['Security Requirements']}")

    print(text_content)


if __name__ == "__main__":
    main()
