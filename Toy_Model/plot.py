import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Replace 'grid_points.csv' with the path to your CSV file.
    file_path = "Toy model/grid_points_toy.csv"
    
    # Read the CSV file into a DataFrame.
    data = pd.read_csv(file_path)
    
    # Assuming the CSV has columns 'x' and 'y'. Adjust if necessary.
    X = data['X']
    Y = data['Y']

    dx=np.diff(X)
    dy=np.diff(Y)
    # -------------------------------# Option 1: Histogram (Frequency Distribution) of the differences# ------------------------------- 
    plt.figure(figsize=(12, 5)) 
    plt.subplot(1, 2, 1) 
    plt.hist(dx, bins=30, color='blue', edgecolor='black') 
    plt.title("Histogram of x[n] - x[n-1]") 
    plt.xlabel("Difference value") 
    plt.ylabel("Frequency") 
    plt.subplot(1, 2, 2) 
    plt.hist(dy, bins=30, color='green', edgecolor='black') 
    plt.title("Histogram of y[n] - y[n-1]") 
    plt.xlabel("Difference value") 
    plt.ylabel("Frequency") 
    plt.tight_layout() 
    plt.show()
    
    # Create a scatter plot for the grid points.
    plt.figure(figsize=(20, 20))
    plt.scatter(X, Y, color='blue', marker='o', s=0.01)
    plt.title("Grid Points")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
