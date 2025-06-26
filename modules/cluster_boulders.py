def cluster_boulders():
    """
    Clusters detected boulders based on their diameters and visualizes the results.
    """
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans
    import os

    # File paths
    input_file = "static/boulder_data.csv"
    output_file = "static/boulder_data_clustered.csv"
    plot_file = "static/clustered_boulders_plot.jpg"

    # Step 1: Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"[ERROR] {input_file} not found. Ensure boulder detection was run first.")

    # Step 2: Load the data
    df = pd.read_csv(input_file)

    # Step 3: Validate required columns
    required_columns = {'Diameter (m)', 'X', 'Y'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"[ERROR] Input CSV must contain these columns: {required_columns}")

    # Step 4: Feature extraction for clustering
    X = df[['Diameter (m)']]

    # Step 5: Apply KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=0, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(X)

    # Step 6: Assign size labels based on cluster means
    sizes = df.groupby("Cluster")["Diameter (m)"].mean().sort_values()
    cluster_map = {i: label for i, label in zip(sizes.index, ['Small', 'Medium', 'Large'])}
    df['SizeLabel'] = df['Cluster'].map(cluster_map)

    # Step 7: Save clustered data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"[✅] Clustered data saved to: {output_file}")

    # Step 8: Plot clustered boulders
    plt.figure(figsize=(10, 8))
    cluster_colors = {'Small': 'green', 'Medium': 'orange', 'Large': 'red'}

    for label in ['Small', 'Medium', 'Large']:
        sub = df[df['SizeLabel'] == label]
        plt.scatter(
            sub['X'], sub['Y'], label=f"{label} Boulders",
            s=50, c=cluster_colors[label], edgecolor='black', alpha=0.7
        )

    # Step 9: Adjust axis for realistic plotting
    plt.gca().invert_yaxis()

    # Step 10: Add titles, labels, and legend
    plt.title("Boulder Clusters by Size", fontsize=16)
    plt.xlabel("X Coordinate", fontsize=12)
    plt.ylabel("Y Coordinate", fontsize=12)
    plt.legend(title="Boulder Size", fontsize=10, loc='upper right')

    # Step 11: Save the plot
    os.makedirs(os.path.dirname(plot_file), exist_ok=True)
    plt.savefig(plot_file, dpi=300)
    plt.close()
    print(f"[✅] Clustered plot saved to: {plot_file}")
