def generate_stats():
    import pandas as pd
    import numpy as np

    df = pd.read_csv("boulder_data.csv")

    # Basic metrics
    total = len(df)
    min_d = df["Diameter (m)"].min()
    max_d = df["Diameter (m)"].max()
    avg_d = df["Diameter (m)"].mean()
    std_d = df["Diameter (m)"].std()
    median_d = df["Diameter (m)"].median()

    # Estimated area covered by boulders (assuming circular shape)
    area = np.pi * (df["Diameter (m)"] / 2) ** 2
    total_area = area.sum()

    # Save to text file in readable format
    output_path = "static/stats_summary.txt"
    with open(output_path, "w") as f:
        f.write("Boulder Detection Statistics Summary\n")
        f.write("======================================\n\n")
        f.write(f" Total Boulders Detected : {total}\n")
        f.write(f" Minimum Diameter        : {min_d:.2f} m\n")
        f.write(f" Maximum Diameter        : {max_d:.2f} m\n")
        f.write(f" Average Diameter        : {avg_d:.2f} m\n")
        f.write(f" Median Diameter         : {median_d:.2f} m\n")
        f.write(f" Std. Deviation          : {std_d:.2f} m\n")
        f.write(f" Total Area Covered      : {total_area:.2f} sq. meters\n")

    print(f"[✔] Statistics saved to {output_path}")
