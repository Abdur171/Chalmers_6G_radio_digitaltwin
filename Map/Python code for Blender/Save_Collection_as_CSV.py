import bpy
import csv
import os

# Get the active collection (the collection that is selected in the Outliner)
active_collection = bpy.context.view_layer.active_layer_collection.collection

# Ensure the active collection exists
if active_collection is None:
    print("No active collection found!")
else:
    # Specify the file path to save the CSV (portable resolution)
    if bpy.data.filepath:
        base_dir = os.path.dirname(os.path.abspath(bpy.data.filepath))
    elif "__file__" in globals():
        base_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        base_dir = os.getcwd()
    filepath = os.path.join(base_dir, "Grid_points_1x1_Entrance.csv")

    # Open the CSV file in write mode
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Object Name", "X", "Y", "Z"])  # Column headers
        
        # Iterate through each object in the active collection
        for obj in active_collection.objects:
            # Get the object's location
            x, y, z = obj.location
            # Write the object name and its coordinates
            writer.writerow([obj.name, x, y, z])

    print(f"Grid points saved to {filepath}")
