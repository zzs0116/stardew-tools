import json

DATA_LOCATIONS = "stardew_fish_by_season/Data_Locations.json"

keywords = [
    "Farm", "Henchman", "BearFam", "EDMushroomCave", "OldWoods", "DTZ"
]

with open(DATA_LOCATIONS, 'r') as f:
    data = json.load(f)
    
    print("Found keys in Data_Locations:")
    for key in data.keys():
        for kw in keywords:
            if kw in key:
                print(f"Key: '{key}'")
