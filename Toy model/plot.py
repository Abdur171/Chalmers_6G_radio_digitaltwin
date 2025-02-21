import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Replace 'grid_points.csv' with the path to your CSV file.
    file_path = "grid_points_toy.csv"
    
    # Read the CSV file into a DataFrame.
    data = pd.read_csv(file_path)
    
    # Assuming the CSV has columns 'x' and 'y'. Adjust if necessary.
    x = data['x']
    y = data['y']
    
    # Create a scatter plot for the grid points.
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color='blue', marker='o', markersize = 1)
    plt.title("Grid Points")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
