"""
Utility helper functions
"""

import re
import json


"""
Removes special characters, normalises all whitespace characters with a uniform single whitespace,
converts all letters to lower case and strips string of any 2+ whitespace sequences.
Hyphens are replaced with whitespace so that hyphenated uniformly match with non-hypthened varients 
(e.g. part-time & part time)

Parameters:
    string (str): string to be normalised
Returns:
     str: string with normalisation applied
 """
def normalise_str(string):
    return re.sub(r'\s+', " ", # normalises all remaining whitespace characters with a single whitespace
                  re.sub(r'[^\w\s]', "", # Removes all special characters (All except whitespace and alphanumerical)
                         re.sub(r'[\s][\s]+', " ", # Replace two or more whitespace with single whitespace
                                re.sub(r'[\-\–—‒‑]', " ", string.lower().strip())))) # Replace all dashes with whitespace


"""
Converts dict to json format and saves file onto file system
Parameters:
    data (dict): dictionary to be exported
    filename (str): name of the output file
Returns: None
"""
def export_json(data, filename):
    with open(f"{filename}.json", "w") as json_file:
        json.dump(data, json_file, default=lambda o: o.encode(), indent=4) # class objects require an encode method to convert into dict
        print(f"Data saved to {filename}.json")
