import json

DATA_LOCATIONS = "stardew_fish_by_season/Data_Locations.json"

def main():
    with open(DATA_LOCATIONS, 'r') as f:
        data = json.load(f)
    
    rsv_locations = set()
    
    for loc_key, loc_data in data.items():
        if loc_key == "Default": continue
        fish_list = loc_data.get("Fish")
        if not fish_list: continue
        
        for f in fish_list:
            item_id = f.get("ItemId") or f.get("Id")
            if item_id and "Rafseazz.RSVCP" in item_id:
                rsv_locations.add(loc_key)
                
    print("Locations containing Ridgeside fish:")
    for loc in sorted(rsv_locations):
        print(f"- {loc}")

if __name__ == "__main__":
    main()
