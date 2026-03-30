import json
import os

DATA_OBJECTS_PATH = "stardew_recipes_counter/src/Data_Objects.json"

def main():
    if not os.path.exists(DATA_OBJECTS_PATH):
        print(f"Error: {DATA_OBJECTS_PATH} not found.")
        return

    try:
        with open(DATA_OBJECTS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    textures = set()
    
    for item_id, item in data.items():
        # Check if it's a fish
        if item.get("Type") == "Fish":
            texture = item.get("Texture")
            if texture:
                # Normalize slashes if needed, or keep as is. 
                # The export_commands.txt had mixed slashes, so the tool likely handles both.
                # However, Data_Objects.json usually has backslashes for Mods.
                # We'll just collect them as is.
                textures.add(texture)

    print(f"Found {len(textures)} unique fish texture paths.")
    
    with open("fish_export_commands.txt", "w", encoding="utf-8") as f:
        for texture in sorted(textures):
            # The format is: patch export "PATH" image
            # We need to handle potential quotes in path if any (unlikely)
            command = f'patch export "{texture}" image'
            print(command)
            f.write(command + "\n")

if __name__ == "__main__":
    main()
