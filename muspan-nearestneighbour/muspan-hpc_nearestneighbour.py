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

    return class_A, class_B

def load_domains(directory):
    saved_domains = [d for d in os.listdir(directory) if not d.startswith("._") and d.endswith(".muspan")]

    domains = []

    for s_domain in saved_domains:
        domain = ms.io.load_domain(os.path.join(directory,s_domain))
        domains.append(domain)

    return domains


def get_min_dist(domains, class_A, class_B, output):
    for domain in domains[1:]:
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

            except:
                continue

        ms.io.domain_to_csv(domain, path_to_save=output, name_of_file=domain.name)


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