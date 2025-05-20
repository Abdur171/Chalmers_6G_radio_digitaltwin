import bpy
import mathutils

height_above_road_variable = 1.3
road_width_variable = 1.4

def create_grid_on_road(curve_obj, step_distance=0.1, road_width=road_width_variable, placed_points=None, height_above_road=height_above_road_variable):
    """Creates a centered, thinner grid on a road following a curve, raised above the road."""
    
    # Get the curve data
    curve_data = curve_obj.data
    if not curve_data.splines:
        print("No splines in the curve object!")
        return
    
    # Create a new collection for the grid points
    collection_name = f"Road Grid - {curve_obj.name}"
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
    else:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    # Create a base mesh object (sphere) to represent each grid point
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05)  
    base_mesh = bpy.context.object
    base_mesh.name = "GridPointMesh"
    bpy.context.scene.collection.objects.unlink(base_mesh)  # Unlink from the main scene
    collection.objects.link(base_mesh)  # Link to our collection
    
    num_across = int(road_width / step_distance)
    half_width = (num_across * step_distance) / 2.0

    world_matrix = curve_obj.matrix_world  # Get world transformation

    # For each road segment, calculate grid points
    for spline in curve_data.splines:
        if spline.type == 'BEZIER':
            points = spline.bezier_points
        elif spline.type == 'POLY':
            points = spline.points
        else:
            continue

        for i in range(len(points) - 1):
            start_point_local = mathutils.Vector(points[i].co.xyz)
            end_point_local = mathutils.Vector(points[i + 1].co.xyz)
            
            # Transform points to world space
            start_point = world_matrix @ start_point_local
            end_point = world_matrix @ end_point_local

            segment_length = (end_point - start_point).length
            if segment_length == 0:
                continue

            num_steps = max(1, int(segment_length / step_distance))

            for step in range(num_steps + 1):
                t = step / num_steps
                interp_point = start_point.lerp(end_point, t)

                tangent = (end_point - start_point).normalized()
                perp = mathutils.Vector((-tangent.y, tangent.x, 0)).normalized()

                for j in range(num_across + 1):
                    offset = (j * step_distance) - half_width
                    offset_point = interp_point + perp * offset

                    offset_point.z += height_above_road  # <<< Raise by given height

                    # Use a grid-based approach to avoid rounding errors
                    grid_x = int(offset_point.x // step_distance) * step_distance
                    grid_y = int(offset_point.y // step_distance) * step_distance
                    grid_position = (grid_x, grid_y)

                    if grid_position not in placed_points:
                        placed_points.add(grid_position)
                        create_mesh_instance(offset_point, base_mesh, collection)

def create_mesh_instance(location, base_mesh, collection):
    """Creates an instance of the base mesh at a given location."""
    instance = base_mesh.copy()
    instance.location = location
    collection.objects.link(instance)

# Collect all road objects
road_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'CURVE']

# Set to track the final grid points for all roads (unique 2D points)
final_placed_points = set()

# Create grid on each road, checking overlap with previously placed points
for obj in road_objects:
    create_grid_on_road(obj, step_distance=1.0, road_width=road_width_variable, placed_points=final_placed_points, height_above_road=height_above_road_variable)
