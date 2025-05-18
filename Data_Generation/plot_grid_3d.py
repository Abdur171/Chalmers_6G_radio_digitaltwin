import pandas as pd
import plotly.express as px

def main():
    file_path = "Undergraduate_Thesis_Project/Data_Generation/grid_points_1x1_full.csv"
    data = pd.read_csv(file_path)

    fig = px.scatter_3d(
        data, x='X', y='Y', z='Z',
        color='Z', color_continuous_scale='Viridis',
        opacity=0.6, height=800, width=1000
    )

    fig.update_traces(marker=dict(size=2))  # Bigger points
    fig.update_layout(
        title='3D Grid Points on Chalmers Campus',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'  # Equal aspect ratio
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )

    fig.show()
    # Optional: Save as static image
    # fig.write_image("3d_grid_plot.png", scale=5)  # Needs kaleido installed

if __name__ == "__main__":
    main()
