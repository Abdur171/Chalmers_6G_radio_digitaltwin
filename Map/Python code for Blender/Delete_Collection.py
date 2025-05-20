import bpy

# Get the active collection
active_collection = bpy.context.collection

# Ensure the collection is not None and is not the Master Collection
if active_collection and active_collection.name != "Collection":
    bpy.data.collections.remove(active_collection)
    print(f"Deleted collection: {active_collection.name}")
else:
    print("Cannot delete the Master Collection or an invalid collection.")