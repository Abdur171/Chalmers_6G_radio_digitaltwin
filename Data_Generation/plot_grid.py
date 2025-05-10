import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Replace 'grid_points.csv' with the path to your CSV file.
    file_path = "Undergraduate_Thesis_Project\Data_Generation\Grid_points_1x1_Entrance.csv"
    
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
