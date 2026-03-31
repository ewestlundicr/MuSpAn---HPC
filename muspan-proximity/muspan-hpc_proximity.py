import muspan as ms
import numpy as np
import pandas as pd
import os
import argparse
from collections import defaultdict

# adding sort on the retrieval of domains fir a better reporducibility, while ensuring domains are processed in a specific order 
def get_domain_list(input_directory):
    return sorted([f for f in os.listdir(input_directory) if not f.lower().startswith("._")])


def load_domain(domain_path):
    return ms.io.load_domain(domain_path)


def create_proximity_network(domain, max_edge_distance):
    qCells = ms.query.query(domain, ('Collection',), 'is', 'Cell centres') # Query the domain to get cell centres
    ms.networks.generate_network(
        domain,
        network_name='proximity_boundary',
        objects_as_nodes=qCells,
        network_type='Proximity',
        min_edge_distance=0,
        max_edge_distance=max_edge_distance
    )

    return domain

def save_domain(domain, output_directory):
    domain_save = os.path.join(output_directory, "domains")
    csv_save = os.path.join(output_directory, "csvs")
    # os.makedirs wont recreate a repo if already existant, so no need for the if conditions
    os.makedirs(domain_save, exist_ok=True)
    os.makedirs(csv_save, exist_ok=True)

    ms.io.save_domain(domain, path_to_save=domain_save, name_of_file=str(domain.name))
    ms.io.domain_to_csv(domain, path_to_save=csv_save, name_of_file=str(domain.name))

def get_classes_to_investigate(path):
    df = pd.read_csv(path)
    column_name = df.columns.to_list()[0]
    classes = df[column_name].to_list()

    return classes, column_name

# the main bottleneck of the code was in this function with very expensive and repetitive lookup logic.
def get_contacts_clusters_of_interest(domain, clusters_of_interest, label_of_interest, output_directory):
    array_save = os.path.join(output_directory, "domain_arrays")
    os.makedirs(array_save, exist_ok=True)

    labels, object_indices = ms.query.get_labels(domain, label_of_interest)

    # Using dicts fast lookup tables - done once for all instead of searching the array per neighbor per neigbhborhood
    cluster_to_pos = {cluster: i for i, cluster in enumerate(clusters_of_interest)}
    object_to_label = {obj_idx: label for obj_idx, label in zip(object_indices, labels)}

    # Group source objects by cluster label
    objects_by_cluster = defaultdict(list)
    for obj_idx, label in zip(object_indices, labels):
        if label in cluster_to_pos:
            objects_by_cluster[label].append(obj_idx)

    total_contacts = np.zeros((len(clusters_of_interest), len(clusters_of_interest)), dtype=np.int64)

    for cluster, row_idx in cluster_to_pos.items():
        source_objects = objects_by_cluster.get(cluster, [])
        if not source_objects:
            continue

        try:
            khop_neighbourhoods = ms.networks.khop_neighbourhood(
                domain,
                network_name='proximity_boundary',
                source_objects=source_objects,
                k=1
            )

            row_counts = np.zeros(len(clusters_of_interest), dtype=np.int64)

            for _, neighbours in khop_neighbourhoods.items():
                for n in neighbours:
                    label = object_to_label.get(n)
                    if label is None:
                        continue

                    col_idx = cluster_to_pos.get(label)
                    if col_idx is not None:
                        row_counts[col_idx] += 1

            total_contacts[row_idx, :] = row_counts

        except Exception as e:
            print(f"[WARN] Failed on domain={domain.name}, cluster={cluster}: {e}")

    np.save(os.path.join(array_save, f"{domain.name}_array.npy"), total_contacts)
    return total_contacts

# this is the merging step that reads from already create .npy files and produces a combined_array
def save_total_arrays(output_directory):
    array_input = os.path.join(output_directory, "domain_arrays")
    array_save = os.path.join(output_directory, "combined_arrays")
    os.makedirs(array_save, exist_ok=True)

    list_of_arrays = []
    for filename in os.listdir(array_input):
        if filename.endswith(".npy"): # read only .npy files
            cur_array = np.load(os.path.join(array_input, filename))
            list_of_arrays.append(cur_array)

    if not list_of_arrays:
        raise ValueError("No per-domain arrays found in domain_arrays.")

    total_array = np.sum(list_of_arrays, axis=0)

    total_array_without_itself = total_array.copy()
    np.fill_diagonal(total_array_without_itself, 0)

    row_sums_with = total_array.sum(axis=1, keepdims=True)
    row_sums_without = total_array_without_itself.sum(axis=1, keepdims=True)

    # using numpy native functions is much more optimal than doing "manual operations"
    norm_array_with_itself = np.divide(
        total_array,
        row_sums_with,
        out=np.zeros_like(total_array, dtype=float),
        where=row_sums_with != 0
    )

    norm_array_without_itself = np.divide(
        total_array_without_itself,
        row_sums_without,
        out=np.zeros_like(total_array_without_itself, dtype=float),
        where=row_sums_without != 0
    )

    np.save(os.path.join(array_save, "total_array.npy"), total_array)
    np.save(os.path.join(array_save, "total_array_without_itself.npy"), total_array_without_itself)
    np.save(os.path.join(array_save, "norm_array_with_itself.npy"), norm_array_with_itself)
    np.save(os.path.join(array_save, "norm_array_without_itself.npy"), norm_array_without_itself)

# adding a new function that runs all the above steps on a single domain
def process_one_domain(domain_path, output_directory, path_classes_to_investigate, max_edge_distance, save_updated_domain=False):
    clusters_of_interest, label_of_interest = get_classes_to_investigate(path_classes_to_investigate)

    domain = load_domain(domain_path)

    if "proximity_boundary" not in domain.networks:
        domain = create_proximity_network(domain, int(max_edge_distance))
        if save_updated_domain:
            save_domain(domain, output_directory)

    return get_contacts_clusters_of_interest(
        domain=domain,
        clusters_of_interest=clusters_of_interest,
        label_of_interest=label_of_interest,
        output_directory=output_directory
    )


def main(input_directory, output_directory, path_classes_to_investigate, max_edge_distance, create_total_arrays):
    domains_list = get_domain_list(input_directory)

    for domain_name in domains_list:
        domain_path = os.path.join(input_directory, domain_name)
        process_one_domain(
            domain_path=domain_path,
            output_directory=output_directory,
            path_classes_to_investigate=path_classes_to_investigate,
            max_edge_distance=int(max_edge_distance),
            save_updated_domain=False
        )

    if int(create_total_arrays) == 1:
        save_total_arrays(output_directory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Muspan neighbourhood analysis")
    parser.add_argument("--inputs", required=False, help="Directory containing domains")
    parser.add_argument("--output", required=True, help="Output directory, to be used for merging")
    parser.add_argument("--path_classes_to_investigate", required=False, help="Path to csv-file with classes to investigate")
    parser.add_argument("--max_edge_distance", required=False, help="Max edge distance for proximity network")
    parser.add_argument("--create_total_arrays", required=False, help="0 = False or 1 = True to create total array")
    parser.add_argument("--domain", required=False, help="Optional single domain path for array jobs")
    parser.add_argument("--merge_only", action="store_true", help="Only merge arrays")

    args = parser.parse_args()

    # MERGE ONLY MODE
    if args.merge_only:
        print("Running merge only...")
        save_total_arrays(args.output)
    # SINGLE DOMAIN MODE (array jobs)
    elif args.domain:
        process_one_domain(
            domain_path=args.domain,
            output_directory=args.output,
            path_classes_to_investigate=args.path_classes_to_investigate,
            max_edge_distance=int(args.max_edge_distance),
            save_updated_domain=False
        )
    # FULL SERIAL MODE
    else:
        main(
            args.inputs,
            args.output,
            args.path_classes_to_investigate,
            int(args.max_edge_distance),
            int(args.create_total_arrays)
        )