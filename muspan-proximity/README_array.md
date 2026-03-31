# Entry point is `submit_all.sh`
`submit_all.sh` runs the proxmitty analysis script (defined in `run_proximity_array.sbatch`), waits for it to finish for all domains and then launches the `run_proximity_merge.sbatch` script on the resulting domain arrays.

To run the analysis:
```bash
./submit_all.sh \ 
  --input_dir /data/domains \  
  --output_dir /data/output \ 
  --classes /data/classes \ 
  --domain_list domain_list.txt \ 
  --max_edge_distance 20
```

## About `run_proximity_array.sbatch` 

`run_proximity_array.sbatch` runs in parallel the proximity script on all domains specified in `domain_list`.
Note that it doesnt run the merge step. 

Note the following line specifying the domain ids (from 0 to 139) and the number of maximum jobs to launch at once (e.g., 40)

```bash
#SBATCH --array=0-139%40
```

## Preparing the domain list file to pass as argument
First, create a text file with the list `absolute paths` to the domains
```bash
find /path/to/domains -maxdepth 1 -type f | sort > domain_list.txt
```
Example `domain_list.txt` file:
```
/absolute/path/domainA
/absolute/path/domainB
/absolute/path/domainC
```
#### To get the number of domain listed in the `.txt` file:
```bash
wc -l domain_list.txt
```

### How to run `run_proximity_array.sbatch`
```bash
sbatch run_proximity_array.sbatch input_dir output_dir classes_file domain_list_file max_edge_distance_int
```

## About `run_proximity_merge.sbatch`

### How to run `run_proximity_merge.sbatch`
```bash
sbatch run_proximity_merge.sbatch output_dir
```
