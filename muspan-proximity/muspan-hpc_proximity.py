import muspan as ms
import numpy as np
import pandas as pd
import os
import argparse

def load_domains(input_directory):
    saved_domains = [f for f in os.listdir(input_directory) if not f.lower().startswith("._")]

    domains = []

    for s_domain in saved_domains:
        domain = ms.io.load_domain(os.path.join(input_directory,s_domain))
        domains.append(domain)

    return domains


def create_proximity_network(domains, max_edge_distance):
    for domain in domains:
        qCells = ms.query.query(domain, ('Collection',), 'is', 'Cell centres') # Query the domain to get cell centres
        ms.networks.generate_network(
            domain,
            network_name='proximity_boundary',
            objects_as_nodes=qCells,
            network_type='Proximity',
            min_edge_distance=0,
            max_edge_distance=max_edge_distance
        )
    return domains

def get_classes_to_investigate(path):
    df = pd.read_csv(path)
    column_name = df.columns.to_list()[0]
    classes = df[column_name].to_list()

    return classes, column_name

def get_contacts_clusters_of_interest(domains, clusters_of_interest, label_of_interest, output_directory):
    array_save = os.path.join(output_directory, "domain_arrays")
    if not os.path.exists(array_save):
        os.mkdir(array_save)

    list_of_arrays = []
    for domain in domains:
        labels, object_indices = ms.query.get_labels(domain, label_of_interest)
        this_order_degree = {}
        total_contacts = np.zeros((len(clusters_of_interest), len(clusters_of_interest)))
        for idex, id in enumerate(clusters_of_interest):
        # Query the domain for the current cluster
            this_id_query = ms.query.query(domain, ('label', label_of_interest), 'is', id)
            
            try:
        # Generate k-hop neighbourhoods for the current cluster
                khop_neighbourhoods_prox = ms.networks.khop_neighbourhood(domain, network_name='proximity_boundary', source_objects=this_id_query, k=1)

        # Initialize a list to store the degrees
                these_degrees = []

        # Calculate the degree for each k-hop neighbourhood
                for k in khop_neighbourhoods_prox:
                    these_degrees.append(len(khop_neighbourhoods_prox[k]))

        # Store the degrees in the dictionary
                this_order_degree[id] = these_degrees

            # Initialize an array to store the compositions
                these_compositions = np.zeros((len(khop_neighbourhoods_prox), len(clusters_of_interest)))
            # Calculate the composition for each k-hop neighbourhood
                for kid, k in enumerate(khop_neighbourhoods_prox):
                    this_neighbourhood = khop_neighbourhoods_prox[k]
                    for n in this_neighbourhood:
                        this_label_index = np.where(object_indices == n)[0][0]
                        if labels[this_label_index] in clusters_of_interest:
                            these_compositions[kid, clusters_of_interest.index(labels[this_label_index])] += 1
            # Calculate the average composition for the current cluster
                total_contacts[idex, :] = np.sum(these_compositions, axis=0)

            except:
                total_contacts[idex, :] = np.zeros((1, len(clusters_of_interest)))    
        #save the total_contacts array for each domain
        np.save(os.path.join(array_save, domain.name + "_array"), total_contacts)

        list_of_arrays.append(total_contacts)

    return list_of_arrays

def save_arrays(list_of_arrays, output_directory):
    array_save = os.path.join(output_directory, "combined_arrays")
    if not os.path.exists(array_save):
        os.mkdir(array_save)

    total_array = np.sum(list_of_arrays, axis=0)
    array_size = total_array.shape[0]
    total_array_without_itself = total_array.copy()
    for i in range(array_size):
        total_array_without_itself[i,i] = 0

    norm_array_with_itself = np.zeros((array_size, array_size))
    norm_array_without_itself = np.zeros((array_size, array_size))

    for i in range(array_size):
        norm_array_with_itself[i,:] = total_array[i, :] / np.sum(total_array[i, :])
        norm_array_without_itself[i,:] = total_array_without_itself[i, :] / np.sum(total_array_without_itself[i, :])

    np.save(os.path.join(array_save, "total_array"), total_array)
    np.save(os.path.join(array_save, "total_array_without_itself"), total_array_without_itself)
    np.save(os.path.join(array_save, "norm_array_with_itself"), norm_array_with_itself)
    np.save(os.path.join(array_save, "norm_array_without_itself"), norm_array_without_itself)

def main(input_directory, output_directory, path_classes_to_investigate, max_edge_distance):
    domains = load_domains(input_directory)

    domains = create_proximity_network(domains, int(max_edge_distance))

    clusters_of_interest, label_of_interest = get_classes_to_investigate(path_classes_to_investigate)

    list_of_arrays = get_contacts_clusters_of_interest(domains, clusters_of_interest, label_of_interest, output_directory)

    save_arrays(list_of_arrays, output_directory)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Muspan neighbourhood analysis")
    parser.add_argument("--inputs", required=True, help="Directory containing domains")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--path_classes_to_investigate", required=True, help="Path to csv-file with classes to investigate")
    parser.add_argument("--max_edge_distance", required=True, help="Max edge distance for proximity network")

    args = parser.parse_args()
    main(args.inputs, args.output, args.path_classes_to_investigate, args.max_edge_distance)