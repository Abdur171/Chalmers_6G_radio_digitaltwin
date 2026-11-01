import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "grid_points_1x1_full.csv")
    
    # Read the CSV file into a DataFrame.
    data = pd.read_csv(file_path)
    
    # Assuming the CSV has columns 'x' and 'y'. Adjust if necessary.
    X = data['X']
    Y = data['Y']
    
    # Create a scatter plot for the grid points.
    plt.figure(figsize=(20, 20))
    plt.scatter(X, Y, color='black', marker='o', s=0.1)
    plt.title("Grid Points")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
