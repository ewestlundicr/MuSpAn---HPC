# How to run run_proximity_array.sbatch 
`run_proximity_array.sbatch` runs in parallel the proximity script on all domains specified in `domain_list`.
Note the following line specifying the domain ids (from 0 to 139) and the number of maximum jobs to launch at once (e.g., 40)

```bash
#SBATCH --array=0-139%40
```

First, create a text file with the list `absolute paths` to the domains
```bash
find /path/to/domains -maxdepth 1 -type f | sort > domain_list.txt
```
Example `domain_list.txt` file:
```
path/domainA
path/domainB
path/domainC
```

## To get the number of domain listed in the `.txt` file:
```bash
wc -l domain_list.txt
```

#
