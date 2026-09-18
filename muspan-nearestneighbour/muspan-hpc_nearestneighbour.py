import muspan as ms
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import os
import json
import argparse

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


def get_min_dist(domains, class_A, class_B, output):
    for domain in domains:
        raw_null_dist = {} 
        for i in range(len(class_B)):
            cur_class_B = class_B[i]

            distances_data = {}

            object_indices_A = ms.query.interpret_query(ms.query.query(domain, ('label', 'Phenotype'), 'in', class_A))
            object_indices_B = ms.query.interpret_query(ms.query.query(domain, ('label', 'Phenotype'), 'is', [cur_class_B]))

            try:
                min_dist_A_B,_,nearest_B,_,_ = ms.query.get_minimum_distances_centroids(domain, object_indices_A, object_indices_B)

                distances_data[domain.name] = min_dist_A_B
                    
                label_name = class_A[0]+"_to_"+cur_class_B

                domain.add_labels(label_name=label_name, labels=min_dist_A_B, add_labels_to=object_indices_A)
                domain.add_labels(label_name=f"Nearest {cur_class_B}_ID", labels=nearest_B, add_labels_to=object_indices_A)

                print(f"Finding null distribution for {cur_class_B}")
                raw_null_dist[f"{domain.name.replace('.csv', '')}_{cur_class_B}"] = list(null_dist(domain, object_indices_A, object_indices_B))
                print("Null distribution found")


            except:
                continue

        try:
            print("Finding null distribution for any CAF")
            ids_1 = ms.query.interpret_query(ms.query.query(domain, ('label', 'Phenotype'), 'in', class_A))
            ids_2 = ms.query.interpret_query(ms.query.query(domain, ('label', 'Phenotype'), 'in', class_B))
            raw_null_dist[domain.name+"_anyCAF"] = list(null_dist(domain, ids_1, ids_2))
            print("Null distribution found")
        except:
            continue


        ms.io.domain_to_csv(domain, path_to_save=output, name_of_file=domain.name)
        with open(os.path.join(output, f"raw_null_dist_{domain.name.replace('.csv', '')}.json"), "w") as f:
            json.dump(raw_null_dist, f)

    

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

def main(input, output, path_to_classes_csv):
    class_A, class_B = get_classes(path_to_classes_csv)

    domains = load_domains(input)

    if not os.path.exists(output):
        os.mkdir(output)
    get_min_dist(domains, class_A, class_B, output)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Muspan neighbourhood analysis")
    parser.add_argument("--inputs", required=True, help="Directory containing muspan domains")
    parser.add_argument("--output", required=True, help="Output directory for saving csv")
    parser.add_argument("--classes_csv", required=True, help="Path to csv with Class A and Class B")


    args = parser.parse_args()
    main(args.inputs, args.output, args.classes_csv)