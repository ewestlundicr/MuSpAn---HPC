import os
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

import muspan as ms
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import os 
import json
from sklearn.cluster import KMeans
import argparse

def create_domains(csv_directory):
    # retrieve list of csv file only
    csvs = sorted([f for f in os.listdir(csv_directory) if f.lower().endswith(".csv")])
    
    domains = []
    
    required = ["Cell X Position", "Cell Y Position", "Phenotype", "Parent"]

    for _, csv in enumerate(csvs):
        csv_path = os.path.join(csv_directory,csv)

        df = pd.read_csv(csv_path)
        # add some control over csv content
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"{csv} missing columns: {missing}")
        points = np.asarray([df["Cell X Position"], df["Cell Y Position"]])
        points[1,:] = -points[1,:]
        domain = ms.domain(str(csv))
        domain.add_points(points.T, "Cell centres")
        domain.add_labels("Phenotype", df["Phenotype"])
        domain.add_labels("ROI", df["Parent"])
        domains.append(domain)
       
    return domains

def generate_neighbourhoods(domains, label_name, network_type, n_nearest_neighbours,
                                k_hops, phenotype_list, 
                                neighbourhood_label_name, n_clusters, save_path):
    
    neighbourhood_enrichment_matrix, consistent_global_labels, unique_cluster_labels, observation_matrix, cluster_labels = ms.networks.cluster_neighbourhoods(
        domains,  # The domain dataset
        label_name=label_name,  # The label to use for clustering
        network_kwargs=dict(network_type=network_type, max_edge_distance=np.inf, min_edge_distance=0, number_of_nearest_neighbours=n_nearest_neighbours),  # The network parameters
        k_hops=k_hops,  # The number of hops to consider for the neighbourhood
        force_labels_to_include=phenotype_list,
        neighbourhood_label_name=neighbourhood_label_name,  # Name for the neighbourhood label
        cluster_method='minibatchkmeans',  # Clustering method
        cluster_parameters={'n_clusters': n_clusters},  # Parameters for the clustering method
        neighbourhood_enrichment_as='zscore', # Neighbourhood enrichment as log-fold
        return_observation_matrix_and_labels=True #return an observation matrix for elbow plot
        ) 
    
    var_dict = {"neighbourhood_enrichment_matrix":neighbourhood_enrichment_matrix.tolist(),
            "consistent_global_labels": consistent_global_labels,
            "unique_cluster_labels":unique_cluster_labels.tolist(),
            "observation_matrix": observation_matrix.tolist()}

    # safeguard in case save_path doesnt exist
    os.makedirs(save_path, exist_ok=True)
    matrices_path = os.path.join(save_path, f"{neighbourhood_label_name}.json") # adding an extension to the filename

    with open(matrices_path, "w+") as f:
        json.dump(var_dict, f)

    return neighbourhood_enrichment_matrix, consistent_global_labels, unique_cluster_labels, observation_matrix

def generate_elbow_plot(observation_matrix, n_neighbourhoods, save_path, image_name):
    obs_mat = np.array(observation_matrix, dtype=float)

    wcss= [] #within cluster sum of squares

    K_range = range(1,n_neighbourhoods) #candidate n_clusters

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state = 42)
        kmeans.fit(obs_mat)
        wcss.append(kmeans.inertia_) #inertia_ = sum of squared distances to cluster centres

    plt.figure(figsize=(6,4))
    plt.plot(K_range, wcss, marker='o')
    plt.xlabel('Number of clusters k')
    plt.ylabel('WCSS (inertia)')
    plt.title('Optimal N for neighbourhood clusters (Elbow)')
    plt.savefig(os.path.join(save_path, image_name), dpi = 300, bbox_inches = 'tight')
    plt.close()#closing figure to avoid memory leaks

def generate_neighbourhood_heatmap(neighbourhood_enrichment_matrix, unique_cluster_labels, consistent_global_labels, save_path, image_name):
    # Create a DataFrame from the neighbourhood enrichment matrix
    df_ME_id = pd.DataFrame(data=neighbourhood_enrichment_matrix, index=unique_cluster_labels, columns=consistent_global_labels)
    df_ME_id.index.name = 'Neighbourhood ID'
    df_ME_id.columns.name = 'Phenotype ID'

    # Visualize the neighbourhood enrichment matrix using a clustermap
    g = sns.clustermap(
        df_ME_id,
        xticklabels=consistent_global_labels,
        yticklabels=unique_cluster_labels,
        figsize=(10.5, 10.5),
        cmap='RdBu_r',
        dendrogram_ratio=(.05, .3),
        col_cluster=True,
        row_cluster=False,
        square=True,
        linewidths=0.5,
        linecolor='black',
        cbar_kws=dict(use_gridspec=False, location="top", label='Neighbourhood enrichment KNN (z-score)', ticks=[-2, 0, 2]),
        cbar_pos=(0.12, 0.81, 0.72, 0.05), #left, bottom, width, height
        vmin=-2,
        vmax=2,
        tree_kws={'linewidths': 0, 'color': 'white'}
    )
    g.savefig(os.path.join(save_path, image_name))
    plt.close(g.figure) #closing figure to avoid memory leaks

def save_domains(domains, save_path):
    domain_save = os.path.join(save_path, "domains")
    if not os.path.exists(domain_save):
        os.mkdir(domain_save)

    csv_save = os.path.join(save_path, "csvs")
    if not os.path.exists(csv_save):
        os.mkdir(csv_save)

    for domain in domains:
        ms.io.save_domain(domain, path_to_save=domain_save, name_of_file= str(domain.name))
        ms.io.domain_to_csv(domain, path_to_save=csv_save, name_of_file= str(domain.name))

def main(csv_directory, save_path):

    domains = create_domains(csv_directory)

    phenotype_list = ['CD8', 'CD8_Other', 'FAP', 'FAP_PDGFRa', 'FAP_PDGFRa_aSMA', 'FAP_PDPN',
                   'FAP_PDPN_PDGFRa', 'FAP_PDPN_PDGFRa_aSMA', 'FAP_PDPN_aSMA', 'FAP_PDPN_panCK',
                    'FAP_aSMA', 'FAP_panCK', 'Other', 'PDGFRa', 'PDGFRa_aSMA', 'PDPN', 'PDPN_CD8',
                    'PDPN_CD8_Other', 'PDPN_PDGFRa', 'PDPN_PDGFRa_aSMA', 'PDPN_aSMA',
                    'PDPN_panCK', 'PDPN_panCK_Other', 'aSMA', 'panCK', 'panCK_Other', 'unclassified detections']

    neighbourhood_label_name = 'Neighbourhood_ID_KNN_8' # I would avoid spaces in filenames
    neighbourhood_enrichment_matrix, consistent_global_labels, unique_cluster_labels, observation_matrix = generate_neighbourhoods(domains, 'Phenotype', 'KNN', 10, 1, phenotype_list, neighbourhood_label_name, 8, save_path)

    generate_elbow_plot(observation_matrix, 15, save_path, "elbow_plot.jpg")

    generate_neighbourhood_heatmap(neighbourhood_enrichment_matrix, unique_cluster_labels, consistent_global_labels, save_path, 'heatmap.jpg')

    save_domains(domains, save_path)

# replace it with command line options
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Muspan neighbourhood analysis")
    parser.add_argument("--inputs", required=True, help="Directory containing CSV files")
    parser.add_argument("--output", required=True, help="Output directory")

    args = parser.parse_args()
    main(args.inputs, args.output)