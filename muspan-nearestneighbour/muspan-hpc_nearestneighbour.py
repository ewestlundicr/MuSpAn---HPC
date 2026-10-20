import muspan as ms
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import os
import json
import argparse
from scipy.spatial import cKDTree

def get_classes(path_to_classes):
    df = pd.read_csv(path_to_classes)

    class_A_df = df[df["Class A"].notna()]
    class_A = class_A_df["Class A"].to_list()

    class_B_df = df[df["Class B"].notna()]
    class_B = class_B_df["Class B"].to_list()
    print(f"Class A: {class_A}, Class B: {class_B}")

    return class_A, class_B

def load_domains(directory):
    saved_domains = [d for d in os.listdir(directory) if not d.startswith("._") and d.endswith(".muspan")]

    domains = []

    for s_domain in saved_domains:
        domain = ms.io.load_domain(os.path.join(directory,s_domain))
        domains.append(domain)

    return domains


def get_min_dist(domains, class_A, class_B, domain_label, find_null, output):
    for domain in domains:
        raw_null_dist = {} 
        subtypes_to_index = {}
        for i in range(len(class_B)):
            cur_class_B = class_B[i]

            distances_data = {}

            object_indices_A = ms.query.interpret_query(ms.query.query(domain, ('label', domain_label), 'in', class_A))
            object_indices_B = ms.query.interpret_query(ms.query.query(domain, ('label', domain_label), 'is', [cur_class_B]))

            if len(object_indices_B) == 0:
                print(f"No objects for class {cur_class_B} in domain {domain}")

            try:
                min_dist_A_B,_,nearest_B,centroids_A,centroids_B = ms.query.get_minimum_distances_centroids(domain, object_indices_A, object_indices_B)

                distances_data[domain.name] = min_dist_A_B

                subtypes_to_index[cur_class_B] = object_indices_B
                    
                label_name = class_A[0]+"_to_"+cur_class_B

                domain.add_labels(label_name=label_name, labels=min_dist_A_B, add_labels_to=object_indices_A)
                domain.add_labels(label_name=f"Nearest {cur_class_B}_ID", labels=nearest_B, add_labels_to=object_indices_A)

                if find_null["ind"]:
                    print(f"Finding null distribution for {cur_class_B}")
                    raw_null_dist[f"{domain.name.replace('.csv', '')}_{cur_class_B}"] = list(null_dist(domain, object_indices_A, object_indices_B))
                    print("Null distribution found")

            except:
                continue

        if find_null["all"] or find_null["near"]:
            try:
                ids_1 = ms.query.interpret_query(ms.query.query(domain, ('label', domain_label), 'in', class_A))
                ids_2 = ms.query.interpret_query(ms.query.query(domain, ('label', domain_label), 'in', class_B))

                if find_null["near"]:
                    print("Finding null distribution for nearest Class B")
                    min_dist_A_B,_,nearest_B,_,_ = ms.query.get_minimum_distances_centroids(domain, ids_1, ids_2)
                    nearest_idx, all_classB_subtype_labels = get_subtype_labels(subtypes_to_index, nearest_B, ids_2)
                    null_dist = within_classB_subtype_test(nearest_idx, all_classB_subtype_labels)
                    for s in null_dist:
                        raw_null_dist[domain.name.replace('.csv', '')+f"_nearest_{s}"] = list(null_dist[s])
                    print("Null distribution found")

                if find_null["all"]:
                    print("Finding null distribution for any Class B")
                    raw_null_dist[domain.name.replace('.csv', '')+"_any"] = list(null_dist(domain, ids_1, ids_2))
                    print("Null distribution found")
            except:
                continue

        ms.io.domain_to_csv(domain, path_to_save=output, name_of_file=domain.name)

        if raw_null_dist:
            with open(os.path.join(output, f"raw_null_dist_{domain.name.replace('.csv', '')}.json"), "w") as f:
                json.dump(raw_null_dist, f)

def get_subtype_labels(subtypes_to_index, nearest_classB_idx, all_classB_idx):
    nearest_idx = []
    all_subtype_labels = []

    for cell in all_classB_idx:
        for s in subtypes_to_index:
            if cell in subtypes_to_index[s]:
                all_subtype_labels.append(s)
                if cell in nearest_classB_idx:
                    nearest_idx.append(np.where(all_classB_idx == cell))
                break

    return nearest_idx, all_subtype_labels
                

import numpy as np

def within_classB_subtype_test(nearest_idx, classB_subtype_labels_full, n_perm=999, seed=None):
    """
    nearest_idx: (n_classA,) array — for each classA cell, the row-index into 
                 classB_subtype_labels_full of its nearest classB point. 
                 Computed once, outside this function, and fixed thereafter.
    classB_subtype_labels_full: (n_classB_total,) array — subtype label for 
                 EVERY classB cell in the sample (the full pooled population, 
                 not just the ones that happen to be nearest to something).
    """
    rng = np.random.default_rng(seed)
    subtypes = np.unique(classB_subtype_labels_full)

    # Null: shuffle labels over the FULL pool, then re-look-up via the SAME fixed nearest_idx
    null_props = {s: np.empty(n_perm) for s in subtypes}
    for i in range(n_perm):
        shuffled_labels = rng.permutation(classB_subtype_labels_full)  # preserves true counts
        perm_subtypes = shuffled_labels[nearest_idx]                    # same fixed indices
        for s in subtypes:
            null_props[s][i] = np.mean(perm_subtypes == s)
    
    return null_props

def null_dist(domain, ids_1, ids_2, n_perm=999, seed=None):
    """
    Standardized effect size for minimum centroid distance between two 
    cell populations, controlling for density via random labelling.
    
    ids_1, ids_2: object IDs (or query results) for the two cell types,
                  drawn from the SAME domain/sample.
    """
    rng = np.random.default_rng(seed)

    # Pool the two populations -- this is the key step.
    # By only shuffling labels over the SAME fixed set of points,
    # density/intensity is held constant automatically.
    pooled_ids = np.concatenate([ids_1, ids_2])
    n1 = len(ids_1)

    null_stats = np.empty(n_perm)
    for i in range(n_perm):
        shuffled = rng.permutation(pooled_ids)
        perm_ids_1, perm_ids_2 = shuffled[:n1], shuffled[n1:]
        perm_dist, *_ = ms.query.get_minimum_distances_centroids(domain, perm_ids_1, perm_ids_2)
        null_stats[i] = np.mean(perm_dist)

    return null_stats

def main(input, output, path_to_classes_csv, domain_label, null_dist):
    class_A, class_B = get_classes(path_to_classes_csv)

    domains = load_domains(input)

    null_dist_measurements = {'ind': null_dist[0], 'near': null_dist[1], 'all': null_dist[2]}
    
    if not os.path.exists(output):
        os.mkdir(output)

    get_min_dist(domains, class_A, class_B, domain_label, null_dist_measurements, output)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Muspan neighbourhood analysis")
    parser.add_argument("--inputs", required=True, help="Directory containing muspan domains")
    parser.add_argument("--output", required=True, help="Output directory for saving csv")
    parser.add_argument("--domain_label", required=False, help="Name of label of interest in domain", default="Phenotype")
    parser.add_argument("--null_dist", required=False, help="What null distance measures to include", default=[0,0,0])


    args = parser.parse_args()
    main(args.inputs, args.output, args.classes_csv, args.domain_label, args.null_dist)